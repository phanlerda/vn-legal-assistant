from source.rerank.utils_rerank import Rerank_Utils
from source.search.utils_search import Qdrant_Utils
from source.extract.utils_extract import Extract_Information
from source.generate.generate import Gemini_Generate
from source.core.config import Settings
from source.function.utils_shared import load_information_from_json,search_from_json,clean_code_fence_safe,parse_raw_json
from source.model.embedding_model import SentenceTransformerEmbedding

class RAG:
    """
    Thực hiện các pipeline RAG (Retrieval-Augmented Generation) cho chatbot pháp luật.
    """
    def __init__(self, gemini_utils: Gemini_Generate, bert_utils: Extract_Information, qdrant_utils: Qdrant_Utils, rerank_utils: Rerank_Utils, setting: Settings, model_embedding: SentenceTransformerEmbedding):
        self.qdrant_utils = qdrant_utils
        self.rerank_utils = rerank_utils
        self.extract_utils = bert_utils
        self.generate = gemini_utils
        self.model_embedding = model_embedding
        self.corpus, self.corpus_embedding = load_information_from_json(setting, self.model_embedding)

    def get_gemini_response(self, user_query: str):
        """Sinh response từ Gemini cho truy vấn đầu vào."""
        return self.generate.generate_response(user_query)

    def get_gemini_response_rag_basic(self, user_query: str):
        document = self.qdrant_utils.search_documents(user_query)
        result = self.generate.generate_response(user_query, document)
        answer_result = clean_code_fence_safe(result)
        answer_result = parse_raw_json(answer_result)
        return answer_result['answer']

    def get_gemini_response_rag_final(self, user_query: str):
        article_documents = self.qdrant_utils.search_With_Similarity_Queries(user_query)
        rrf_result_docs = self.rerank_utils.reciprocal_rank_fusion(article_documents)
        rerank_article_documents = self.rerank_utils.rerank_documents(user_query, rrf_result_docs)
        result_gemini = self.generate.generate_response(user_query, rerank_article_documents)
        answer_result = clean_code_fence_safe(result_gemini)
        answer_result = parse_raw_json(answer_result)
        return answer_result['answer']

    def get_gemini_response_rag_final_extract(self, user_query: str):
        article_documents = self.qdrant_utils.search_With_Similarity_Queries(user_query)
        rrf_result_docs = self.rerank_utils.reciprocal_rank_fusion(article_documents)
        rerank_article_documents = self.rerank_utils.rerank_documents(user_query, rrf_result_docs)
        article_content_results = [doc.replace("_", " ") for doc, _ in rerank_article_documents]
        document_reduce = self.extract_utils.predict(article_content_results, user_query)
        result_gemini = self.generate.generate_response(user_query, document_reduce)
        answer_result = clean_code_fence_safe(result_gemini)
        answer_result = parse_raw_json(answer_result)
        return answer_result['answer']

    def get_Article_Content_Results(self, user_query: str):
        check = self.generate.classify_query(user_query)
        if check == 0:
            context = search_from_json(self.corpus_embedding, self.corpus, user_query, self.model_embedding)
            return self.generate.generate_information(user_query, context), "", False
        elif check == 2:
            return self.generate.invalid_query(user_query), "", False
        elif check == 1:
            article_documents = self.qdrant_utils.search_With_Similarity_Queries(user_query)
            rrf_result_docs = self.rerank_utils.reciprocal_rank_fusion(article_documents)
            rerank_article_documents = self.rerank_utils.rerank_documents_finetune(user_query, rrf_result_docs)
            article_content_results = [doc.replace("_", " ") for doc, _ in rerank_article_documents]
            try:
                document_reduce = self.extract_utils.predict(article_content_results, user_query)
                result_gemini = self.generate.generate_response(user_query, document_reduce)
                answer_result = clean_code_fence_safe(result_gemini)
                answer_result = parse_raw_json(answer_result)
                selected_keys = answer_result.get("key", [])
                answer = answer_result.get('answer', "")
                if selected_keys:
                    selected_documents = [rerank_article_documents[i] for i in selected_keys]
                    lst_Article_Quote = [
                        f"""
                        Tài liệu tham khảo: {i+1}
                        Loại văn bản: {infor['doc_metadata'].get('LoaiVanBan', '')}
                        Nơi ban hành: {infor['doc_metadata'].get('NoiBanHanh', '')}
                        Số hiệu: {infor['doc_metadata'].get('SoHieu', '')}
                        Lĩnh vực - ngành: {infor['doc_metadata'].get('LinhVucNganh', '')}
                        Ngày ban hành: {infor['doc_metadata'].get('NgayBanHanh', '')}
                        Chủ đề: {infor['doc_metadata'].get('ChuDe', '')}
                        Chương: {infor['doc_metadata'].get('Chapter', '')}
                        Mục: {infor['doc_metadata'].get('Section', '')}
                        Tiểu mục: {infor['doc_metadata'].get('MiniSection', '')}
                        {infor['doc_metadata'].get('Article', '')}
                        <=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=>
                        {doc.replace('_', ' ').replace(' .', '.').replace(' ,', ',').replace(' !', '!').replace(' ?', '?').replace(' :', ':').replace(' ;', ';')}
                        """
                        for i, ((doc, infor), key) in enumerate(zip(selected_documents, selected_keys))
                    ]
                    return answer, lst_Article_Quote, False
                else:
                    return "", [], True
            except Exception as e:
                print(e)
                return "", [], True