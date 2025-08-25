from source.core.config import Settings
from source.model.embedding_model import Sentences_Transformer_Embedding
from langchain_qdrant import Qdrant
from typing import Any

class QdrantVector:
    """
    Utility class for interacting with a Qdrant vector database collection.
    """
    def __init__(self, setting: Settings, embedding: Sentences_Transformer_Embedding) -> None:
        self.setting = setting
        self.embedding = embedding

    def open_qdrant(self) -> Any:
        """
        Open an existing Qdrant collection using the provided settings and embedding model.

        Returns:
            Qdrant: An instance of the Qdrant collection.
        Raises:
            Exception: If the collection cannot be opened.
        """
        try:
            collection = Qdrant.from_existing_collection(
                embedding=self.embedding.embeddings_bkai,
                url=self.setting.URL_QDRANT_LOCAL,
                collection_name=self.setting.EXIST_COLLECTION_NAME,
                metadata_payload_key=self.setting.metadata_payload_key
            )
            return collection
        except Exception as e:
            # Optionally, log the error here
            raise RuntimeError(f"Failed to open Qdrant collection: {e}")


