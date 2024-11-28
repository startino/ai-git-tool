from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.lib.internal_expertise.custom_embedding_function import (
    HuggingFaceEmbeddingsWrapper,
)
from src.interfaces import db

from src.lib.internal_expertise.document_loader import DocumentLoader
from src.routers import router
from src.routers.threads import router as threads
from src.routers.chromadb import router as chromadb_router
from src.lib.internal_expertise.chroma_helper import chroma_client
from src.utils.logging import setup_logging

load_dotenv()
setup_logging()

# from src.interfaces.supabase import create_tables

# create_tables()

embedding_function = HuggingFaceEmbeddingsWrapper()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        supabase_client = db.client()

        logging.info(f"CHROMA CLIENT:\t\t {chroma_client.heartbeat()}")

        collection = chroma_client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_function,
        )  # type: ignore

        # Get all document IDs from Supabase buckets
        documents_from_bucket = supabase_client.storage.from_("documents").list()

        documents_from_db = (
            supabase_client.table("documents").select("*").execute().data
        )

        if len(documents_from_bucket) == 0:
            logging.info("No documents found in Supabase buckets")
            yield

        # Get all documents from Chroma
        chroma_chunks = collection.get()

        chunks_document_ids = []
        chroma_chunks_metadatas = chroma_chunks.get("metadatas", None)
        if chroma_chunks_metadatas is not None:
            chunks_document_ids = [
                metadata["document_id"]
                for metadata in chroma_chunks_metadatas
                if "document_id" in metadata
            ]

        # Compare the two sets and add any missing documents to Chroma
        for document in documents_from_db:
            if document["id"] not in chunks_document_ids:
                loader = DocumentLoader()
                chunks = loader.load_file(
                    file_path=document["file"], supabase_client=supabase_client
                ).create_chunks()
                if chunks is None:
                    logging.error(f"No chunks found for document {document['id']}")
                    continue

                logging.info(f"Adding document {document['id']} to Chroma")
                collection.add(
                    documents=chunks,
                    metadatas=[
                        {"id": str(i), "document_id": document["id"]}
                        for i in range(len(chunks))
                    ],
                    ids=[str(i) + document["id"] for i in range(len(chunks))],
                )
                # Log the collection details
                logging.info(
                    f"Added doc {document['id']}. Collection '{collection.name}' details:"
                )
                logging.info(f"Number of documents: {collection.count()}")

    except Exception as e:
        logging.error(f"Error syncing Chroma with Supabase: {str(e)}")

    yield


def create_app() -> FastAPI:
    # app = FastAPI(lifespan=lifespan)
    app = FastAPI()

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(end_time)
        return response

    app.include_router(router)
    app.include_router(threads)
    app.include_router(chromadb_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
