from source.core.config import Settings
from source.model.reset_apikey import APIKeyManager

class Gemini:
    """
    Quản lý truy cập model Gemini với API key luân phiên.
    """
    def __init__(self, setting: Settings):
        self.key_manager = APIKeyManager(setting.APIS_GEMINI_LIST)
        self.model_gemini = setting.MODEL_GEMINI