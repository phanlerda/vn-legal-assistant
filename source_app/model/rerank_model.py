from source.model.reset_apikey import APIKeyManager
from source.core.config import Settings
from sentence_transformers import CrossEncoder

class Cohere:
    """
    Quản lý model rerank Cohere và API key luân phiên.
    """
    def __init__(self, setting: Settings):
        self.key_manager = APIKeyManager(setting.API_RERANKER)
        self.model_cohere = setting.MODEL_RERANK