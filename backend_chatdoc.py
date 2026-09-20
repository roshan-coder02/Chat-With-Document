from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import shutil  # For saving uploaded files
from pathlib import Path  # For safer path handling
from typing import List  # Import List for type hinting
from langchain_community.document_loaders import PyPDFLoader
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from the .env file")
client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

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
# Constants
VECTOR_STORE_PATH = "faiss_vector_store"
UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

vector_store = None
def load_vector_store():
    global vector_store
    try:
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        print("Vector store loaded successfully from disk.")
    except Exception as e:
        print(f"Error loading vector store from disk: {e}. Creating a new one.")
        vector_store = FAISS.from_texts(["Initial empty document."], embedding=embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)

load_vector_store()  # Load on application startup

class QueryRequest(BaseModel):
    question: str

def query(question: str):
    global vector_store
    if vector_store is None:
        return {"answer": "Vector store is not initialized. Please upload a document."}

    relevant_docs = vector_store.similarity_search(question, k=2)
    print(f"len(relevant_docs): {len(relevant_docs)}")
    print(f"relevant_docs: {relevant_docs}")
    context = "\n".join([doc.page_content for doc in relevant_docs])

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
        "sources": [doc.metadata.get("source", "Unknown") for doc in relevant_docs],
    }


def process_document(file_path: str) -> List[str]:
    """Loads and processes a PDF document, returning texts."""
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        extracted_texts = [text.page_content.strip() for text in texts if text.page_content.strip()]
        if not extracted_texts:
            raise HTTPException(
                status_code=400,
                detail="The PDF contains no extractable text. Upload a text-based PDF or run OCR first.",
            )
        return extracted_texts

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error processing PDF document: {e}")

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    global vector_store  # Access the global variable

    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        texts = process_document(file_path)

        new_vector_store = FAISS.from_texts(texts, embedding=embeddings)
        if vector_store is None:
            vector_store = new_vector_store
        else:
            vector_store.merge_from(new_vector_store) # Fixed merging
        vector_store.save_local(VECTOR_STORE_PATH) # Save updated store
        
        if hasattr(vector_store, 'index') and hasattr(vector_store.index, 'ntotal'):
            index_size = vector_store.index.ntotal
            print(f"FAISS index Size: {index_size}")
        else:
            print("Could not determine FAISS index size.")

        return {"filename": file.filename, "message": "PDF document uploaded and processed successfully."}

    except Exception as e:
        print(f"Upload error: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) # Return error as HTTPException
    finally:
        file.file.close()  # Ensure file is closed



@app.post("/query/")
async def ask_question(request: QueryRequest):
    return query(request.question)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
