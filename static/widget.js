(() => {
  const currentScript = document.currentScript;

  const endpoint =
    (currentScript && currentScript.dataset.chatEndpoint) ||
    "/chat";
  const title =
    (currentScript && currentScript.dataset.title) ||
    "Assistant";
  const subtitle =
    (currentScript && currentScript.dataset.subtitle) ||
    "Ask admission related queries";
  const primaryColor =
    (currentScript && currentScript.dataset.primaryColor) ||
    "#0b4a7a";
  const positionRight =
    (currentScript && currentScript.dataset.right) ||
    "20px";
  const positionBottom =
    (currentScript && currentScript.dataset.bottom) ||
    "20px";

  const style = document.createElement("style");
  style.textContent = `
    .ad-chat-widget {
      position: fixed;
      right: ${positionRight};
      bottom: ${positionBottom};
      z-index: 2147483647;
      font-family: Arial, sans-serif;
    }
    .ad-chat-toggle {
      width: 58px;
      height: 58px;
      border: none;
      border-radius: 50%;
      background: ${primaryColor};
      color: #fff;
      font-size: 24px;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }
    .ad-chat-wrapper {
      width: 360px;
      height: 520px;
      margin-bottom: 12px;
      background: #fff;
      display: none;
      flex-direction: column;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
      border: 1px solid #d9d9d9;
    }
    .ad-chat-wrapper.open {
      display: flex;
    }
    .ad-chat-header {
      background: ${primaryColor};
      color: #fff;
      padding: 15px;
      text-align: center;
    }
    .ad-chat-header h2 {
      margin: 0;
      font-size: 18px;
    }
    .ad-chat-header p {
      margin: 5px 0 0;
      font-size: 12px;
    }
    .ad-chatbox {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      background: #e5ddd5;
      display: flex;
      flex-direction: column;
    }
    .ad-chat-message {
      margin: 8px 0;
      padding: 10px;
      border-radius: 8px;
      max-width: 75%;
      word-wrap: break-word;
      font-size: 14px;
      line-height: 1.35;
    }
    .ad-chat-user {
      background: #dcf8c6;
      align-self: flex-end;
      text-align: right;
    }
    .ad-chat-bot {
      background: #fff;
      align-self: flex-start;
    }
    .ad-chat-input-area {
      display: flex;
      padding: 10px;
      background: #f0f0f0;
    }
    .ad-chat-input {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 20px;
      outline: none;
    }
    .ad-chat-send {
      margin-left: 10px;
      padding: 10px 15px;
      border: none;
      background: ${primaryColor};
      color: #fff;
      border-radius: 20px;
      cursor: pointer;
    }
    .ad-chat-send:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
    @media (max-width: 480px) {
      .ad-chat-widget {
        right: 12px;
        bottom: 12px;
      }
      .ad-chat-wrapper {
        width: min(92vw, 360px);
        height: min(70vh, 520px);
      }
    }
  `;
  document.head.appendChild(style);

  const widget = document.createElement("div");
  widget.className = "ad-chat-widget";
  widget.innerHTML = `
    <div class="ad-chat-wrapper" id="adChatWrapper">
      <div class="ad-chat-header">
        <h2>${title}</h2>
        <p>${subtitle}</p>
      </div>
      <div class="ad-chatbox" id="adChatbox"></div>
      <div class="ad-chat-input-area">
        <input class="ad-chat-input" id="adChatInput" placeholder="Type your message..." />
        <button class="ad-chat-send" id="adChatSend">Send</button>
      </div>
    </div>
    <button class="ad-chat-toggle" id="adChatToggle" aria-label="Open chatbot">💬</button>
  `;
  document.body.appendChild(widget);

  const wrapper = widget.querySelector("#adChatWrapper");
  const toggleBtn = widget.querySelector("#adChatToggle");
  const chatbox = widget.querySelector("#adChatbox");
  const input = widget.querySelector("#adChatInput");
  const sendBtn = widget.querySelector("#adChatSend");
  let hasWelcomed = false;

  function addMessage(text, who) {
    const bubble = document.createElement("div");
    bubble.className = `ad-chat-message ${who === "user" ? "ad-chat-user" : "ad-chat-bot"}`;
    bubble.textContent = text;
    chatbox.appendChild(bubble);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function toggleChat() {
    wrapper.classList.toggle("open");
    const isOpen = wrapper.classList.contains("open");
    toggleBtn.textContent = isOpen ? "×" : "💬";
    toggleBtn.setAttribute("aria-label", isOpen ? "Close chatbot" : "Open chatbot");
    if (isOpen) {
      input.focus();
      if (!hasWelcomed) {
        addMessage("Hi! I can help you with admission-related questions.", "bot");
        hasWelcomed = true;
      }
    }
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";
    sendBtn.disabled = true;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      addMessage(data.response || "I could not generate a response.", "bot");
    } catch (error) {
      addMessage("Chatbot is unavailable right now. Please try again later.", "bot");
      console.error("Chat widget error:", error);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  toggleBtn.addEventListener("click", toggleChat);
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
})();
