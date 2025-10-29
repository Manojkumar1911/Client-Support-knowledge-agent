"""Test configuration loading and validation."""
from app.utils.config import Config, settings

def test_config_loads():
    """Test that critical configuration values are present."""
    assert Config.MONGO_URI and isinstance(Config.MONGO_URI, str)
    assert Config.MONGO_DB_NAME and isinstance(Config.MONGO_DB_NAME, str)
    assert Config.GEMINI_API_KEY and isinstance(Config.GEMINI_API_KEY, str)
    assert Config.CHROMA_DIR and isinstance(Config.CHROMA_DIR, str)
    
def test_settings_match_config():
    """Test that Config class matches Settings."""
    assert Config.MONGO_URI == settings.MONGO_URI
    assert Config.MONGO_DB_NAME == settings.MONGO_DB_NAME
    assert Config.GEMINI_API_KEY == settings.GEMINI_API_KEY
    assert Config.CHROMA_DIR == settings.CHROMA_DIR