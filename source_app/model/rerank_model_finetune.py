from sentence_transformers import CrossEncoder
from source.core.config import Settings

class RerankModelFinetune:
    """
    Model rerank đã fine-tune sử dụng CrossEncoder.
    """
    def __init__(self, setting: Settings):
        # Nếu muốn dùng GPU: device='cuda' if torch.cuda.is_available() else 'cpu'
        self.model = CrossEncoder(setting.RERANK, trust_remote_code=True, device='cpu')