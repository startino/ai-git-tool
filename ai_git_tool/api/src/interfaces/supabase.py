import os, logging
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv, find_dotenv
from src.utils.error_handler import handle_error
from src.models.db import (
    Agent,
    Agent_Threads,
    Document,
    Eca,
    Event,
    Observation,
    Profiles,
    Prompt,
    PromptCollection,
    Scenerio,
    Thread,
)


_: bool = load_dotenv(find_dotenv())

engine = create_engine(url=str(os.getenv("PG_DB_URL")), echo=True)


@handle_error
def create_tables():
    logging.info(f"Creating tables with connection: {os.getenv('PG_DB_URL')}")

    tables = SQLModel.metadata.tables
    print(f"Tables to be created: {', '.join(tables.keys())}")

    SQLModel.metadata.create_all(engine)
    logging.info("Tables created successfully")


def get_session():
    with Session(engine) as session:
        yield session
