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

def test_index_post(client, monkeypatch):
    """Submit a POST request and verify expected placeholders in the response."""
    # Mock LLM functions to avoid real network calls
    monkeypatch.setattr('askllm.query_llm_1', lambda q: 'Gemini answer')
    monkeypatch.setattr('askllm.query_llm_2', lambda q: 'GPT answer')
    monkeypatch.setattr('askllm.query_llm_3', lambda q: 'DeepSeek answer')
    monkeypatch.setattr('askllm.analyze_differences_with_llm_4', lambda r, analyzer='claude': 'analysis')

    response = client.post('/', data={'question': 'test question', 'analyzer': 'claude'})
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert 'Response from Gemini 2.5 Pro' in data
    assert 'Gemini answer' in data
    assert 'analysis' in data
