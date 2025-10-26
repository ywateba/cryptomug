import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.db.database import get_db, Base

# Use the test database URL from the environment variables set in tox.ini
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override to use the test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def before_scenario(context, scenario):
    """Set up the test client and a clean database before each scenario."""
    Base.metadata.create_all(bind=engine)
    context.client = TestClient(app)


def after_scenario(context, scenario):
    """Tear down the database after each scenario."""
    Base.metadata.drop_all(bind=engine)
