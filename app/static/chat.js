let activeConversationId = null;
let conversations = [];
let sending = false;

document.addEventListener("DOMContentLoaded", async function () {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendMessage();
    });
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    input.addEventListener("input", resizeComposer);

    await loadConversations();
    if (conversations.length) {
        await selectConversation(conversations[0].id);
    }
});

async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
    if (response.status === 401) {
        window.location.href = "/login";
        throw new Error("Your session has expired.");
    }
    if (!response.ok) {
        let message = "The request could not be completed.";
        try {
            const body = await response.json();
            message = body.detail || message;
        } catch (_) {}
        throw new Error(message);
    }
    return response.json();
}

async function loadConversations() {
    const data = await apiFetch("/api/chat/conversations");
    conversations = data.conversations;
    renderConversationList();
}

function renderConversationList() {
    const list = document.getElementById("conversationList");
    list.replaceChildren();
    if (!conversations.length) {
        const hint = document.createElement("p");
        hint.className = "conversation-hint";
        hint.textContent = "Your conversations will appear here.";
        list.appendChild(hint);
        return;
    }

    conversations.forEach(function (conversation) {
        const row = document.createElement("div");
        row.className = `conversation-row${conversation.id === activeConversationId ? " active" : ""}`;

        const button = document.createElement("button");
        button.type = "button";
        button.className = "conversation-button";
        button.textContent = conversation.title;
        button.title = conversation.title;
        button.onclick = () => selectConversation(conversation.id);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "delete-chat-button";
        remove.textContent = "×";
        remove.title = "Delete conversation";
        remove.onclick = (event) => deleteConversation(event, conversation.id);

        row.append(button, remove);
        list.appendChild(row);
    });
}

async function createConversation() {
    if (sending) return;
    const data = await apiFetch("/api/chat/conversations", {
        method: "POST",
        body: JSON.stringify({ title: "New chat" })
    });
    activeConversationId = data.conversation.id;
    await loadConversations();
    renderConversation(data.conversation);
    closeSidebarOnMobile();
    document.getElementById("chatInput").focus();
}

async function selectConversation(conversationId) {
    if (sending) return;
    const data = await apiFetch(`/api/chat/conversations/${conversationId}`);
    activeConversationId = conversationId;
    renderConversation(data.conversation);
    renderConversationList();
    closeSidebarOnMobile();
}

async function deleteConversation(event, conversationId) {
    event.stopPropagation();
    if (!window.confirm("Delete this conversation?")) return;
    await apiFetch(`/api/chat/conversations/${conversationId}`, { method: "DELETE" });
    if (activeConversationId === conversationId) activeConversationId = null;
    await loadConversations();
    if (conversations.length) {
        await selectConversation(conversations[0].id);
    } else {
        renderConversation({ title: "New chat", messages: [] });
    }
}

function renderConversation(conversation) {
    document.getElementById("conversationTitle").textContent = conversation.title || "New chat";
    const container = document.getElementById("messages");
    container.replaceChildren();
    const messages = conversation.messages || [];
    document.getElementById("chatEmpty").classList.toggle("hidden", messages.length > 0);
    messages.forEach(message => container.appendChild(buildMessage(message)));
    scrollToBottom();
}

function buildMessage(message) {
    const article = document.createElement("article");
    article.className = `chat-message ${message.role}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = message.role === "user" ? "You" : "RFP";

    const body = document.createElement("div");
    body.className = "message-body";
    const label = document.createElement("strong");
    label.textContent = message.role === "user" ? "You" : "RFP Assistant";
    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message.content;
    body.append(label, content);

    if (message.role === "assistant" && message.sources?.length) {
        const sources = document.createElement("div");
        sources.className = "message-sources";
        const sourceLabel = document.createElement("span");
        sourceLabel.textContent = "Sources";
        sources.appendChild(sourceLabel);
        message.sources.forEach(function (source) {
            const chip = document.createElement("span");
            chip.className = "source-chip";
            chip.textContent = source.label;
            sources.appendChild(chip);
        });
        body.appendChild(sources);
    }

    article.append(avatar, body);
    return article;
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const question = input.value.trim();
    if (!question || sending) return;
    if (!activeConversationId) await createConversation();

    sending = true;
    setComposerState(true);
    document.getElementById("chatEmpty").classList.add("hidden");
    const container = document.getElementById("messages");
    container.appendChild(buildMessage({ role: "user", content: question }));
    container.appendChild(buildTypingMessage());
    input.value = "";
    resizeComposer();
    scrollToBottom();

    try {
        const data = await apiFetch(`/api/chat/conversations/${activeConversationId}/messages`, {
            method: "POST",
            body: JSON.stringify({ message: question })
        });
        renderConversation(data.conversation);
        await loadConversations();
    } catch (error) {
        document.getElementById("typingMessage")?.remove();
        container.appendChild(buildMessage({ role: "assistant", content: error.message }));
    } finally {
        sending = false;
        setComposerState(false);
        input.focus();
    }
}

function buildTypingMessage() {
    const message = buildMessage({ role: "assistant", content: "" });
    message.id = "typingMessage";
    const content = message.querySelector(".message-content");
    content.className += " typing-dots";
    content.innerHTML = "<span></span><span></span><span></span>";
    return message;
}

function setComposerState(disabled) {
    document.getElementById("chatInput").disabled = disabled;
    document.getElementById("sendButton").disabled = disabled;
}

function useSuggestion(button) {
    const input = document.getElementById("chatInput");
    input.value = button.textContent;
    input.focus();
    resizeComposer();
}

function resizeComposer() {
    const input = document.getElementById("chatInput");
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

function scrollToBottom() {
    const scroll = document.getElementById("messageScroll");
    requestAnimationFrame(() => { scroll.scrollTop = scroll.scrollHeight; });
}

function toggleSidebar() {
    document.getElementById("chatSidebar").classList.toggle("open");
}

function closeSidebarOnMobile() {
    if (window.innerWidth <= 760) document.getElementById("chatSidebar").classList.remove("open");
}
