Document Search and Q&A System
This repository contains a FastAPI-based application that allows users to upload documents (PDF, JSON, or text files) and ask questions based on the content of those documents. The system uses FAISS for document indexing and retrieval, and OpenAI's API for generating answers.

Features
Document Upload: Users can upload documents in PDF, JSON, or text format.
Document Indexing: Uploaded documents are stored and indexed using FAISS, enabling efficient retrieval.
Question Answering: Users can ask questions, and the system retrieves the most relevant document and generates an answer using OpenAI's API.
Web Interface: A simple HTML interface for uploading documents and asking questions.