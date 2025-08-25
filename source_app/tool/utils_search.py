import json
from typing import Tuple, List
from source.function.utils_shared import clean_code_fence_safe, parse_raw_json
from source.extract.utils_extract import ExtractInformation
from source.core.config import Settings
from source.generate.generate import GeminiGenerate
from source.tool.google_search import GoogleSearchTool

class UtilsSearchTools:
    """
    Tìm kiếm, trích xuất, rút gọn và tổng hợp kết quả từ Google Search cho chatbot.
    """
    def __init__(self, setting: Settings, gemini_func: GeminiGenerate, extract_func: ExtractInformation, google_search_tools: GoogleSearchTool):
        self.setting = setting
        self.gemini_func = gemini_func
        self.extract_func = extract_func
        self.google_search_tools = google_search_tools

    def search_docs_from_tools(self, query: str) -> Tuple[str, List[str]]:
        """
        Tìm kiếm, trích xuất, rút gọn và tổng hợp kết quả từ Google Search.
        Trả về tuple: (câu trả lời hoặc thông báo lỗi, danh sách link liên quan).
        """
        try:
            lst_links = self.google_search_tools.search(query)
            lst_docs = self.google_search_tools.extract_texts_from_links(lst_links)
            lst_reduce_docs = self.extract_func.predict(lst_docs, query)
            result_final = self.gemini_func.generate_response(query, lst_reduce_docs)
            answer_result = clean_code_fence_safe(result_final)
            answer_result = parse_raw_json(answer_result)
            relevant_links = [lst_links[i] for i in answer_result.get('key', []) if i < len(lst_links)]
            if not relevant_links:
                error_message = "Xin lỗi, tôi không thể đưa ra kết quả cuối cùng được. Tuy nhiên, bạn có thể tham khảo thông qua danh sách các tài liệu mà tôi đã tìm kiếm."
                return error_message, lst_links
            return answer_result.get('answer', ''), relevant_links
        except Exception as e:
            print(f"Đang bị lỗi: {e}")
            error_message = "Xin lỗi, tôi không thể đưa ra kết quả cuối cùng được. Tuy nhiên, bạn có thể tham khảo thông qua danh sách các tài liệu mà tôi đã tìm kiếm."
            return error_message, []