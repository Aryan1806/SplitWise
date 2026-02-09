"""
Database Configuration
Sets up SQLAlchemy engine, session maker, and base model.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# echo=True will log all SQL statements (useful for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10  # Maximum number of connections to create beyond pool_size
)

# Session factory
# autocommit=False: Don't auto-commit, we'll control transactions
# autoflush=False: Don't auto-flush, we'll control when to flush
# bind=engine: Associate this session with our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
# All SQLAlchemy models will inherit from this
Base = declarative_base()


def get_db():
    """
    Dependency function that creates a database session.
    
    This is used with FastAPI's dependency injection:
    - Creates a new session for each request
    - Automatically closes the session when done
    - Handles rollback on exceptions
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()