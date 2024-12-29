import pytest
import asyncio
import warnings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from _pytest.nodes import Item
from _pytest.runner import CallInfo
import json

from .test_config import test_settings
from src.core.database import Base, get_db
from src.main import app

# Define a custom marker for database tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "db: mark test as requiring database setup"
    )

# Configure event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def postgres_container():
    """Create a PostgreSQL container that lives for the entire test session."""
    print("\nStarting PostgreSQL container...")
    postgres = PostgresContainer(
        image="postgres:17",
        username=test_settings.POSTGRES_USER,
        password=test_settings.POSTGRES_PASSWORD,
        dbname=test_settings.POSTGRES_DB
    )
    try:
        postgres.start()
        connection_url = postgres.get_connection_url()
        print(f"PostgreSQL container started. Connection URL: {connection_url}")
        
        # Test the connection
        engine = create_engine(connection_url)
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("Database connection test successful")
        except Exception as e:
            print(f"Database connection test failed: {e}")
            raise
            
        test_settings.DATABASE_TEST_URL = connection_url
        yield postgres
    finally:
        print("\nStopping PostgreSQL container...")
        postgres.stop()

@pytest.fixture(scope="session")
def engine(postgres_container):
    """Create SQLAlchemy engine using the PostgreSQL container."""
    engine = create_engine(postgres_container.get_connection_url())
    try:
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Creates a new database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        # Clear all tables before each test
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        db.commit()
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user with unique email and username."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test{unique_id}@example.com",
        "username": f"testuser{unique_id}",
        "password": "Test123!@#"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    if response.status_code == 400:
        print(f"Registration failed: {response.json()}")  # Add debug logging
    assert response.status_code == 200, f"User registration failed: {response.json()}"
    return response.json()

@pytest.fixture(scope="function")
def test_user_token(client, test_user):
    """Get token for test user."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["username"],
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200, f"Token generation failed: {response.json()}"
    return response.json()["access_token"]

# @pytest.fixture(autouse=True)
# def ignore_crypt_warnings():
#     warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*crypt.*") 

def pytest_collection_modifyitems(items):
    """Modify test items in place to ensure that test classes are run in a given order."""
    # Ensure database tests run after basic tests
    db_items = []
    non_db_items = []
    
    for item in items:
        if item.get_closest_marker('db'):
            db_items.append(item)
        else:
            non_db_items.append(item)
    
    items[:] = non_db_items + db_items 

def pytest_runtest_makereport(item: Item, call: CallInfo):
    """Hook to execute after each test."""
    if call.when == "call" and item.name == "test_create_and_get_posts":
        # Get the test client from the fixture
        client = item.funcargs.get('client')
        if client:
            # Make a request to get all posts
            response = client.get("/api/v1/posts/")
            if response.status_code == 200:
                data = response.json()
                posts = data["items"]  # Get posts from items field
                total = data["total"]
                print(f"\nNumber of posts after {item.name}: {total}")
                print("Posts summary:")
                for post in posts:
                    print(f"- {post['title']} (ID: {post['id']})") 