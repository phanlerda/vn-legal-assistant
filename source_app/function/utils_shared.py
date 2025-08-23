import yaml
import os
import json
import re
import textwrap
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import util
from source.core.config import Settings
from source.model.embedding_model import SentenceTransformerEmbedding
def load_prompt_from_yaml(settings: Settings, section: str) -> ChatPromptTemplate:
    """
    Load prompt template từ file YAML theo section.
    """
    current_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(current_dir, '..', 'core', settings.YAML_PATH)
    yaml_path = os.path.abspath(yaml_path)
    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    messages = yaml_data['prompts'][section]['messages']
    return ChatPromptTemplate.from_messages(
        [(msg['role'], msg['content']) for msg in messages]
    )
def load_information_from_json(settings: Settings, model_embedding: SentenceTransformerEmbedding):
    """
    Load dữ liệu corpus và embedding từ file JSON.
    """
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, '..', 'core', settings.PATH_INFOR)
    json_path = os.path.abspath(json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    corpus = [item['content'] for item in data]
    corpus_embedding = model_embedding.embeddings.embeddings.embed_documents(corpus)
    return corpus, corpus_embedding
def search_from_json(corpus_embedding, corpus, query, model_embedding: SentenceTransformerEmbedding) -> str:
    """
    Tìm kiếm các đoạn văn bản liên quan nhất từ corpus.
    """
    query_embedding = model_embedding.embeddings.embeddings.embed_query(query)
    cos_scores = util.cos_sim(query_embedding, corpus_embedding)[0]
    top_results = cos_scores.argsort(descending=True)[:5]
    results = [corpus[idx] for idx in top_results]
    return "\n".join(results)

def clean_generated_queries(queries):
    """
    Lọc các query không hợp lệ hoặc quá ngắn.
    """
    cleaned_queries = []
    for query in queries:
        if '```' in query:
            continue
        if len(query.split()) < 5:
            continue
        cleaned_queries.append(query)
    return cleaned_queries
def extract_json_dict(text: str) -> dict:
    """
    Trích xuất dict JSON từ text có code fence ```json ... ```.
    """
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    else:
        raise ValueError("Không tìm thấy nội dung JSON hợp lệ.")
    
def clean_code_fence_safe(text: str) -> str:
    """
    Loại bỏ code fence ``` ở đầu/cuối text nếu có.
    """
    lines = text.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()

def parse_raw_json(raw_text: str) -> dict:
    """
    Parse chuỗi JSON trả về từ model, đảm bảo trường answer được escape đúng.
    """
    text = raw_text.replace('“', '"').replace('”', '"')
    pattern = r'("answer"\s*:\s*")(.+?)"(?=\s*,\s*"key"|})'
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        print("DEBUG - raw_text:\n", raw_text)
        raise ValueError("Không tìm thấy trường 'answer' hoặc định dạng quá lệch không parse được.")
    prefix = match.group(1)
    raw_content = match.group(2)
    end_pos = match.end()
    escaped_content = json.dumps(raw_content)[1:-1]
    fixed_text = (
        text[: match.start(1)] +
        prefix +
        escaped_content +
        '"' +
        text[end_pos:]
    )
    fixed_text = textwrap.dedent(fixed_text).strip()
    return json.loads(fixed_text)

# def parse_raw_json(raw_text: str) -> dict:
#     # 1. Chuẩn hóa ngoặc kép Unicode
#     text = raw_text.replace('“', '"').replace('”', '"')
    
#     # 2. Pattern để bắt "answer": "<nội dung>" (hỗ trợ \\" hay \\n sẵn)
#     pattern = r'("answer"\s*:\s*")((?:[^"\\]|\\.)*?)"(?=\s*,\s*"key")'
#     match = re.search(pattern, text, flags=re.DOTALL)
#     if not match:
#         print("DEBUG - raw_text:\n", raw_text)
#         raise ValueError("Không tìm thấy trường 'answer' hoặc định dạng quá lệch không parse được.")

#     prefix = match.group(1)        # ví dụ: '"answer": "'
#     raw_content = match.group(2)   # nội dung hiện tại (chưa được escape đúng)
#     end_pos = match.end()          # vị trí ngay sau dấu " đóng của answer

#     # 3. Dùng json.dumps để escape đúng chuỗi
#     #    json.dumps trả về dạng "\"nội dung đã escape\"", nên ta cắt bỏ 2 ký tự " ở đầu-cuối
#     escaped_content = json.dumps(raw_content)[1:-1]

#     # 4. Ghép lại toàn bộ JSON: 
#     #    - Phần trước prefix
#     #    - prefix
#     #    - escaped_content
#     #    - dấu " đóng
#     #    - phần còn lại của text từ end_pos
#     fixed_text = (
#         text[: match.start(1)] +
#         prefix +
#         escaped_content +
#         '"' +
#         text[end_pos:]
#     )

#     # 5. Loại bỏ indent không cần thiết và strip
#     fixed_text = textwrap.dedent(fixed_text).strip()

#     # 6. Chuyển thành dict
#     return json.loads(fixed_text)



