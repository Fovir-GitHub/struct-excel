from sqlalchemy import Engine
from sqlmodel import Session
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine


def init_db(path: str) -> Engine:
    engine: Engine = create_engine(path)
    SQLModel.metadata.create_all(engine)
    return engine


def model_to_db(engine: Engine, models):
    with Session(engine) as session:
        session.add_all(models)
        session.commit()
