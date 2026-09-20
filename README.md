# Chat-with-Your-Documents (React Frontend & FastAPI Backend)

An AI-powered document chatbot that lets you chat with your own PDF documents, featuring a modern React.js frontend and a robust FastAPI backend.

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-Frontend-blue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-blue)](https://fastapi.tiangolo.com/)

## Overview

This project provides a local solution for interacting with PDF documents using natural language. It combines a React.js frontend for a user-friendly experience with a FastAPI backend for efficient document processing and question answering using Retrieval-Augmented Generation (RAG).

**App Showcase:**

![Chat-with-Your-Documents Screenshot](images/app.png)

*See the application in action!*

## Key Features

*   **Modern React.js Frontend:** A clean and responsive user interface.
*   **FastAPI Backend:** Handles document processing and question answering efficiently.
*   **Retrieval-Augmented Generation (RAG):** Provides accurate and context-aware answers by grounding the responses in your uploaded document.
*   **Local Document Q&A:** Ask questions and get answers based on your PDF documents, all running locally.
*   **Persistent Vector Store:** Uses a lightweight JSON vector store with Gemini-generated document embeddings.
*   **Gemini Integration:** Uses the Gemini API for language generation. The chatbot requires a valid Gemini API key.

## Technology Stack

*   **Frontend:**
    *   [React.js](https://reactjs.org/)
    *   [styled-components](https://styled-components.com/)
    *   [axios](https://axios-http.com/)
    *   [react-dropzone](https://react-dropzone.js.org/)
*   **Backend:**
    *   [FastAPI](https://fastapi.tiangolo.com/)
    *   [Google Gemini API](https://ai.google.dev/gemini-api/docs)
    *   [Google Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
    *   [Python](https://www.python.org/) 3.10+

## Prerequisites

*   [Node.js](https://nodejs.org/) and npm (Node Package Manager)
*   Python 3.10 or higher
*   A [Gemini API key](https://aistudio.google.com/app/apikey) (required for the chatbot to respond)

## Setup and Installation

**1. Clone the repository:**

```bash
git clone https://github.com/devcom33/Chat-with-Your-Documents.git
cd Chat-with-Your-Documents
```

**2. Configure the Gemini API key:**

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

**3. Install the backend dependency:**

```bash
python -m pip install google-genai
```
 # Chat with Your Documents

 An AI document chatbot that lets you upload a PDF and ask questions about its contents. The project uses a React frontend, a FastAPI backend, and Google Gemini for text generation and embeddings.

 ## Features

 - Upload text-based PDF documents.
 - Process large PDFs asynchronously so the upload request returns quickly.
 - Extract PDF text page by page.
 - Generate document and query embeddings with Gemini.
 - Retrieve the most relevant document chunks with cosine similarity.
 - Ask questions grounded only in the uploaded document.
 - Replace the active document when a new PDF is uploaded.
 - Run locally or deploy the frontend and backend separately on Render.

 ## Architecture

 ```text
 React + Vite frontend
                 |
                 | POST /upload/
                 | GET  /upload-status/{job_id}
                 | POST /query/
                 v
 FastAPI backend
                 |
                 +-- pypdf extracts PDF text
                 +-- Gemini Embeddings creates vectors
                 +-- vector_store.json stores chunks and vectors
                 +-- Gemini generates grounded answers
 ```

 The backend stores the active document's chunks and embeddings in `vector_store.json`. A new successful upload replaces the previous document.

 ## Technology Stack

 ### Frontend

 - React 19
 - Vite
 - Axios
 - styled-components
 - react-dropzone

 ### Backend

 - Python 3.10 or newer recommended
 - FastAPI
 - Uvicorn
 - pypdf
 - Google Gemini API
 - Google Gemini Embeddings

 ## Requirements

 Install the following before running the project:

 - Python 3.10 or newer
 - Node.js and npm
 - A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

 ## Project Structure

 ```text
 .
 ├── backend_chatdoc.py       # FastAPI application
 ├── requirements.txt         # Backend dependencies
 ├── .env                     # Local secrets; do not commit
 ├── uploaded_documents/      # Uploaded PDFs; generated locally
 ├── vector_store.json        # Generated embeddings; ignored by Git
 ├── images/                  # Project images
 └── front-chatdoc/
         ├── package.json
         ├── src/
         │   ├── App.jsx
         │   └── components/
         │       ├── ChatInterface.jsx
         │       └── FileUpload.jsx
         └── vite.config.js
 ```

 ## Configuration

 Create a `.env` file in the project root. Never commit this file or share the API key.

 ```env
 GEMINI_API_KEY=your_gemini_api_key
 GEMINI_MODEL=gemini-3.6-flash
 GEMINI_EMBEDDING_MODEL=gemini-embedding-001
 FRONTEND_URL=http://localhost:5173
 ```

 `GEMINI_MODEL` can be changed to another Gemini model available to your API account. If a model is unavailable, Gemini returns a model-not-found error.

 ## Local Setup

 ### 1. Clone the repository

 ```bash
 git clone https://github.com/roshan-coder02/Chat-With-Document.git
 cd Chat-With-Document
 ```

 If you are working from an existing checkout, open the project directory instead.

 ### 2. Create and activate a Python environment

 macOS/Linux:

 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```

 Windows PowerShell:

 ```powershell
 py -m venv .venv
 .venv\Scripts\Activate.ps1
 ```

 ### 3. Install backend dependencies

 ```bash
 python -m pip install -r requirements.txt
 ```

 ### 4. Start the backend

 From the project root:

 ```bash
 python backend_chatdoc.py
 ```

 The API runs at `http://localhost:8000`.

 You can also start it with Uvicorn:

 ```bash
 uvicorn backend_chatdoc:app --host 0.0.0.0 --port 8000
 ```

 ### 5. Install and start the frontend

 Open a second terminal:

 ```bash
 cd front-chatdoc
 npm install
 npm run dev
 ```

 Open the URL shown by Vite, normally `http://localhost:5173`.

 The frontend uses this API URL by default:

 ```text
 http://localhost:8000
 ```

 To override it locally, create `front-chatdoc/.env.local`:

 ```env
 VITE_API_URL=http://localhost:8000
 ```

 Restart Vite after changing frontend environment variables.

 ## Using the Application

 1. Start the backend and frontend in separate terminals.
 2. Open the frontend URL.
 3. Select or drop a text-based PDF.
 4. Wait until processing finishes and the filename appears.
 5. Ask a question about the uploaded document.

 Large PDFs may take time because their text is extracted and sent to Gemini in embedding batches. Do not close or refresh the page while it displays `Processing PDF...`.

 Only one document is active at a time. Uploading another PDF replaces the previous document's searchable content.

 Scanned or image-only PDFs are not supported by the current text extractor. Run OCR on those PDFs before uploading them.

 ## API Endpoints

 ### Upload a PDF

 ```http
 POST /upload/
 Content-Type: multipart/form-data
 ```

 Example:

 ```bash
 curl -X POST http://localhost:8000/upload/ \
     -F "file=@document.pdf"
 ```

 The response contains a processing job ID:

 ```json
 {
     "job_id": "...",
     "filename": "document.pdf",
     "status": "processing"
 }
 ```

 ### Check upload status

 ```http
 GET /upload-status/{job_id}
 ```

 Processing response:

 ```json
 {
     "status": "processing",
     "filename": "document.pdf"
 }
 ```

 Completed response:

 ```json
 {
     "status": "completed",
     "filename": "document.pdf"
 }
 ```

 ### Ask a question

 ```http
 POST /query/
 Content-Type: application/json
 ```

 Example:

 ```bash
 curl -X POST http://localhost:8000/query/ \
     -H "Content-Type: application/json" \
     -d '{"question":"What is this document about?"}'
 ```

 Example response:

 ```json
 {
     "answer": "...",
     "sources": ["document.pdf"]
 }
 ```

 The backend returns `Please upload a document first.` when no document has been successfully processed.

 ## Frontend Commands

 Run these commands from `front-chatdoc/`:

 ```bash
 npm run dev       # Start the development server
 npm run build     # Create a production build
 npm run preview   # Preview the production build locally
 npm run lint      # Run ESLint
 ```

 ## Deploying the Backend to Render

 Create a Render **Web Service** connected to the GitHub repository.

 Use these settings:

 ```text
 Root Directory: leave blank
 Runtime: Python
 Build Command: pip install -r requirements.txt
 Start Command: uvicorn backend_chatdoc:app --host 0.0.0.0 --port $PORT
 ```

 Add these environment variables in Render:

 ```text
 GEMINI_API_KEY=your_gemini_api_key
 GEMINI_MODEL=gemini-3.6-flash
 GEMINI_EMBEDDING_MODEL=gemini-embedding-001
 FRONTEND_URL=https://your-frontend-name.onrender.com
 ```

 Deploy the backend and copy its Render URL, for example:

 ```text
 https://your-backend-name.onrender.com
 ```

 You can verify the service is reachable by opening:

 ```text
 https://your-backend-name.onrender.com/docs
 ```

 ## Deploying the Frontend to Render

 Create a Render **Static Site** using the same GitHub repository.

 Use these settings:

 ```text
 Root Directory: front-chatdoc
 Build Command: npm install && npm run build
 Publish Directory: dist
 ```

 Add this environment variable:

 ```text
 VITE_API_URL=https://your-backend-name.onrender.com
 ```

 Deploy the frontend. Then make sure the backend's `FRONTEND_URL` exactly matches the deployed frontend URL and redeploy the backend if necessary.

 Frontend environment variables are applied during the build, so a frontend redeploy is required after changing `VITE_API_URL`.

 ## Render Storage Limitations

 The current backend writes uploaded PDFs and `vector_store.json` to the local filesystem. Render free web services have ephemeral filesystems, so these files can disappear after a restart or redeploy.

 For production persistence, replace the local JSON store and upload directory with one of these options:

 - Render persistent disks
 - Object storage such as Amazon S3 or Cloud Storage
 - A managed vector database
 - A database with vector search support

 The current implementation is suitable for demonstrations and small deployments where re-uploading the PDF after a restart is acceptable.

 ## Large PDF Notes

 - Upload processing runs as a FastAPI background task.
 - PDF text is extracted page by page.
 - Gemini embedding requests are sent in batches of 20 chunks.
 - Text chunks are currently 1,000 characters each.
 - The complete JSON vector store is loaded into memory for similarity search.
 - Very large documents can still exceed Render's memory limit because the embeddings and chunks are kept in memory.

 For very large or production documents, use a managed vector database rather than the local JSON store.

 ## Troubleshooting

 ### `vite: command not found`

 Install frontend dependencies from the frontend directory:

 ```bash
 cd front-chatdoc
 npm install
 npm run dev
 ```

 ### `GEMINI_API_KEY is missing`

 Create `.env` in the project root locally, or add `GEMINI_API_KEY` under the Render service's environment variables.

 ### `API key not valid`

 Create a new key in [Google AI Studio](https://aistudio.google.com/app/apikey). Revoke any key that has been exposed in terminal logs, screenshots, commits, or chat messages.

 ### `Please upload a document first`

 The PDF was not successfully indexed. Check the upload error in the frontend and the backend Render logs. Upload processing must reach the `completed` status before querying.

 ### `The PDF contains no extractable text`

 The PDF is likely scanned or image-only. Run OCR first, then upload the OCR-enabled PDF.

 ### `503 Gemini is temporarily busy`

 Gemini is temporarily unavailable or rate-limited. Wait and retry. Check your Gemini API quota and model availability.

 ### CORS errors

 Set the backend environment variable to the exact frontend origin:

 ```text
 FRONTEND_URL=https://your-frontend-name.onrender.com
 ```

 Do not add a trailing slash. Redeploy the backend after changing it.

 ### Render reports no open port

 Use the Render start command exactly as follows:

 ```bash
 uvicorn backend_chatdoc:app --host 0.0.0.0 --port $PORT
 ```

 ### Render runs out of memory

 Use smaller PDFs, reduce the number of chunks, upgrade the Render instance, or move retrieval to an external vector database. The backend no longer installs local Transformer models, but the JSON vector store still grows with the document and embeddings.

 ## Security

 - Never commit `.env`.
 - Never expose `GEMINI_API_KEY` in frontend code.
 - Revoke and replace keys that appear in logs or screenshots.
 - Keep uploaded documents private and avoid committing them.
 - Validate production CORS origins instead of allowing all origins.

 ## License

 This project is released under the MIT License. See the repository for license details.