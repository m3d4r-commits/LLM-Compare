import importlib
import os
import pytest

# required environment variables for the app
REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "DEEPSEEK_API_KEY",
    "ANTHROPIC_API_KEY",
]

@pytest.fixture(scope="module")
def app():
    # set dummy environment variables so the app can load
    for key in REQUIRED_KEYS:
        os.environ.setdefault(key, "test")
    import askllm
    # Reload module in case it was previously imported with missing env vars
    importlib.reload(askllm)
    askllm.app.config.update({"TESTING": True})
    return askllm.app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_app_load(app):
    """Ensure the Flask application loads without error."""
    assert app is not None
    assert app.name == "askllm"

def test_index_get(client):
    """Verify GET / returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
