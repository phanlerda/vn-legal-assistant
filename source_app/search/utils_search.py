from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from pyvi import ViTokenizer
from typing import Optional
from source.generate.generate import Gemini_Generate
from source.data.vectordb.qdrant import Qdrant_Vector
from source.function.utils_shared import extract_json_dict
 
class QdrantUtils:
    """
    Cung cấp các hàm tìm kiếm tài liệu và xây dựng filter metadata cho Qdrant.
    """
    def __init__(self, qdrant: Qdrant_Vector, gemini_util: Gemini_Generate):
        self.qdrant = qdrant
        self.gemini = gemini_util

    def search_documents(self, query: str, top_k: int = 25, filter: Optional[Filter] = None):
        """Tìm kiếm tài liệu tương tự với truy vấn và filter metadata (nếu có)."""
        connection = self.qdrant.Open_Qdrant()
        return connection.similarity_search_with_score(
            query=query,
            k=top_k,
            timeout=300,
            filter=filter
        )

    def build_metadata_filter(self, entity_dict: dict) -> Optional[Filter]:
        """Tạo filter metadata cho Qdrant từ dict thực thể."""
        conditions = []
        for key, value in entity_dict.items():
            if key == "NgayBanHanhFilter":
                conditions.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchAny(any=[value])
                    )
                )
            else:
                conditions.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value.lower())
                    )
                )
        if not conditions:
            return None
        return Filter(should=conditions)

    def search_with_similarity_queries(self, user_query: str):
        """Sinh các truy vấn tối ưu, trích xuất thực thể, tìm kiếm tài liệu tương ứng."""
        queries = self.gemini.generate_query(user_query)
        query_results = []
        for query in queries:
            tokenized_query = ViTokenizer.tokenize(query)
            raw_result = self.gemini.extract_entities(query)
            entity_dict = extract_json_dict(raw_result)
            metadata_filter = self.build_metadata_filter(entity_dict) if entity_dict else None
            search_results = self.search_documents(tokenized_query, filter=metadata_filter)
            query_results.append(search_results)
        return query_results
