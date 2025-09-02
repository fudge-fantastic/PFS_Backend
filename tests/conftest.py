import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user():
    return {
        "email": "test@pixelforgestudio.in",
        "password": "testpassword123"
    }

@pytest.fixture
def sample_admin():
    return {
        "email": "admin@pfs.in",
        "password": "adminpassword123"
    }

@pytest.fixture
def sample_product():
    return {
        "title": "Beautiful Photo Magnet",
        "price": 25.99,
        "category": "Photo Magnets",
        "rating": 4.5
    }
