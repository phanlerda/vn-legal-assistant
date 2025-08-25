
from fastapi import APIRouter, HTTPException
from source.function.utils_result import RAG
from source.search.utils_search import QdrantUtils
from source.rerank.utils_rerank import RerankUtils
from source.model.embedding_model import SentenceTransformerEmbedding
from source.model.extract_model import BertExtract
from source.model.generate_model import Gemini
from source.model.rerank_model import Cohere
from source.model.rerank_model_finetune import RerankModelFinetune
from source.data.vectordb.qdrant import Qdrant_Vector
from source.core.config import Settings
from source.generate.generate import GeminiGenerate
from source.extract.utils_extract import ExtractInformation
from source.schema.chatbot_querry import ChatbotQuery
from source.tool.utils_search import UtilsSearchTools
from source.tool.google_search import GoogleSearchTool
from typing import Any, Dict

setting = Settings()
gemini = Gemini(setting)
cohere = Cohere(setting)
bert = BertExtract(setting)
sentences_transformer_embedding = SentenceTransformerEmbedding(setting)
qdrant = Qdrant_Vector(setting, sentences_transformer_embedding)
router = APIRouter()
model_finetune = RerankModelFinetune(setting)
rerank_utils = RerankUtils(cohere, model_finetune)
extract_utils = ExtractInformation(bert)
generate_utils = GeminiGenerate(gemini, setting)
qdrant_utils = QdrantUtils(qdrant, generate_utils)
rag = RAG(generate_utils, extract_utils, qdrant_utils, rerank_utils, setting, sentences_transformer_embedding)

# Khởi tạo các tools cần thiết cho web search
google_search_tools = GoogleSearchTool(setting)
search_tools = UtilsSearchTools(setting, generate_utils, extract_utils, google_search_tools)


@router.post("/chatbot-with-search-web")
def chatbot_with_search_web(query: ChatbotQuery) -> Dict[str, Any]:
    """Chatbot trả lời với kết quả tìm kiếm web."""
    try:
        user_input = query.query
        answer, relevant_links = search_tools.search_docs_from_tools(user_input)
        return {
            "answer": answer,
            "lst_Relevant_Documents": relevant_links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.post("/chatbot-with-gemini")
def chatbot_with_gemini(query: ChatbotQuery) -> Dict[str, Any]:
    """Chatbot trả lời với pipeline Gemini (không dùng web search)."""
    try:
        user_input = query.query
        article_document_results, lst_article_quote, use_web_search = rag.get_article_content_results(user_input)
        return {
            "answer": article_document_results,
            "lst_Relevant_Documents": lst_article_quote,
            "use_web_search": use_web_search
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
