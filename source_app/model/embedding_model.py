from langchain_huggingface import HuggingFaceEmbeddings
from source.core.config import Settings
class Sentences_Transformer_Embedding:
    """
    Tạo embedding từ mô hình HuggingFace cho các câu văn bản.
    """
    def __init__(self,setting:Settings):
            self.embeddings_bkai = HuggingFaceEmbeddings(
            model_name=setting.MODEL_EMBEDDING,
            model_kwargs=setting.DEVICE,
            encode_kwargs={"normalize_embeddings": True}
        )