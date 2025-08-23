// ===== Flex selectors: ưu tiên HTML mới, fallback HTML cũ =====
const $sidebar         = $('.sidebar');
const $toggleButton    = $('.toggle-button');

// new-chat: .new-chat-btn (mới) hoặc #new-chat (cũ)
const $newChatBtn      = $('.new-chat-btn').length ? $('.new-chat-btn') : $('#new-chat');

// input: #chatInput (mới) hoặc #user-query (cũ)
const $userInput       = $('#chatInput').length ? $('#chatInput') : $('#user-query');

// send: .send-btn (mới) hoặc #send-button (cũ)
const $sendButton      = $('.send-btn').length ? $('.send-btn') : $('#send-button');

// chat output: #chat-output (cũ vẫn dùng id này; nếu HTML mới chưa có, thêm guard)
const $chatOutput      = $('#chat-output');

// optional buttons có thể không tồn tại trong HTML mới
const $toggleSearchWeb = $('#toggle-search-web'); // có thể rỗng
const $clearChatButton = $('#clear-chat');        // có thể rỗng

let isLoading = false;
let isTyping  = false;
let isSearchWebMode = false;
let currentSessionId = null;

// ===== Sidebar toggle giữ nguyên hành vi =====
function toggleSidebar() {
  const $newChat = $newChatBtn;
  if ($sidebar.hasClass('sidebar-collapsed')) {
    $sidebar.removeClass('sidebar-collapsed');
    $('.sidebar-content').show();
    $toggleButton.attr('title', 'Close Sidebar');
    $newChat.attr('title', 'New Chat');
  } else {
    $sidebar.addClass('sidebar-collapsed');
    $('.sidebar-content').hide();
    $toggleButton.attr('title', 'Open Sidebar');
    $newChat.removeAttr('title');
  }
}
window.toggleSidebar = window.toggleSidebar || toggleSidebar;

// ===== Ready: đặt title đúng trạng thái & init session / input =====
$(document).ready(function () {
  if ($sidebar.hasClass('sidebar-collapsed')) {
    $toggleButton.attr('title', 'Open Sidebar');
    $newChatBtn.removeAttr('title');
  } else {
    $toggleButton.attr('title', 'Close Sidebar');
    $newChatBtn.attr('title', 'New Chat');
  }

  // Nếu có session_id → load lịch sử, ngược lại input mở sẵn (UI mới)
  const sid = localStorage.getItem('session_id');
  if (sid) {
    loadChatHistory(sid);
  } else {
    enableInput(true, 'Nhập tin nhắn ...');
  }

  updateSearchWebButtonState();
});

// ===== Helpers =====
function enableInput(enabled, placeholderText) {
  if (!$userInput.length) return;
  $userInput.prop('disabled', !enabled);
  if (placeholderText) $userInput.attr('placeholder', placeholderText);
  updateSendButtonState();
}

function updateSendButtonState() {
  if (!$userInput.length || !$sendButton.length) return;
  if ($userInput.val()?.trim() !== "" && !isTyping && !isLoading) {
    $sendButton.addClass('active').removeClass('disabled').prop('disabled', false);
  } else {
    $sendButton.removeClass('active').addClass('disabled').prop('disabled', true);
  }
}

function updateSearchWebButtonState() {
  if (!$toggleSearchWeb.length) return; // không có nút này trong HTML mới thì bỏ qua
  if (currentSessionId) {
    $toggleSearchWeb.prop('disabled', false).removeClass('disabled');
  } else {
    $toggleSearchWeb.prop('disabled', true).addClass('disabled');
  }
}

// ===== Input events =====
if ($userInput.length) {
  $userInput.on('input', updateSendButtonState);

  // Enter-to-send
  $userInput.on('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });
}

// ===== Send button click =====
if ($sendButton.length) {
  $sendButton.on('click', function () {
    // hiệu ứng UI mới (không ảnh hưởng logic)
    try {
      this.style.transform = 'translateY(-50%) scale(0.95)';
      setTimeout(() => {
        this.style.transform = 'translateY(-50%) scale(1.05)';
        setTimeout(() => { this.style.transform = 'translateY(-50%) scale(1)'; }, 100);
      }, 100);
    } catch (_) {}

    sendMessage();
  });
}

// ===== Search Web toggle (nếu có) =====
if ($toggleSearchWeb.length) {
  $toggleSearchWeb.on('click', function () {
    if ($(this).prop('disabled')) return;
    isSearchWebMode = !isSearchWebMode;
    $(this).toggleClass('active', isSearchWebMode);
    if (isSearchWebMode) {
      $(this).find('span').text('🌐 Search');
      if ($userInput.length) $userInput.attr('placeholder', 'Trả lời dùng Search Tool ...');
    } else {
      $(this).find('span').text('Chat');
      if ($userInput.length) $userInput.attr('placeholder', 'Nhập tin nhắn ...');
    }
  });
}

const OUT_OF_SCOPE_MESSAGE = "Xin lỗi bạn. Kiến thức này nằm ngoài phạm vi hiểu biết của tôi. Bạn có thể hỏi tôi một câu hỏi khác không? Tôi sẽ cố gắng giải đáp câu hỏi của bạn!";

// ===== Send message =====
function sendMessage() {
  if (!$userInput.length || !$chatOutput.length) return;
  const query = $userInput.val().trim();
  if (!query || isLoading || isTyping) return;

  $('#relevant-documents-container').empty();
  $sendButton.prop('disabled', true).removeClass('active').addClass('disabled');
  isLoading = true;
  $('#loading-indicator').text("Loading...");

  $chatOutput.append(`
    <div class="chat-message user">
      <div class="avatar user-avatar" style="background-image: url('https://media.istockphoto.com/id/1300845620/vector/user-icon-flat-isolated-on-white-background-user-symbol-vector-illustration.jpg?s=612x612&w=0&k=20&c=yBeyba0hUkh14_jgv1OKqIH0CCSWU_4ckRkAoy2p73o=');"></div>
      <div class="message">${query}</div>
    </div>
  `);

  saveMessage(currentSessionId, 'user', query);

  if ($('#chat-sessions .chat-session[data-session-id="' + currentSessionId + '"]').length === 0) {
    addChatSessionToSidebar(currentSessionId, query);
  }

  $userInput.val('');
  $chatOutput.scrollTop($chatOutput.prop('scrollHeight'));

  const $typingIndicator = $(`
    <div class="chat-message bot typing-indicator">
      <div class="avatar bot-avatar" style="background-image: url('https://media.istockphoto.com/id/1333838449/vector/chatbot-icon-support-bot-cute-smiling-robot-with-headset-the-symbol-of-an-instant-response.jpg?s=612x612&w=0&k=20&c=sJ_uGp9wJ5SRsFYKPwb-dWQqkskfs7Fz5vCs2w5w950=');"></div>
      <div class="message" style="font-size:14px;color:rgba(0,0,0,0.6);display:flex;align-items:center;">
        Đang suy nghĩ câu trả lời 
        <div class="time-count" style="margin:0 5px;">00:00</div>
        <span>.</span><span>.</span><span>.</span>
      </div>
    </div>
  `);
  $chatOutput.append($typingIndicator);
  $chatOutput.scrollTop($chatOutput.prop('scrollHeight'));

  const startTime = Date.now();
  const updateTimeInterval = setInterval(() => {
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsedTime / 60);
    const seconds = elapsedTime % 60;
    const formatted = `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    $typingIndicator.find('.time-count').text(formatted);
  }, 1000);

  $.ajax({
    url: 'http://127.0.0.1:8000/api/chat/chatbot-with-gemini',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ query }),
    success: function (data) {
      clearInterval(updateTimeInterval);
      $typingIndicator.remove();

      if (data.use_web_search || (typeof data.answer === 'string' && data.answer.trim() === OUT_OF_SCOPE_MESSAGE)) {
        searchWeb(query);
      } else {
        processResponse(data);
        saveMessage(currentSessionId, 'bot', data.answer, data.lst_Relevant_Documents);
        $chatOutput.scrollTop($chatOutput.prop('scrollHeight'));
        isLoading = false;
        updateSendButtonState();
        $('#loading-indicator').text("");
      }
    }
  });
}

// ===== Search Web fallback =====
function searchWeb(query) {
  if (!$chatOutput.length) return;

  const $combinedMessage = $(`
    <div class="chat-message bot">
      <div class="avatar bot-avatar" style="background-image: url('https://media.istockphoto.com/id/1333838449/vector/chatbot-icon-support-bot-cute-smiling-robot-with-headset-the-symbol-of-an-instant-response.jpg?s=612x612&w=0&k=20&c=sJ_uGp9wJ5SRsFYKPwb-dWQqkskfs7Fz5vCs2w5w950=');"></div>
      <div class="message">
        <div class="transition-text" style="margin-bottom:10px;">Xin lỗi bạn. Kiến thức này nằm ngoài phạm vi hiểu biết của tôi. Tôi sẽ tiến hành tìm kiếm thông qua kết quả bên ngoài</div>
        <div class="searching-text" style="font-size:14px;color:rgba(0,0,0,0.6);display:flex;align-items:center;">
          Đang tìm kiếm thông tin từ web
          <div class="time-count" style="margin:0 5px;">00:00</div>
          <span>.</span><span>.</span><span>.</span>
        </div>
      </div>
    </div>
  `);
  $chatOutput.append($combinedMessage);
  $chatOutput.scrollTop($chatOutput.prop('scrollHeight'));

  const startTime = Date.now();
  const updateTimeInterval = setInterval(() => {
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsedTime / 60);
    const seconds = elapsedTime % 60;
    const formatted = `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    $combinedMessage.find('.time-count').text(formatted);
  }, 1000);

  $.ajax({
    url: 'http://127.0.0.1:8000/api/chat/chatbot-with-search-web',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ query }),
    success: function (data) {
      clearInterval(updateTimeInterval);
      $combinedMessage.remove();
      processResponse(data);
      saveMessage(currentSessionId, 'bot', data.answer, data.lst_Relevant_Documents);
      $chatOutput.scrollTop($chatOutput.prop('scrollHeight'));
      isLoading = false;
      updateSendButtonState();
      $('#loading-indicator').text("");
    }
  });
}

// ===== Render bot message + references =====
function processResponse(data) {
  const { answer, lst_Relevant_Documents } = data;
  let formattedAnswer = answer
    .replace(/\\n\\n/g, "<br><br>")
    .replace(/\\n/g, "<br>")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  const $botMessage = $(`
    <div class="chat-message bot">
      <div class="avatar bot-avatar" style="background-image: url('https://media.istockphoto.com/id/1333838449/vector/chatbot-icon-support-bot-cute-smiling-robot-with-headset-the-symbol-of-an-instant-response.jpg?s=612x612&w=0&k=20&c=sJ_uGp9wJ5SRsFYKPwb-dWQqkskfs7Fz5vCs2w5w950=');"></div>
      <div class="message"></div>
    </div>
  `);
  $chatOutput.append($botMessage);
  typeMessage($botMessage.find(".message"), formattedAnswer, () => {
    if (lst_Relevant_Documents && lst_Relevant_Documents.length > 0) {
      displayRelevantDocuments(lst_Relevant_Documents);
    } else {
      $('#relevant-documents-container').empty();
    }
    $('#show-references-btn').remove();
    $('.references-overlay').remove();
  });
}

function typeMessage($element, message, callback) {
  const parts = message.split(/(<br>)/g);
  let words = [];
  parts.forEach(part => {
    if (part === "<br>") {
      words.push("<br>");
    } else {
      const splitWords = part.split(" ");
      splitWords.forEach((w, i) => {
        if (w !== "" || i < splitWords.length - 1) words.push(w);
      });
    }
  });

  let wordIndex = 0;
  isTyping = true;
  updateSendButtonState();

  const interval = setInterval(() => {
    if (wordIndex < words.length) {
      if (words[wordIndex] === "<br>") {
        $element.append("<br>");
      } else {
        const addSpace = (wordIndex < words.length - 1 && words[wordIndex + 1] !== "<br>");
        $element.append(words[wordIndex] + (addSpace ? " " : ""));
      }
      wordIndex++;
      $element.parent().scrollTop($element.parent().prop('scrollHeight'));
    } else {
      clearInterval(interval);
      isTyping = false;
      updateSendButtonState();
      if (callback) callback();
    }
  }, 25);
}

// ===== References (giữ nguyên luồng cũ) =====
function displayRelevantDocuments(documents) {
  const container = $('#relevant-documents-container');
  container.empty();

  const maxReferences = 5;
  const displayDocs = documents.slice(0, maxReferences);
  const count = displayDocs.length;
  let badgeClass = '';
  if (count >= 5) badgeClass = 'red';
  else if (count >= 3) badgeClass = 'orange';

  const header = $(`
    <div class="references-collapsible-header" style="cursor:pointer;">
      <span class="references-collapsible-arrow">▶</span>
      <span>Trích dẫn tham khảo</span>
      <span class="references-collapsible-badge ${badgeClass}">${count}</span>
    </div>
  `);
  container.append(header);
  header.on('click', function () { showReferencesModal(displayDocs); });
}

function showReferencesModal(documents) {
  $('.references-modal-overlay').remove();
  const overlay = $(`
    <div class="references-modal-overlay">
      <div class="references-modal-popup">
        <div class="references-modal-title">📑 Trích dẫn tham khảo (${documents.length})</div>
        <button class="references-modal-close" title="Đóng">×</button>
        <div class="documents-wrapper"></div>
      </div>
    </div>
  `);
  const documentsWrapper = overlay.find('.documents-wrapper');
  documents.forEach((doc) => {
    if (typeof doc === 'string' && doc.startsWith('http')) {
      documentsWrapper.append(`
        <div class="relevant-document">
          <span class="doc-icon">🔗</span>
          <div class="doc-title">Link tham khảo</div>
          <div class="doc-content"><a href="${doc}" target="_blank" rel="noopener noreferrer">${doc}</a></div>
        </div>
      `);
      return;
    }
    const parts = doc.split('<=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=>');
    if (parts.length > 1) {
      const contentPart = parts[1].trim();
      const metadataPart = parts[0].trim();
      const loaiVanBanMatch = metadataPart.match(/Loại văn bản: (.*)/);
      const soHieuMatch = metadataPart.match(/Số hiệu: (.*)/);
      const loaiVanBan = loaiVanBanMatch ? loaiVanBanMatch[1] : "N/A";
      const soHieu = soHieuMatch ? soHieuMatch[1] : "N/A";
      const shortContent = contentPart.length > 40 ? contentPart.substring(0, 40) + '...' : contentPart;
      const docElement = $(`
        <div class="relevant-document" data-full-content="${doc}">
          <span class="doc-icon">📄</span>
          <div class="doc-title">${loaiVanBan} ${soHieu}</div>
          <div class="doc-content">${shortContent}</div>
        </div>
      `);
      docElement.on('click', function (e) {
        e.stopPropagation();
        const fullContent = $(this).data('full-content');
        openFullscreenDocument(fullContent);
      });
      documentsWrapper.append(docElement);
    }
  });
  overlay.find('.references-modal-close').on('click', function () { overlay.remove(); });
  overlay.on('click', function (e) { if ($(e.target).is('.references-modal-overlay')) overlay.remove(); });
  $('body').append(overlay);
}

function openFullscreenDocument(content) {
  const parts = content.split('<=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=>');
  let metadata = (parts[0] || '').replace(/\n/g, "<br>");
  let mainContent = (parts[1] || '').replace(/\n/g, "<br>").replace(/(\d+\.\s)/g, '<br>$1').replace(/^<br>/, "");
  const formatted = metadata + '<br><b><=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=></b><br>' + mainContent;
  const overlay = $(`
    <div class="fullscreen-overlay">
      <div class="fullscreen-document">
        <div class="document-content">${formatted}</div>
      </div>
    </div>
  `);
  overlay.on('click', function (e) { if ($(e.target).is('.fullscreen-overlay')) overlay.remove(); });
  $('body').append(overlay);
}

// ===== Sessions =====
function startNewSession() {
  $.ajax({
    url: 'http://127.0.0.1:8000/api/session/start-session',
    type: 'POST',
    contentType: 'application/json',
    success: function (response) {
      currentSessionId = response.session_id;
      localStorage.setItem('session_id', currentSessionId);

      if ($chatOutput.length) {
        $chatOutput.empty();
        $('#relevant-documents-container').empty();
        $chatOutput.append(`
          <div class="chat-message bot">
            <div class="avatar bot-avatar" style="background-image: url('https://media.istockphoto.com/id/1333838449/vector/chatbot-icon-support-bot-cute-smiling-robot-with-headset-the-symbol-of-an-instant-response.jpg?s=612x612&w=0&k=20&c=sJ_uGp9wJ5SRsFYKPwb-dWQqkskfs7Fz5vCs2w5w950=');"></div>
            <div class="message">Xin chào Bạn, Tôi là một trợ lý chuyên hỗ trợ về pháp luật Việt Nam. Bạn có câu hỏi gì xin đừng ngần ngại hỏi Tôi nhé!</div>
          </div>
        `);
      }

      isSearchWebMode = false;
      if ($toggleSearchWeb.length) {
        $toggleSearchWeb.removeClass('active').find('span').text('Chat');
      }
      enableInput(true, 'Nhập tin nhắn ...');
      updateSearchWebButtonState();
      loadChatSessions();
      // Clear Chat: nếu có nút thì tắt
      if ($clearChatButton.length) {
        $clearChatButton.removeClass('active').addClass('disabled').prop('disabled', true);
      }
    },
    error: function () {
      alert("Error: Unable to start new session.");
    }
  });
}

// new chat click: hỗ trợ cả HTML mới lẫn cũ
if ($newChatBtn.length) {
  $newChatBtn.on('click', function (event) {
    event.preventDefault();
    if (confirm("Bạn có chắc chắn muốn bắt đầu một phiên trò chuyện mới?")) {
      localStorage.removeItem('session_id');
      startNewSession();
    }
  });
}

function saveMessage(sessionId, sender, message, references = null) {
  if (references === "") references = [];
  $.ajax({
    url: 'http://127.0.0.1:8000/api/session/save-message',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ session_id: sessionId, sender, message, references }),
    success: function (response) { console.log("Message saved:", response); },
    error: function (xhr) { console.error("Error saving message:", xhr.responseText); }
  });
}

function loadChatSessions() {
  $.ajax({
    url: 'http://127.0.0.1:8000/api/session/get-sessions',
    type: 'GET',
    contentType: 'application/json',
    success: function (response) {
      const sessions = response.sessions;
      const $chatSessions = $('#chat-sessions');
      if (!$chatSessions.length) return;
      $chatSessions.empty();

      sessions.forEach(session => {
        const firstMessage = session.first_message || "No message yet";
        const truncatedMessage = firstMessage.length > 30 ? firstMessage.substring(0, 30) + "..." : firstMessage;

        const sessionElement = $(`
          <div class="chat-session" data-session-id="${session.id}">
            <div class="chat-session-content">${truncatedMessage}</div>
            <div class="session-menu-trigger">⋯</div>
            <div class="session-menu">
              <div class="session-menu-item delete-session">
                <svg class="delete-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24"><path fill="#d00" d="M9 3a3 3 0 0 1 6 0h5a1 1 0 1 1 0 2h-1v15a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V5H4a1 1 0 1 1 0-2h5Zm8 2H7v15a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V5Zm-5 3a1 1 0 0 1 1 1v8a1 1 0 1 1-2 0V9a1 1 0 0 1 1-1Zm4 1a1 1 0 0 1 2 0v8a1 1 0 1 1-2 0V9Zm-8 0a1 1 0 0 1 2 0v8a1 1 0 1 1-2 0V9Z"/></svg>
                Delete
              </div>
            </div>
          </div>
        `);

        sessionElement.on('click', function (e) {
          if ($(e.target).hasClass('session-menu-trigger') || $(e.target).closest('.session-menu').length) return;
          loadChatHistory(session.id);
        });

        sessionElement.find('.session-menu-trigger').on('click', function (e) {
          e.stopPropagation();
          const $menu = $(this).siblings('.session-menu');
          if ($menu.is(':visible')) { $menu.hide(); }
          else { $('.session-menu').hide(); $menu.show(); }
        });

        $(document).on('click', function () { $('.session-menu').hide(); });

        sessionElement.find('.delete-session').on('click', function (e) {
          e.stopPropagation();
          if (confirm('Bạn có chắc chắn muốn xóa phiên chat này?')) {
            const sessionId = session.id;
            deleteChatSession(sessionId);
            sessionElement.remove();
          }
        });

        $chatSessions.append(sessionElement);
      });
    },
    error: function () { console.error("Error fetching chat sessions"); }
  });
}

// Khi load trang nếu muốn chặn nhập trước khi có session, dùng đoạn sau.
// Ở HTML mới mình cho phép nhập luôn nếu chưa có session_id, nên comment lại.
// $(document).ready(function() {
//   enableInput(false, 'Click "Biểu tượng bút" để bắt đầu một phiên trò chuyện mới!');
// });

function updateClearChatButtonState() {
  if (!$clearChatButton.length || !$chatOutput.length) return;
  const userMessagesExist = $chatOutput.find('.chat-message.user').length > 0;
  if (userMessagesExist) {
    $clearChatButton.removeClass('disabled').addClass('active').prop('disabled', false);
  } else {
    $clearChatButton.removeClass('active').addClass('disabled').prop('disabled', true);
  }
}

$('.chat-session').on('click', function () { updateClearChatButtonState(); });

function loadMessageReferences(messageId) {
  $('.chat-message.bot').removeClass('selected');
  $(`.chat-message.bot[data-message-id="${messageId}"]`).addClass('selected');

  $.ajax({
    url: `http://127.0.0.1:8000/api/session/get-message-references/${messageId}`,
    type: 'GET',
    contentType: 'application/json',
    success: function (response) {
      if (response.references && response.references.length > 0) {
        displayRelevantDocuments(response.references);
      } else {
        $('#relevant-documents-container').empty();
      }
    },
    error: function () { console.error("Error loading message references."); }
  });
}

function loadChatHistory(sessionId) {
  console.log("Loading chat history for session ID:", sessionId);
  $('#relevant-documents-container').empty();
  $('.chat-session').removeClass('selected');
  $('.chat-message.bot').removeClass('selected');
  $(`.chat-session[data-session-id="${sessionId}"]`).addClass('selected');

  $.ajax({
    url: `http://127.0.0.1:8000/api/session/get-chat-history/${sessionId}`,
    type: 'GET',
    contentType: 'application/json',
    success: function (response) {
      const chatHistory = response.chat_history;
      if ($chatOutput.length) $chatOutput.empty();

      chatHistory.forEach(chat => {
        const isBot = chat.sender === 'bot';
        let formattedMessage = chat.message
          .replace(/\\n\\n/g, "<br><br>")
          .replace(/\\n/g, "<br>")
          .replace(/\n\n/g, "<br><br>")
          .replace(/\n/g, "<br>")
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        const messageHtml = `
          <div class="chat-message ${isBot ? 'bot' : 'user'}" data-message-id="${chat.id}">
            <div class="avatar ${isBot ? 'bot-avatar' : 'user-avatar'}" 
                 style="background-image: url('${isBot ? 'https://media.istockphoto.com/id/1333838449/vector/chatbot-icon-support-bot-cute-smiling-robot-with-headset-the-symbol-of-an-instant-response.jpg?s=612x612&w=0&k=20&c=sJ_uGp9wJ5SRsFYKPwb-dWQqkskfs7Fz5vCs2w5w950=' : 'https://media.istockphoto.com/id/1300845620/vector/user-icon-flat-isolated-on-white-background-user-symbol-vector-illustration.jpg?s=612x612&w=0&k=20&c=yBeyba0hUkh14_jgv1OKqIH0CCSWU_4ckRkAoy2p73o='}');">
            </div>
            <div class="message">${formattedMessage}</div>
          </div>
        `;
        if ($chatOutput.length) $chatOutput.append(messageHtml);
      });

      $('.chat-message.bot').on('click', function () {
        const messageId = $(this).data('message-id');
        loadMessageReferences(messageId);
      });

      enableInput(true, 'Nhập tin nhắn ...');

      updateClearChatButtonState();
      currentSessionId = sessionId;
      localStorage.setItem('session_id', sessionId);
      updateSearchWebButtonState();
    },
    error: function () { console.error("Error loading chat history."); }
  });
}

function addChatSessionToSidebar(sessionId, firstMessage) {
  const $chatSessions = $('#chat-sessions');
  if (!$chatSessions.length) return;
  const truncatedMessage = firstMessage.length > 30 ? firstMessage.substring(0, 30) + "..." : firstMessage;

  const sessionElement = $(`
    <div class="chat-session" data-session-id="${sessionId}">
      <div class="chat-session-content">${truncatedMessage}</div>
    </div>
  `);

  sessionElement.on('click', function () { loadChatHistory(sessionId); });
  $chatSessions.prepend(sessionElement);
}

if ($clearChatButton.length) {
  $clearChatButton.on('click', function () {
    if (confirm("Bạn có chắc chắn muốn xóa phiên Chat này?")) {
      clearChatHistory();
      enableInput(false, 'Click "Đoạn Chat Mới" để bắt đầu một phiên trò chuyện mới!');
      deleteChatSession(currentSessionId);
    }
  });
}

function clearChatHistory() {
  if ($chatOutput.length) $chatOutput.empty();
  $('#relevant-documents-container').empty();
  updateClearChatButtonState();
}

function deleteChatSession(sessionId) {
  $.ajax({
    url: `http://127.0.0.1:8000/api/session/delete-session/${sessionId}`,
    type: 'DELETE',
    contentType: 'application/json',
    success: function () {
      loadChatSessions();
      if (currentSessionId === sessionId) {
        if ($chatOutput.length) $chatOutput.empty();
        $('#relevant-documents-container').empty();
        enableInput(false, 'Click "Đoạn Chat Mới" để bắt đầu một phiên trò chuyện mới!');
        if ($sendButton.length) $sendButton.prop('disabled', true).removeClass('active').addClass('disabled');
      }
    },
    error: function () { console.error("Error deleting session."); }
  });
}

// Nút nổi xem trích dẫn (giữ để tương thích nếu bạn gọi elsewhere)
function showReferencesButton(documents) {
  $('#show-references-btn').remove();
  if (!documents || documents.length === 0) return;
  const btn = $(`
    <button id="show-references-btn" class="highlight" title="Xem trích dẫn tham khảo">
      📑 Trích dẫn <span class="badge">${documents.length}</span>
    </button>
  `);
  $('body').append(btn);
  setTimeout(() => btn.removeClass('highlight'), 2000);
  btn.on('click', function () { showReferencesOverlay(documents); });
}

function showReferencesOverlay(documents) {
  $('.references-overlay').remove();
  const overlay = $(`
    <div class="references-overlay">
      <div class="references-popup">
        <div class="references-popup-title">📑 Trích dẫn tham khảo (${documents.length})</div>
        <button class="references-popup-close" title="Đóng">×</button>
        <div class="documents-wrapper"></div>
      </div>
    </div>
  `);
  const documentsWrapper = overlay.find('.documents-wrapper');
  documents.forEach((doc) => {
    if (typeof doc === 'string' && doc.startsWith('http')) {
      documentsWrapper.append(`
        <div class="relevant-document">
          <span class="doc-icon">🔗</span>
          <div class="doc-title">Link tham khảo</div>
          <div class="doc-content"><a href="${doc}" target="_blank" rel="noopener noreferrer">${doc}</a></div>
        </div>
      `);
      return;
    }
    const parts = doc.split('<=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=>');
    if (parts.length > 1) {
      const contentPart = parts[1].trim();
      const metadataPart = parts[0].trim();
      const loaiVanBanMatch = metadataPart.match(/Loại văn bản: (.*)/);
      const soHieuMatch = metadataPart.match(/Số hiệu: (.*)/);
      const loaiVanBan = loaiVanBanMatch ? loaiVanBanMatch[1] : "N/A";
      const soHieu = soHieuMatch ? soHieuMatch[1] : "N/A";
      const shortContent = contentPart.length > 40 ? contentPart.substring(0, 40) + '...' : contentPart;
      const docElement = $(`
        <div class="relevant-document" data-full-content="${doc}">
          <span class="doc-icon">📄</span>
          <div class="doc-title">${loaiVanBan} ${soHieu}</div>
          <div class="doc-content">${shortContent}</div>
        </div>
      `);
      docElement.on('click', function (e) {
        e.stopPropagation();
        const fullContent = $(this).data('full-content');
        openFullscreenDocument(fullContent);
      });
      documentsWrapper.append(docElement);
    }
  });
  overlay.find('.references-popup-close').on('click', function () { overlay.remove(); });
  overlay.on('click', function (e) { if ($(e.target).is('.references-overlay')) overlay.remove(); });
  $('body').append(overlay);
}
