
from fastapi import APIRouter, HTTPException
from source.schema.message_input import MessageInput
from source.data.db.utils_db import DB_Utils
from source.data.db.db_connection import DBConnection
from source.core.config import Settings
from typing import Any, Dict

router = APIRouter()
setting = Settings()
db = DBConnection(setting)
db_utils = DB_Utils(db)


@router.post("/start-session")
def start_session() -> Dict[str, Any]:
    """Khởi tạo session mới."""
    try:
        session_id = db_utils.create_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")


@router.post("/save-message")
def save_message(data: MessageInput) -> Dict[str, str]:
    """Lưu message vào session."""
    try:
        message_id = db_utils.insert_message(data.session_id, data.sender, data.message)
        if data.sender == 'bot' and hasattr(data, 'references'):
            db_utils.insert_references(message_id, data.references)
        return {"status": "success", "message": "Message saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving message: {str(e)}")


@router.get("/get-sessions")
def get_sessions() -> Dict[str, Any]:
    """Lấy danh sách các session."""
    try:
        sessions = db_utils.get_session()
        return {
            "sessions": [
                {"id": s[0], "create_at": s[1], "first_message": s[2]} for s in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")


@router.get("/get-chat-history/{session_id}")
def get_chat_history(session_id: int) -> Dict[str, Any]:
    """Lấy lịch sử chat của một session."""
    try:
        messages = db_utils.get_history(session_id)
        return {
            "chat_history": [
                {
                    "id": m[0],
                    "sender": m[1],
                    "message": m[2],
                    "send_at": m[3].strftime('%Y-%m-%d %H:%M:%S') if hasattr(m[3], 'strftime') else m[3]
                } for m in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")


@router.get("/get-message-references/{message_id}")
def get_message_references(message_id: int) -> Dict[str, Any]:
    """Lấy danh sách tài liệu tham khảo của một message."""
    try:
        references = db_utils.get_references(message_id)
        return {"references": references}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching message references: {str(e)}")


@router.delete("/delete-session/{session_id}")
def delete_session(session_id: int) -> Dict[str, str]:
    """Xóa một session."""
    try:
        db_utils.delete_session(session_id)
        return {"status": "success", "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
