from source.data.db.db_connection import DBConnection

class DBUtils:
    """
    Tiện ích thao tác với database cho chat sessions, messages, references.
    """
    def __init__(self, db: DBConnection):
        self.db = db

    def create_session(self) -> int:
        """Tạo session chat mới, trả về session_id."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Chat_Sessions (create_at) OUTPUT INSERTED.id VALUES (GETDATE())"
        )
        session_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return session_id

    def insert_message(self, session_id: int, sender: str, message: str) -> int:
        """Thêm message vào session, trả về message_id."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Chat_Messages (session_id, sender, message, send_at)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, GETDATE())
            """,
            (session_id, sender, message)
        )
        message_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return message_id

    def insert_references(self, message_id: int, references: list):
        """Thêm các reference cho message nếu có."""
        if not references:
            return
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        for ref in references:
            cursor.execute(
                """
                INSERT INTO Chat_References (message_id, reference_content)
                VALUES (?, ?)
                """,
                (message_id, ref)
            )
        conn.commit()
        conn.close()

    def get_references(self, message_id: int) -> list:
        """Lấy danh sách reference_content của message."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT reference_content
            FROM Chat_References
            WHERE message_id = ?
            """,
            (message_id,)
        )
        references = [row[0] for row in cursor.fetchall()]
        conn.close()
        return references

    def get_sessions(self):
        """Lấy danh sách session có user chat, kèm message đầu tiên."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        query = (
            """
            SELECT 
                cs.id, 
                cs.create_at, 
                (SELECT TOP 1 message FROM Chat_Messages 
                 WHERE session_id = cs.id AND sender = 'user' 
                 ORDER BY send_at ASC) AS first_message
            FROM Chat_Sessions cs
            WHERE EXISTS (
                SELECT 1 FROM Chat_Messages 
                WHERE session_id = cs.id AND sender = 'user'
            )
            ORDER BY cs.create_at DESC
            """
        )
        cursor.execute(query)
        sessions = cursor.fetchall()
        conn.close()
        return sessions

    def get_history(self, session_id: int):
        """Lấy toàn bộ lịch sử chat của 1 session."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        query = (
            """
            SELECT id, sender, message, send_at
            FROM Chat_Messages
            WHERE session_id = ?
            ORDER BY send_at ASC
            """
        )
        cursor.execute(query, (session_id,))
        messages = cursor.fetchall()
        conn.close()
        return messages

    def delete_session(self, session_id: int):
        """Xóa session và toàn bộ message liên quan."""
        conn = self.db.Get_DB_Connection()
        cursor = conn.cursor()
        # Nếu muốn xóa luôn message thì bỏ comment dòng dưới
        # cursor.execute("DELETE FROM Chat_Messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM Chat_Sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()