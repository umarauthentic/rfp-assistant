let lastQuery = "";
let lastAnswer = "";
let memoryData = [];
let history = [];

document.addEventListener("DOMContentLoaded", function () {
    loadMemory();

    const textarea = document.getElementById("query");

    textarea.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            ask();
        }
    });

    textarea.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = this.scrollHeight + "px";
    });
});

function escapeHtml(value) {
    if (!value) return "";

    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function loadMemory() {
    try {
        const response = await fetch("/memory/list");
        const data = await response.json();

        memoryData = data.items || [];
        renderMemory(memoryData);

    } catch (error) {
        console.error("Failed to load memory:", error);
        document.getElementById("memoryList").innerHTML =
            "<div class='memory-item'>Could not load saved answers.</div>";
    }
}

function renderMemory(items) {
    const memoryList = document.getElementById("memoryList");
    memoryList.innerHTML = "";

    if (!items || items.length === 0) {
        memoryList.innerHTML =
            "<div class='memory-item'>No saved answers yet.</div>";
        return;
    }

    items.forEach((item, index) => {
        const question = item.question || "";
        const answer = item.answer || "";

        const div = document.createElement("div");
        div.className = "memory-item";
        div.onclick = function () {
            useMemory(index);
        };

        div.innerHTML = `
            <div class="memory-question">${escapeHtml(question)}</div>
            <div class="memory-answer">${escapeHtml(answer.substring(0, 120))}...</div>
        `;

        memoryList.appendChild(div);
    });
}

function filterMemory() {
    const q = document.getElementById("search").value.toLowerCase();

    const filtered = memoryData.filter(item =>
        (item.question || "").toLowerCase().includes(q) ||
        (item.answer || "").toLowerCase().includes(q)
    );

    renderMemory(filtered);
}

function useMemory(index) {
    const item = memoryData[index];

    if (!item) return;

    lastQuery = item.question || "";
    lastAnswer = item.answer || "";

    document.getElementById("badge").innerHTML = "♻ Reused from memory";
    document.getElementById("answerText").innerHTML = escapeHtml(lastAnswer);
    document.getElementById("editBox").value = lastAnswer;
    document.getElementById("source").innerHTML = "Source: Memory";
    document.getElementById("result").classList.remove("hidden");
}

async function ask() {
    const query = document.getElementById("query").value.trim();

    if (!query) {
        alert("Please enter a question.");
        return;
    }

    lastQuery = query;

    document.getElementById("loader").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: query,
                use_memory: true,
                use_documents: true
            })
        });

        const data = await response.json();

        lastAnswer = data.answer || "";

        const badge = data.from_memory
            ? "♻ Reused from memory"
            : "📄 From documents";

        document.getElementById("badge").innerHTML = badge;
        document.getElementById("answerText").innerHTML = escapeHtml(lastAnswer);
        document.getElementById("editBox").value = lastAnswer;

        document.getElementById("source").innerHTML =
            data.from_memory ? "Source: Memory" : "Source: Documents";

        document.getElementById("result").classList.remove("hidden");

        updateHistory(query, lastAnswer);

    } catch (error) {
        console.error(error);
        document.getElementById("badge").innerHTML = "Error";
        document.getElementById("answerText").innerHTML =
            "Could not connect to backend.";
        document.getElementById("result").classList.remove("hidden");
    }

    document.getElementById("loader").classList.add("hidden");
}

async function save() {
    if (!lastQuery || !lastAnswer) {
        alert("No answer to save.");
        return;
    }

    try {
        const response = await fetch("/memory/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: lastQuery,
                answer: lastAnswer,
                tags: ["manual"],
                approved: true,
                source_docs: []
            })
        });

        const data = await response.json();

        if (!data.success) {
            alert("Save failed.");
            return;
        }

        alert("Saved answer.");
        await loadMemory();

    } catch (error) {
        console.error(error);
        alert("Save failed.");
    }
}

function copyAnswer() {
    if (!lastAnswer) return;

    navigator.clipboard.writeText(lastAnswer);
    alert("Copied.");
}

function toggleEdit() {
    const editBox = document.getElementById("editBox");
    const answerText = document.getElementById("answerText");

    if (editBox.classList.contains("hidden")) {
        editBox.classList.remove("hidden");
        answerText.classList.add("hidden");
        editBox.value = lastAnswer;
    } else {
        editBox.classList.add("hidden");
        answerText.classList.remove("hidden");

        lastAnswer = editBox.value;
        answerText.innerHTML = escapeHtml(lastAnswer);
    }
}

function updateHistory(query, answer) {
    history.unshift({
        query,
        answer
    });

    const html = history.map(item => `
        <div>
            <b>Q:</b> ${escapeHtml(item.query)}<br>
            <b>A:</b> ${escapeHtml(item.answer)}
        </div>
        <hr>
    `).join("");

    document.getElementById("history").innerHTML = html;
}