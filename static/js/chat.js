const Chat = (() => {
  let _isOpen = false;
  let _conversationId = null;
  let _isStreaming = false;

  let _root = null;
  let _widget = null;
  let _toggle = null;
  let _messagesEl = null;
  let _input = null;
  let _sendBtn = null;

  function _buildDOM() {
    _root = document.getElementById('chat-root');
    if (!_root) return false;

    _toggle = document.createElement('button');
    _toggle.className = 'chat-toggle';
    _toggle.setAttribute('aria-label', 'Открыть чат с ассистентом');
    _toggle.innerHTML = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H6l-2 2V4h16v10z"/>
    </svg>`;
    document.body.appendChild(_toggle);

    _widget = document.createElement('div');
    _widget.className = 'chat-widget hidden';
    _widget.innerHTML = `
      <div class="chat-header">
        <span class="chat-header__title">🍹 AI-бармен</span>
        <button class="chat-header__btn" id="chat-clear-btn">Очистить</button>
        <button class="chat-header__close" id="chat-close-btn" aria-label="Закрыть">×</button>
      </div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-input-area">
        <textarea
          class="chat-input"
          id="chat-input"
          placeholder="Спросите про коктейли…"
          rows="1"
          maxlength="2000"
        ></textarea>
        <button class="chat-send" id="chat-send-btn">Отправить</button>
      </div>
    `;
    _root.appendChild(_widget);

    _messagesEl = document.getElementById('chat-messages');
    _input = document.getElementById('chat-input');
    _sendBtn = document.getElementById('chat-send-btn');

    _toggle.addEventListener('click', toggle);
    document.getElementById('chat-close-btn').addEventListener('click', () => {
      _isOpen = true;
      toggle();
    });
    document.getElementById('chat-clear-btn').addEventListener('click', clearHistory);
    _sendBtn.addEventListener('click', _onSend);
    _input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        _onSend();
      }
    });
    _input.addEventListener('input', _autoResize);
    return true;
  }

  function _autoResize() {
    _input.style.height = 'auto';
    _input.style.height = Math.min(_input.scrollHeight, 100) + 'px';
  }

  function _onSend() {
    const text = _input.value.trim();
    if (!text || _isStreaming) return;
    sendMessage(text);
  }

  function _addMessage(role, content) {
    const el = document.createElement('div');
    el.className = `message ${role}`;
    el.textContent = content;
    _messagesEl.appendChild(el);
    _scrollBottom();
    return el;
  }

  function _appendToBubble(el, chunk) {
    el.textContent += chunk;
    _scrollBottom();
  }

  function _showTyping() {
    const el = document.createElement('div');
    el.className = 'typing-indicator';
    el.id = 'typing-indicator';
    el.innerHTML = '<span></span><span></span><span></span>';
    _messagesEl.appendChild(el);
    _scrollBottom();
  }

  function _removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  function _scrollBottom() {
    _messagesEl.scrollTop = _messagesEl.scrollHeight;
  }

  function _setStreaming(val) {
    _isStreaming = val;
    _input.disabled = val;
    _sendBtn.disabled = val;
  }

  async function init() {
    if (!Auth.isLoggedIn()) return;
    if (!_buildDOM()) return;
    await loadHistory();
  }

  function destroy() {
    if (_toggle) { _toggle.remove(); _toggle = null; }
    if (_widget) { _widget.remove(); _widget = null; }
    _isOpen = false;
    _conversationId = null;
    _isStreaming = false;
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/assistant/history', { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      _conversationId = data.conversation_id;
      if (data.messages && data.messages.length > 0) {
        _messagesEl.innerHTML = '';
        for (const msg of data.messages) {
          _addMessage(msg.role, msg.content);
        }
      }
    } catch { /* ignore */ }
  }

  async function sendMessage(text) {
    _input.value = '';
    _input.style.height = 'auto';
    _addMessage('user', text);
    _showTyping();
    _setStreaming(true);

    const bubble = document.createElement('div');
    bubble.className = 'message assistant';
    bubble.textContent = '';

    try {
      const response = await fetch('/api/assistant/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        _removeTyping();
        const errData = await response.json().catch(() => ({}));
        _addMessage('error', `Ошибка: ${errData.detail || response.status}`);
        _setStreaming(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let bubbleAdded = false;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split('\n\n');
        buffer = events.pop();

        for (const event of events) {
          if (!event.startsWith('data: ')) continue;
          let data;
          try { data = JSON.parse(event.slice(6)); } catch { continue; }

          if (data.conversation_id) {
            _conversationId = data.conversation_id;
          }
          if (data.chunk) {
            if (!bubbleAdded) {
              _removeTyping();
              _messagesEl.appendChild(bubble);
              bubbleAdded = true;
            }
            _appendToBubble(bubble, data.chunk);
          }
          if (data.error) {
            _removeTyping();
            _addMessage('error', `Ошибка ассистента: ${data.error}`);
          }
          if (data.done) break;
        }
      }
      if (!bubbleAdded) _removeTyping();
    } catch (err) {
      _removeTyping();
      _addMessage('error', 'Не удалось связаться с ассистентом.');
    }

    _setStreaming(false);
  }

  async function clearHistory() {
    if (!confirm('Очистить историю диалога?')) return;
    try {
      await fetch('/api/assistant/history', {
        method: 'DELETE',
        credentials: 'include',
      });
    } catch { /* ignore */ }
    _messagesEl.innerHTML = '';
    _conversationId = null;
  }

  function toggle() {
    _isOpen = !_isOpen;
    if (_isOpen) {
      _widget.classList.remove('hidden');
      _input.focus();
      _scrollBottom();
    } else {
      _widget.classList.add('hidden');
    }
  }

  return { init, destroy, toggle, sendMessage, clearHistory, loadHistory };
})();
