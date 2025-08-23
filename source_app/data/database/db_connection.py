import pyodbc
from source.core.config import Settings

class DBConnection:
    """
    Kết nối tới database sử dụng pyodbc và config từ Settings.
    """
    def __init__(self, setting: Settings):
        self.setting = setting

    def get_db_connection(self):
        """Tạo và trả về một kết nối database mới."""
        conn = pyodbc.connect(
            f"DRIVER={self.setting.DRIVER};"
            f"SERVER={self.setting.DB_HOST};"
            f"DATABASE={self.setting.DB_NAME};"
            "Trusted_Connection=yes;"
        )
        return conn