class APIKeyManager:
    """
    Quản lý luân phiên và thống kê số lần sử dụng các API key.
    """
    def __init__(self, keys):
        if not keys:
            raise ValueError("Danh sách API key không được rỗng.")
        self._usage = {key: 0 for key in keys}
        self._key_list = list(self._usage.keys())
        self._index = 0

    def get_next_key(self):
        """Trả về API key tiếp theo theo vòng tròn và tăng số lần sử dụng."""
        if not self._key_list:
            raise RuntimeError("Không có API key để sử dụng.")
        key = self._key_list[self._index]
        self._usage[key] += 1
        self._index = (self._index + 1) % len(self._key_list)
        return key

    def get_key_usage(self):
        """Trả về dict số lần sử dụng của từng API key."""
        return dict(self._usage)