from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever, TextConverter, JsonConverter, PDFToTextConverter
from haystack.pipelines import DocumentSearchPipeline
import openai
import os
from fastapi.responses import HTMLResponse

# Retrieve OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Paths for FAISS index and config files
faiss_index_path = "faiss_db"
sql_url = "sqlite:///faiss_document_store.db"

# Global variables for the document store and retriever
document_store = None
retriever = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global document_store, retriever

    # Startup: Load or create the FAISS index
    if os.path.exists(faiss_index_path):
        document_store = FAISSDocumentStore.load(index_path=faiss_index_path)
    else:
        document_store = FAISSDocumentStore(sql_url=sql_url, embedding_dim=1536)
        retriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model="text-embedding-ada-002",
            model_format="openai",
            use_gpu=False,
            api_key=openai_api_key,
            max_seq_len=1024
        )
        # Update embeddings and save the FAISS index
        document_store.update_embeddings(retriever)
        document_store.save(faiss_index_path)

    # Initialize the retriever
    retriever = EmbeddingRetriever(
        document_store=document_store,
        embedding_model="text-embedding-ada-002",
        api_key=openai_api_key
    )

    try:
        yield
    finally:
        # Shutdown: Save the FAISS index explicitly
        if document_store:
            document_store.save(faiss_index_path)
            print("FAISS index saved during shutdown")


# Initialize the FastAPI app with a custom lifespan manager
app = FastAPI(lifespan=lifespan)

# Load converters for different file types
pdf_converter = PDFToTextConverter()
text_converter = TextConverter()
json_converter = JsonConverter()


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), file_type: str = Form(...)):
    # Convert the uploaded file based on its type
    if file_type == "text":
        docs = text_converter.convert(file_path=file.filename)
    elif file_type == "json":
        docs = json_converter.convert(file_path=file.filename)
    elif file_type == "pdf":
        docs = pdf_converter.convert(file_path=file.filename)
    else:
        return {"error": "Unsupported file type"}

    # Store the converted document and update embeddings
    document_store.write_documents(docs)
    document_store.update_embeddings(retriever)
    document_store.save(faiss_index_path)  # Save the index after updating

    return {"status": "Document processed and stored"}


@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Search</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <h1>Upload a PDF Document</h1>
    <form id="upload-form" enctype="multipart/form-data">
        <input type="file" id="file" name="file" accept=".pdf"><br><br>
        <input type="hidden" name="file_type" value="pdf">
        <input type="button" value="Upload" onclick="uploadFile()">
    </form>
    <div id="upload-status"></div>

    <h1>Ask a Question</h1>
    <form id="ask-form">
        <textarea id="query" name="query" placeholder="Ask your question" rows="4" cols="50"></textarea><br><br>
        <input type="button" value="Ask" onclick="askQuestion()">
    </form>
    <div id="answer"></div>
    <div id="error-message" style="color:red;"></div>

    <script>
        async function uploadFile() {
            const formData = new FormData();
            const fileField = document.querySelector("#file");

            // Show uploading message
            document.getElementById("upload-status").innerText = "Uploading file...";

            formData.append("file", fileField.files[0]);
            formData.append("file_type", "pdf");

            try {
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();
                document.getElementById("upload-status").innerText = result.status;
            } catch (error) {
                document.getElementById("upload-status").innerText = "Error uploading file: " + error.message;
            }
        }

        async function askQuestion() {
            const query = document.querySelector("#query").value;

            // Show generating answer message
            document.getElementById("answer").innerHTML = "";
            document.getElementById("error-message").innerText = "";
            document.getElementById("answer").innerText = "Generating answer...";

            try {
                const response = await fetch(`/ask?query=${encodeURIComponent(query)}`);

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }

                const result = await response.text();

                if (result.trim()) {
                    const html = marked.parse(result);
                    document.getElementById("answer").innerHTML = html;
                } else {
                    document.getElementById("answer").innerText = "";
                    document.getElementById("error-message").innerText = "No response received. Please try again.";
                }
            } catch (error) {
                document.getElementById("answer").innerText = "";
                document.getElementById("error-message").innerText = "Error asking question: " + error.message;
            }
        }
    </script>
</body>
</html>
    """



@app.get("/ask")
async def ask_question(query: str):
    # Create a pipeline to search the documents
    pipeline = DocumentSearchPipeline(retriever)
    result = pipeline.run(query=query)

    # If no documents are found, return a message
    if not result['documents']:
        return "No relevant documents found."

    # Prepare a prompt for the OpenAI API based on the retrieved document
    prompt = f"Based on the following document, answer the question: {query}\n\nDocument:\n{result['documents'][0].content}"

    # Query OpenAI's API to generate an answer
    answer = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the generated answer
    return answer.choices[0].message['content']
