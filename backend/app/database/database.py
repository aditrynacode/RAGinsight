from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_PATH

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
Base = declarative_base()

def create_tables():

    # Import every model module here (not at top-level) so they register
    # themselves on Base.metadata before create_all runs, without creating
    # circular imports with database.py.
    from app.database.models import Document
    from app.database.models import Chunk
    from app.database.models import QueryLog
    from app.database.models import Feedback
    from app.database.models import Diagnosis
    from app.database.models import Experiment
    from app.database.models import EvalScore

    Base.metadata.create_all(bind=engine)
