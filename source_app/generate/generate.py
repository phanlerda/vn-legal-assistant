# --- patch_langchain.py (gọi ngay khi app khởi động) ---
import importlib
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.caches import BaseCache
from langchain_core.callbacks.base import Callbacks 
mod = importlib.import_module('langchain_google_genai')
mod.BaseCache = BaseCache
mod.Callbacks = Callbacks
ChatGoogleGenerativeAI.model_rebuild()
from langchain_core.output_parsers import StrOutputParser
from source.model.generate_model import Gemini
from source.function.utils_shared import load_prompt_from_yaml,clean_generated_queries
from source.core.config import Settings
from source.tool.google_search import GoogleSearchTool
class GeminiGenerate:
    """
    Sinh truy vấn, phân loại, sinh câu trả lời và trích xuất thực thể bằng Gemini + prompt YAML.
    """
    def __init__(self, gemini_model: Gemini, settings: Settings):
        self.gemini_model = gemini_model
        self.yaml_path = settings

    def generate_query(self, original_query: str) -> list[str]:
        """Sinh các truy vấn tìm kiếm tối ưu từ truy vấn gốc."""
        prompt = load_prompt_from_yaml(self.yaml_path, 'query_generator')
        model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0
        )
        prompt = prompt.format_messages(original_query=original_query)
        result = (model | StrOutputParser()).invoke(prompt)
        generated_queries = clean_generated_queries(result.strip().split('\n'))
        return [original_query] + generated_queries

    def generate_response(self, query: str, docs: dict) -> str:
        """Sinh câu trả lời dựa trên truy vấn và tài liệu."""
        docs_str = "\n".join(f"{k}: {v}" for k, v in docs.items())
        prompt_template = load_prompt_from_yaml(self.yaml_path, "response")
        response_model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0.2,
            max_tokens=10000,
            top_p=0.6,
        )
        prompt_template = prompt_template.format_messages(original_query=query, context=docs_str)
        final_response = (response_model | StrOutputParser()).invoke(prompt_template).strip()
        return final_response

    def classify_query(self, query: str) -> int:
        """Phân loại truy vấn thành các nhóm: thông tin, pháp luật, không hợp lệ."""
        prompt = load_prompt_from_yaml(self.yaml_path, 'classify_query')
        classify_model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0
        )
        prompt = prompt.format_messages(query=query)
        classification = (classify_model | StrOutputParser()).invoke(prompt).strip()
        return int(classification)

    def invalid_query(self, query: str) -> str:
        """Sinh phản hồi cho truy vấn không hợp lệ."""
        prompt = load_prompt_from_yaml(self.yaml_path, 'invalid_query')
        invalid_model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0
        )
        prompt = prompt.format_messages(query=query)
        invalid = (invalid_model | StrOutputParser()).invoke(prompt).strip()
        return invalid

    def generate_information(self, query: str, context: str) -> str:
        """Sinh phần giới thiệu/thông tin cá nhân dựa trên context."""
        prompt = load_prompt_from_yaml(self.yaml_path, 'information_query')
        information_model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0
        )
        prompt = prompt.format_messages(query=query, context=context)
        information = (information_model | StrOutputParser()).invoke(prompt).strip()
        return information

    def extract_entities(self, query: str) -> str:
        """Trích xuất thực thể pháp lý từ truy vấn."""
        prompt = load_prompt_from_yaml(self.yaml_path, 'query_extract_entities')
        extract_information_model = ChatGoogleGenerativeAI(
            google_api_key=self.gemini_model.key_manager.get_next_key(),
            model=self.gemini_model.model_gemini,
            temperature=0
        )
        prompt = prompt.format_messages(query=query)
        extract_information = (extract_information_model | StrOutputParser()).invoke(prompt).strip()
        return extract_information
        