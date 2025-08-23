from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from source.core.config import Settings

class BertExtract:
    """
    Mô hình trích xuất thông tin dựa trên BERT cho QA.
    """
    def __init__(self, config: Settings):
        self.max_length = config.MAX_LENGTH
        self.max_answer_length = config.MAX_ANSWER_LENGTH
        self.stride = config.STRIDE
        self.model_extract = AutoModelForQuestionAnswering.from_pretrained(config.MODEL_EXTRACT)
        self.tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER)
        self.n_best = config.N_BEST