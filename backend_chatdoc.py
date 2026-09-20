from fastapi import BackgroundTasks, FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from pypdf import PdfReader
import os
import json
import math
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
import shutil  # For saving uploaded files
from typing import Dict, List  # Import List for type hinting
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from the .env file")
client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

#FastAPI
app = FastAPI()

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


# Constants
VECTOR_STORE_PATH = "vector_store.json"
UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def embed_documents(texts: List[str], task_type: str) -> List[List[float]]:
    if not texts:
        return []
    embeddings = []
    for start in range(0, len(texts), 20):
        response = client.models.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            contents=texts[start:start + 20],
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=768,
            ),
        )
        embeddings.extend(embedding.values for embedding in response.embeddings)
    return embeddings


def embed_query(text: str) -> List[float]:
    return embed_documents([text], "RETRIEVAL_QUERY")[0]


vector_store: List[dict] = []
upload_jobs: Dict[str, dict] = {}


def save_vector_store() -> None:
    with open(VECTOR_STORE_PATH, "w", encoding="utf-8") as store_file:
        json.dump(vector_store, store_file)


def load_vector_store() -> None:
    global vector_store
    try:
        with open(VECTOR_STORE_PATH, encoding="utf-8") as store_file:
            vector_store = json.load(store_file)
        print("Vector store loaded successfully from disk.")
    except (FileNotFoundError, json.JSONDecodeError):
        vector_store = []
        print("No vector store found. A new one will be created after the first upload.")


def cosine_similarity(first: List[float], second: List[float]) -> float:
    numerator = sum(left * right for left, right in zip(first, second))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    if not first_norm or not second_norm:
        return 0.0
    return numerator / (first_norm * second_norm)


def find_relevant_documents(question: str, limit: int = 2) -> List[dict]:
    question_embedding = embed_query(question)
    ranked_documents = sorted(
        vector_store,
        key=lambda document: cosine_similarity(question_embedding, document["embedding"]),
        reverse=True,
    )
    return ranked_documents[:limit]


load_vector_store()


def query(question: str):
    if not vector_store:
        return {"answer": "Please upload a document first."}

    relevant_docs = find_relevant_documents(question)
    print(f"len(relevant_docs): {len(relevant_docs)}")
    context = "\n".join(document["text"] for document in relevant_docs)

    prompt = (
        "Answer the question using only the provided document context. "
        "If the context does not contain the answer, say 'I need more context.'\n\n"
        f"Question: {question}\nContext: {context}"
    )
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an AI assistant. Answer based on the provided context only. "
                    "Do not use outside information."
                )
            ),
        )
    except errors.ServerError as error:
        raise HTTPException(
            status_code=503,
            detail="Gemini is temporarily busy. Please try again in a moment.",
        ) from error
    except errors.ClientError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini request failed: {error.message}",
        ) from error

    return {
        "answer": response.text,
        "sources": [document["source"] for document in relevant_docs],
    }


def split_text(text: str, chunk_size: int = 1000) -> List[str]:
    return [
        text[start:start + chunk_size].strip()
        for start in range(0, len(text), chunk_size)
        if text[start:start + chunk_size].strip()
    ]


def process_document(file_path: str):
    """Yield text chunks page by page to keep large PDFs out of memory."""
    try:
        reader = PdfReader(file_path)
        found_text = False
        for page in reader.pages:
            page_text = page.extract_text() or ""
            for text_chunk in split_text(page_text):
                found_text = True
                yield text_chunk
        if not found_text:
            raise HTTPException(
                status_code=400,
                detail="The PDF contains no extractable text. Upload a text-based PDF or run OCR first.",
            )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error processing PDF document: {error}") from error


def process_upload_job(job_id: str, file_path: str, safe_filename: str) -> None:
    global vector_store
    try:
        new_vector_store = []
        pending_texts = []
        for text in process_document(file_path):
            pending_texts.append(text)
            if len(pending_texts) == 20:
                document_embeddings = embed_documents(pending_texts, "RETRIEVAL_DOCUMENT")
                new_vector_store.extend(
                    {"text": chunk, "embedding": embedding, "source": safe_filename}
                    for chunk, embedding in zip(pending_texts, document_embeddings)
                )
                pending_texts.clear()

        if pending_texts:
            document_embeddings = embed_documents(pending_texts, "RETRIEVAL_DOCUMENT")
            new_vector_store.extend(
                {"text": chunk, "embedding": embedding, "source": safe_filename}
                for chunk, embedding in zip(pending_texts, document_embeddings)
            )

        vector_store = new_vector_store
        save_vector_store()
        upload_jobs[job_id] = {"status": "completed", "filename": safe_filename}
    except errors.ServerError:
        upload_jobs[job_id] = {
            "status": "failed",
            "error": "Gemini is temporarily busy while processing the PDF. Please try again.",
        }
    except errors.ClientError as error:
        upload_jobs[job_id] = {"status": "failed", "error": f"Gemini embedding failed: {error.message}"}
    except HTTPException as error:
        upload_jobs[job_id] = {"status": "failed", "error": error.detail}
    except Exception as error:
        print(f"Upload processing error: {error}")
        upload_jobs[job_id] = {"status": "failed", "error": str(error)}


@app.post("/upload/")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        safe_filename = Path(file.filename).name
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        with open(file_path, "wb") as output_file:
            shutil.copyfileobj(file.file, output_file)

        job_id = str(uuid4())
        upload_jobs[job_id] = {"status": "processing", "filename": safe_filename}
        background_tasks.add_task(process_upload_job, job_id, file_path, safe_filename)
        return {"job_id": job_id, "filename": safe_filename, "status": "processing"}
    except HTTPException:
        raise
    except Exception as error:
        print(f"Upload error: {error}")
        raise HTTPException(status_code=500, detail=str(error)) from error
    finally:
        file.file.close()


@app.get("/upload-status/{job_id}")
async def upload_status(job_id: str):
    job = upload_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Upload job not found.")
    return job


@app.post("/query/")
async def ask_question(request: QueryRequest):
    return query(request.question)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
