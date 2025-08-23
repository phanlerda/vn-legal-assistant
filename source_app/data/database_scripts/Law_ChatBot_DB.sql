-- =============================
-- TẠO DATABASE VÀ CÁC BẢNG CHO LAW CHATBOT
-- =============================

-- 1. Tạo database
CREATE DATABASE Law_ChatBot_DB;
GO

-- 2. Sử dụng database vừa tạo
USE Law_ChatBot_DB;
GO

-- 3. Bảng lưu thông tin phiên chat
CREATE TABLE Chat_Sessions (
    id INT PRIMARY KEY IDENTITY(1,1),           -- ID tự tăng
    create_at DATETIME DEFAULT GETDATE()        -- Ngày giờ tạo phiên
);
GO

-- 4. Bảng lưu tin nhắn trong từng phiên
CREATE TABLE Chat_Messages (
    id INT PRIMARY KEY IDENTITY(1,1),           -- ID tự tăng
    session_id INT NOT NULL,                    -- Liên kết đến Chat_Sessions
    sender NVARCHAR(50),                        -- Người gửi ('user' hoặc 'bot')
    message NVARCHAR(MAX),                      -- Nội dung tin nhắn
    send_at DATETIME DEFAULT GETDATE(),         -- Thời gian gửi tin nhắn
    CONSTRAINT FK_ChatSession FOREIGN KEY (session_id) REFERENCES Chat_Sessions(id) ON DELETE CASCADE
);
GO

-- 5. Bảng lưu tài liệu/tham chiếu liên quan đến message
CREATE TABLE Chat_References (
    id INT PRIMARY KEY IDENTITY(1,1),           -- ID tự tăng
    message_id INT NOT NULL,                    -- Liên kết đến Chat_Messages
    reference_content NVARCHAR(MAX),            -- Nội dung tài liệu tham khảo
    CONSTRAINT FK_ChatMessage FOREIGN KEY (message_id) REFERENCES Chat_Messages(id) ON DELETE CASCADE
);
GO

-- =============================
-- CÁC LỆNH THAM KHẢO (XÓA, XEM DỮ LIỆU)
-- =============================
-- Xem dữ liệu:
-- SELECT * FROM Chat_Sessions;
-- SELECT * FROM Chat_Messages;
-- SELECT * FROM Chat_References;

-- Xóa toàn bộ dữ liệu:
-- DELETE FROM Chat_References;
-- DELETE FROM Chat_Messages;
-- DELETE FROM Chat_Sessions;

-- Xóa các session không còn message:
-- DELETE FROM Chat_Sessions WHERE NOT EXISTS (
--     SELECT 1 FROM Chat_Messages WHERE Chat_Messages.session_id = Chat_Sessions.id
-- );
