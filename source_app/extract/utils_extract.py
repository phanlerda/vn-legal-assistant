import numpy as np
import torch
from pyvi import ViTokenizer
from source.model.extract_model import BertExtract
from typing import List, Dict, Any

class ExtractInformation:
    """
    Thực hiện trích xuất thông tin trả lời từ các đoạn context sử dụng mô hình BERT QA.
    """
    def __init__(self, bert: BertExtract):
        self.bert = bert

    def predict(self, contexts: List[str], question: str) -> Dict[int, str]:
        """
        Trả về dict: index context -> câu trả lời tốt nhất hoặc thông báo không có.
        """
        lst_answer_final = {}
        question_tok = ViTokenizer.tokenize(question)
        try:
            for idx, context in enumerate(contexts):
                context_tok = ViTokenizer.tokenize(context)
                inputs = self.bert.tokenizer(
                    question_tok,
                    context_tok,
                    max_length=self.bert.max_length,
                    truncation="only_second",
                    stride=self.bert.stride,
                    return_offsets_mapping=True,
                    padding="max_length",
                    return_tensors="pt"
                )
                with torch.no_grad():
                    outputs = self.bert.model_extract(**{k: v for k, v in inputs.items() if k in ['input_ids', 'attention_mask']})
                start_logits = outputs.start_logits.squeeze().cpu().numpy()
                end_logits = outputs.end_logits.squeeze().cpu().numpy()
                offsets = inputs["offset_mapping"][0].cpu().numpy()
                answers = []
                n_best = getattr(self.bert, 'n_best', getattr(self.bert, 'nbert', 5))
                start_indexes = np.argsort(start_logits)[-n_best:][::-1].tolist()
                end_indexes = np.argsort(end_logits)[-n_best:][::-1].tolist()
                for start_index in start_indexes:
                    for end_index in end_indexes:
                        if end_index < start_index or end_index - start_index + 1 > self.bert.max_answer_length:
                            continue
                        if offsets[start_index][0] is not None and offsets[end_index][1] is not None:
                            answer_text = context_tok[offsets[start_index][0]: offsets[end_index][1]].strip()
                            if answer_text:
                                answers.append({
                                    "text": answer_text,
                                    "score": start_logits[start_index] + end_logits[end_index],
                                })
                if answers:
                    answers.sort(key=lambda x: x["score"], reverse=True)
                    best_answer = answers[0]['text']
                    lst_answer_final[idx] = best_answer.replace("_", " ").replace(' .', '.').replace(' ,', ',').replace(' !', '!').replace(' ?', '?').replace(' :', ':').replace(' ;', ';')
                else:
                    lst_answer_final[idx] = "Không có câu trả lời"
        except Exception as e:
            print(f"Lỗi xảy ra: {e}")
            return {0: "Không có câu trả lời do lỗi xử lý"}
        return lst_answer_final