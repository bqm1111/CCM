from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Make the engine
engine = create_engine("sqlite+pysqlite:///camera.db", future=True, echo=False,
                       connect_args={"check_same_thread": False})

# Make the DeclarativeMeta
Base = declarative_base()

# Create SessionLocal class from sessionmaker factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

