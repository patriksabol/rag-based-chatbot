# Document Search API with OpenAI and FAISS

This FastAPI-based service allows users to upload documents (PDF, JSON, or text) and ask questions based on the content of these documents using an OpenAI-powered chatbot.

## Features

- **Document Upload**: Upload and store documents in a FAISS-based index for quick retrieval.
- **Question Answering**: Ask questions about the content of the uploaded documents and get responses powered by OpenAI's GPT model.

## Prerequisites

Before you begin, ensure you have the following installed:

- Docker
- Docker Compose (optional, if you want to run with Docker Compose)
- OpenAI API Key

## Environment Variables

Create a `.env` file in the root directory of your project with the following content:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Building and Running the Service

### 1. Clone the Repository

```bash
git clone https://github.com/patriksabol/rag-based-chatbot.git
cd document-search-api
```

### 2. Build the Docker Image

You can build the Docker image using the provided `Dockerfile`. Run the following command:

```bash
docker build -t document-search-api .
```

### 3. Run the Service

Once the Docker image is built, you can run the service using Docker:

```bash
docker run -d -p 8080:80 --env-file .env document-search-api
```

This command runs the service in detached mode and maps port `80` on your local machine to port `80` in the container.

### 4. Access the Service

You can now access the service in your web browser by navigating to:

```
http://localhost:8080
```

### 5. Upload a Document

1. On the homepage, click "Choose File" and select a PDF document.
2. Click "Upload" to store the document in the FAISS index.

### 6. Ask a Question

1. Enter your question in the text area under "Ask a Question".
2. Click "Ask" to submit your query. The service will retrieve the most relevant document and generate a response using OpenAI's API.
the service, as well as additional information for development and deployment. Make sure to update the repository URL in the "Clone the Repository" section with your actual repository URL.