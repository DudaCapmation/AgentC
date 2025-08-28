const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const panelToggle = document.getElementById('panel-toggle');
const sidePanel = document.getElementById('side-panel');
const errorBanner = document.getElementById('error-banner');
const typingIndicator = document.getElementById('typing-indicator');

let activeEventSource = null;

// Init
window.onload = () => {
  clearChatWindow();
  showEmptySlate();
  // side panel initially visible on desktop
  if (sidePanel) sidePanel.style.display = 'block';
};

// Utilities
function clearChatWindow() {
  chatWindow.innerHTML = '';
}

function showEmptySlate() {
  clearChatWindow();
  const el = document.createElement('div');
  el.className = 'empty-slate';
  el.textContent = "Welcome — start by typing a question, using any tool or just talking to the assistant!";
  chatWindow.appendChild(el);
}

function appendMessage(text, role) {
  // If empty slate present, remove it
  const slate = chatWindow.querySelector('.empty-slate');
  if (slate) slate.remove();

  const msgDiv = document.createElement('div');
  msgDiv.className = 'message ' + role;
  msgDiv.textContent = text;
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showErrorBanner(msg) {
  if (!errorBanner) return;
  errorBanner.textContent = msg;
  errorBanner.classList.remove('hidden');
}

function hideErrorBanner() {
  if (!errorBanner) return;
  errorBanner.classList.add('hidden');
  errorBanner.textContent = '';
}

function setStreamingActive(active, msgDiv) {
  if (active) {
    // show typing indicator (above input)
    typingIndicator.classList.remove('hidden');

    // ensure empty slate removed
    const slate = chatWindow.querySelector('.empty-slate');
    if (slate) slate.remove();

    if (msgDiv) {
      // append stream dots if not present
      if (!msgDiv.querySelector('.stream-dots')) {
        const dots = document.createElement('span');
        dots.className = 'stream-dots';
        dots.textContent = ' •••';
        msgDiv.appendChild(dots);
      }
    }
  } else {
    typingIndicator.classList.add('hidden');
    document.querySelectorAll('.stream-dots').forEach(el => el.remove());
  }
}

// SSE streaming send function (plain text)
async function sendMessageSSE(reset = false) {
  const text = userInput.value.trim();
  if (!text && !reset) return;

  // If reset flag triggered by caller, we still POST reset (but do not stream)
  if (reset) {
    // backend reset endpoint: POST /chat/ with reset true
    try {
      await fetch('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: "", reset: true }),
      });
    } catch (err) {
      console.error("Reset error", err);
    }
    // Clear UI and show empty slate
    clearChatWindow();
    showEmptySlate();
    hideErrorBanner();
    userInput.value = '';
    userInput.focus();
    return;
  }

  // append user message
  appendMessage(text, 'user');

  // Prepare assistant bubble (starts empty with dots appended by setStreamingActive)
  const msgDiv = document.createElement('div');
  msgDiv.className = 'message assistant';
  msgDiv.textContent = ''; // plain text content will be inserted
  chatWindow.appendChild(msgDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  // Build query params and encode them
  const params = new URLSearchParams({
    user_input: text,
    reset: "false"
  });
  const url = `/stream-chat/?${params.toString()}`;

  // If active ES, close it
  if (activeEventSource) {
    try { activeEventSource.close(); } catch (_) {}
    activeEventSource = null;
  }

  // Open EventSource
  const es = new EventSource(url);
  activeEventSource = es;

  setStreamingActive(true, msgDiv);
  hideErrorBanner();

  es.onopen = () => {
    hideErrorBanner();
  };

  es.onmessage = (e) => {
    // end sentinel
    if (e.data === "[DONE]" || e.data === "[END]") {
      try { es.close(); } catch (err) {}
      setStreamingActive(false, msgDiv);
      activeEventSource = null;
      return;
    }

    // Append incoming chunk as plain text BEFORE dots (so dots stay at end)
    const dots = msgDiv.querySelector('.stream-dots');
    if (dots) {
      const node = document.createTextNode(e.data);
      msgDiv.insertBefore(node, dots);
    } else {
      msgDiv.textContent += e.data;
    }
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  es.onerror = (err) => {
    try {
      if (es.readyState !== EventSource.CLOSED) {
        console.error("EventSource error:", err);
        showErrorBanner("Stream error: connection interrupted.");
        msgDiv.textContent += "\n\n[Stream interrupted — check console]";
      }
    } catch (e) {
      msgDiv.textContent += "\n\n[Stream interrupted — check console]";
    } finally {
      try { es.close(); } catch (_) {}
      setStreamingActive(false, msgDiv);
      activeEventSource = null;
    }
  };

  // Clear input & disable controls while streaming
  userInput.value = '';
  userInput.disabled = true;
  sendBtn.disabled = true;

  // Re-enable UI when EventSource closes
  const checkClosed = setInterval(() => {
    if (!es || es.readyState === EventSource.CLOSED) {
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.focus();
      clearInterval(checkClosed);
    }
  }, 200);
}

// Event bindings
sendBtn.addEventListener('click', () => sendMessageSSE());
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessageSSE();
  }
});

// Clear chat button: POST reset to backend; DO NOT stream
clearBtn.addEventListener('click', async () => {
  try {
    // backend will clear conversation state when reset is true
    await fetch('/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: "", reset: true }),
    });
  } catch (err) {
    console.error("Clear request failed", err);
    showErrorBanner("Could not reset conversation (network).");
  }
  // Reset UI
  if (activeEventSource) {
    try { activeEventSource.close(); } catch (_) {}
    activeEventSource = null;
  }
  setStreamingActive(false);
  clearChatWindow();
  showEmptySlate();
  userInput.value = '';
  userInput.focus();
  hideErrorBanner();
});

// Panel toggle — show/hide the fixed left side panel
panelToggle.addEventListener('click', () => {
  if (!sidePanel) return;
  if (sidePanel.style.display === 'none' || getComputedStyle(sidePanel).display === 'none') {
    sidePanel.style.display = 'block';
  } else {
    sidePanel.style.display = 'none';
  }
});

// Accessibility: focus input on page load
userInput.focus();