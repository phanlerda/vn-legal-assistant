from pydantic_settings import BaseSettings
import os 
from dotenv import load_dotenv
load_dotenv()
class Settings():
    def __init__(self):
        self.URL_QDRANT_LOCAL: str = os.getenv("URL_QDRANT_LOCAL")
        self.EXIST_COLLECTION_NAME: str = os.getenv("EXIST_COLLECTION_NAME")
        self.APIS_GEMINI_LIST: list = os.getenv("APIS_GEMINI_LIST").split(',')
        self.MODEL_GEMINI: str = os.getenv("MODEL_GEMIMI")
        self.MODEL_RERANK: str = os.getenv("MODEL_RERANKER")
        self.API_RERANKER: list = os.getenv('API_RERANKER').split(',')
        self.MODEL_EMBEDDING: str = os.getenv("MODEL_EMBEDDING")
        self.metadata_payload_key="metadata"
        self.MODEL_EXTRACT:str=os.getenv("GENERATE_MODEL_EXTRACT")
        self.TOKENIZER:str=os.getenv("GENERATE_MODEL_TOKENIZER")
        self.SERVER_SSMS = os.getenv("SERVER_SSMS")
        self.MAX_LENGTH = 512
        self.STRIDE = 150
        self.N_BEST = 380
        self.MAX_ANSWER_LENGTH = 2000
        self.DEVICE={"device": "cuda"}
        self.YAML_PATH=os.getenv("PATH_PROMPT")
        self.PATH_INFOR=os.getenv("PATH_INFOR")
        self.GOOGLE_SEARCH_API=os.getenv("GOOGLE_SEARCH_API")
        self.TOOL_SEARCH=os.getenv("TOOL_SEARCH_API")
        # Thêm các biến kết nối DB
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DRIVER=os.getenv("DRIVER")
        self.RERANK=os.getenv("MODEL_RERANK")