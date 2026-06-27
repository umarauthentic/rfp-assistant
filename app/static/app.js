let lastQuery = "";
let lastAnswer = "";
let lastMatches = [];
let memoryData = [];
let history = [];
let rfpItems = [];

document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("memoryList")) {
        loadMemory();
    }

    const textarea = document.getElementById("query");
    if (!textarea) {
        return;
    }

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

function renderAnswer(value) {
    const text = value || "";
    const lines = text.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
    const listLines = lines.filter(line => /^[-*]\s+/.test(line) || /^\d+[.)]\s+/.test(line));
    const listItems = listLines
        .map(line => line.replace(/^[-*]\s+/, "").replace(/^\d+[.)]\s+/, "").trim())
        .filter(Boolean);

    if (listItems.length > 1 && listItems.length === lines.length) {
        return `<ul class="answer-list">${listItems.map(line => `<li>${escapeHtml(line)}</li>`).join("")}</ul>`;
    }

    return escapeHtml(text).replace(/\r?\n/g, "<br>");
}

function renderResponseTags(tags, matches) {
    const container = document.getElementById("responseTags");
    const preview = document.getElementById("tagPreview");

    container.innerHTML = "";
    preview.classList.add("hidden");
    preview.innerHTML = "";

    if (!tags || tags.length === 0) {
        return;
    }

    tags.forEach((tag, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "tag-chip";
        button.textContent = tag.label || tag.value || "Source";
        button.onclick = function () {
            showTagPreview(index, tag, matches);
        };
        container.appendChild(button);
    });
}

function extractAnswerFromSource(text) {
    const source = (text || "").trim();
    if (!source) return "";

    const labelPattern = "(answer|answers|response|responses|reply|vendor response|customer response|details|detail)";
    const labeledMatch = source.match(
        new RegExp(`(?:^|[\\n|])\\s*${labelPattern}\\s*:\\s*([\\s\\S]*?)(?=(?:[\\n|])\\s*[A-Za-z][A-Za-z\\s]{0,40}\\s*:|$)`, "i")
    );

    if (labeledMatch && labeledMatch[2]) {
        return labeledMatch[2].trim();
    }

    const cells = source
        .split(/\s+\|\s+/)
        .map(cell => cell.trim())
        .filter(Boolean)
        .filter(cell => !/^(sheet\s*:|row\s+\d+\b|unnamed\s*:)/i.test(cell));

    const answerCell = cells.find(cell => {
        const label = cell.split(":")[0].trim().toLowerCase();
        return /^(answer|answers|response|responses|reply|vendor response|customer response|details|detail)$/.test(label);
    });

    if (answerCell) {
        const parts = answerCell.split(":");
        return parts.slice(1).join(":").trim() || answerCell.trim();
    }

    if (cells.length >= 2) {
        const firstCell = cells[0].toLowerCase();
        const looksLikeQuestionRow =
            firstCell.includes("question") ||
            firstCell.includes("requirement") ||
            firstCell.includes("prompt") ||
            cells[0].endsWith("?");

        if (looksLikeQuestionRow) {
            return cells[cells.length - 1].replace(/^[A-Za-z][A-Za-z\s]{0,40}:\s*/, "").trim();
        }
    }

    return source;
}

function showTagPreview(index, tag, matches) {
    const preview = document.getElementById("tagPreview");
    const match = (matches || []).find(item => item.id === tag.match_id) || (matches || [])[index];
    const score = tag.score === null || tag.score === undefined
        ? ""
        : `Match score: ${Number(tag.score).toFixed(3)}\n\n`;
    const matchedText = match && match.text
        ? match.text
        : tag.value || "";
    const sourceText = tag.tag_type === "document"
        ? extractAnswerFromSource(matchedText)
        : matchedText;

    preview.innerHTML = `<strong>${escapeHtml(tag.label || "Source")}</strong><pre>${escapeHtml(score + sourceText)}</pre>`;
    preview.classList.remove("hidden");
}

function setRfpStatus(message) {
    const status = document.getElementById("rfpStatus");
    if (status) {
        status.textContent = message || "";
    }
}

function parseQuestionList(value) {
    return (value || "")
        .split(/\r?\n/)
        .map(line => line.replace(/^[-*]\s+/, "").replace(/^\d+[.)]\s+/, "").trim())
        .filter(Boolean);
}

function addQuestionsToBuilder(questions) {
    const existing = new Set(rfpItems.map(item => item.question.toLowerCase()));
    let added = 0;

    questions.forEach(question => {
        const cleaned = question.trim();
        const key = cleaned.toLowerCase();
        if (!cleaned || existing.has(key)) {
            return;
        }

        rfpItems.push({
            question: cleaned,
            answer: "",
            from_memory: false,
            status: "pending",
            error: "",
            references: []
        });
        existing.add(key);
        added += 1;
    });

    renderRfpItems();
    setRfpStatus(added ? `Added ${added} question${added === 1 ? "" : "s"}.` : "No new questions added.");
}

function addRfpQuestion() {
    const input = document.getElementById("rfpSingleQuestion");
    addQuestionsToBuilder([input.value]);
    input.value = "";
}

function addRfpQuestionList() {
    const input = document.getElementById("rfpQuestionList");
    addQuestionsToBuilder(parseQuestionList(input.value));
    input.value = "";
}

function renderRfpItems() {
    const container = document.getElementById("rfpItems");
    if (!container) return;

    if (!rfpItems.length) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = rfpItems.map((item, index) => `
        <div class="rfp-item">
            <div class="rfp-item-header">
                <div class="rfp-question">${index + 1}. ${escapeHtml(item.question)}</div>
                <div>
                    <span class="rfp-item-status">${escapeHtml(item.status || "pending")}</span>
                    <button class="secondary" type="button" onclick="removeRfpItem(${index})">Remove</button>
                </div>
            </div>
            <textarea class="rfp-answer" data-rfp-index="${index}" oninput="updateRfpAnswer(${index}, this.value)" placeholder="Generated answer will appear here...">${escapeHtml(item.answer || "")}</textarea>
            ${renderRfpReferences(item.references || [])}
            ${item.error ? `<div class="rfp-error">${escapeHtml(item.error)}</div>` : ""}
        </div>
    `).join("");
}

function renderRfpReferences(references) {
    if (!references || !references.length) {
        return "";
    }

    const html = references.map(ref => {
        const chunk = ref.chunk_index === null || ref.chunk_index === undefined
            ? ""
            : ` #${Number(ref.chunk_index) + 1}`;
        const score = ref.score === null || ref.score === undefined
            ? ""
            : ` (${Number(ref.score).toFixed(3)})`;
        return `<span class="rfp-reference">${escapeHtml((ref.source || "Document") + chunk + score)}</span>`;
    }).join("");

    return `<div class="rfp-references"><strong>References:</strong>${html}</div>`;
}

function updateRfpAnswer(index, value) {
    if (!rfpItems[index]) return;
    rfpItems[index].answer = value;
    rfpItems[index].status = value.trim() ? "edited" : "pending";
    rfpItems[index].error = "";
}

function removeRfpItem(index) {
    rfpItems.splice(index, 1);
    renderRfpItems();
    setRfpStatus(rfpItems.length ? `${rfpItems.length} question${rfpItems.length === 1 ? "" : "s"} ready.` : "");
}

function clearRfpBuilder() {
    rfpItems = [];
    renderRfpItems();
    setRfpStatus("");
}

async function loadTemplateQuestions() {
    setRfpStatus("Loading template questions...");

    try {
        const response = await fetch("/rfp/template/questions");
        const data = await response.json();
        addQuestionsToBuilder(data.questions || []);
    } catch (error) {
        console.error(error);
        setRfpStatus("Could not load template questions.");
    }
}

async function uploadRfpTemplate() {
    const input = document.getElementById("rfpTemplateFile");
    const file = input && input.files ? input.files[0] : null;

    if (!file) {
        alert("Choose a .docx RFP template first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setRfpStatus("Uploading RFP template...");

    try {
        const response = await fetch("/rfp/template/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Template upload failed.");
        }

        const data = await response.json();
        addQuestionsToBuilder(data.questions || []);
        setRfpStatus(`Uploaded ${file.name}. Loaded ${data.questions ? data.questions.length : 0} template questions.`);
        input.value = "";
    } catch (error) {
        console.error(error);
        setRfpStatus("Could not upload RFP template.");
    }
}

function syncRfpAnswersFromDom() {
    document.querySelectorAll("[data-rfp-index]").forEach(element => {
        const index = Number(element.getAttribute("data-rfp-index"));
        if (Number.isInteger(index) && rfpItems[index]) {
            rfpItems[index].answer = element.value;
        }
    });
}

function wait(ms) {
    return new Promise(resolve => {
        window.setTimeout(resolve, ms);
    });
}

async function waitWithCountdown(seconds, index, attempt) {
    for (let remaining = seconds; remaining > 0; remaining -= 1) {
        rfpItems[index].status = `rate limited - retry in ${remaining}s`;
        renderRfpItems();
        setRfpStatus(`LLM rate limit reached. Retrying question ${index + 1} in ${remaining}s. Attempt ${attempt + 1} of 4.`);
        await wait(1000);
    }
}

async function answerRfpItem(index) {
    let lastError = "";

    for (let attempt = 1; attempt <= 4; attempt += 1) {
        const response = await fetch("/rfp/answer-one", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: rfpItems[index].question,
                use_memory: true,
                use_documents: true
            })
        });

        if (!response.ok) {
            lastError = `Request failed with status ${response.status}.`;
        } else {
            const data = await response.json();
            if (data.success) {
                return data;
            }
            lastError = data.error || "Answer generation failed.";
            if (data.rate_limited) {
                const retryAfter = Math.max(10, Math.min(Number(data.retry_after || 25), 60));
                rfpItems[index].error = lastError;
                await waitWithCountdown(retryAfter, index, attempt);
                continue;
            }
        }

        if (attempt < 2) {
            rfpItems[index].status = "retrying";
            rfpItems[index].error = lastError;
            renderRfpItems();
            await wait(3000);
        }
    }

    throw new Error(lastError || "Answer generation failed.");
}

async function generateRfpAnswers() {
    if (!rfpItems.length) {
        alert("Add at least one RFP question first.");
        return;
    }

    syncRfpAnswersFromDom();
    setRfpStatus(`Generating answers: 0 of ${rfpItems.length} complete.`);

    let completed = 0;
    let failed = 0;
    let nextDelay = 1000;

    for (let index = 0; index < rfpItems.length; index += 1) {
        rfpItems[index].status = "generating";
        rfpItems[index].error = "";
        renderRfpItems();

        try {
            const data = await answerRfpItem(index);
            rfpItems[index].answer = data.answer || "";
            rfpItems[index].from_memory = Boolean(data.from_memory);
            rfpItems[index].status = data.from_memory ? "answered from memory" : "answered";
            rfpItems[index].error = "";
            rfpItems[index].references = data.document_references || [];
            completed += 1;
            nextDelay = 1000;
        } catch (error) {
            console.error(error);
            rfpItems[index].status = "failed";
            rfpItems[index].error = error.message || "Answer generation failed.";
            failed += 1;
            nextDelay = 3000;
        }

        renderRfpItems();
        setRfpStatus(`Generating answers: ${completed + failed} of ${rfpItems.length} complete.`);
        await wait(nextDelay);
    }

    const message = failed
        ? `Generated ${completed} answer${completed === 1 ? "" : "s"}; ${failed} failed. You can retry or edit failed answers manually.`
        : `Generated ${completed} answer${completed === 1 ? "" : "s"}. You can edit them before exporting.`;
    setRfpStatus(message);
}

async function downloadRfpDocx() {
    syncRfpAnswersFromDom();
    const completedItems = rfpItems
        .map(item => ({
            question: item.question.trim(),
            answer: (item.answer || "").trim()
        }))
        .filter(item => item.question && item.answer);

    if (!completedItems.length) {
        alert("Generate or enter at least one answer before creating the DOCX.");
        return;
    }

    setRfpStatus("Creating DOCX...");

    try {
        const response = await fetch("/rfp/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: "Generated Vendor Responses",
                items: completedItems
            })
        });

        if (!response.ok) {
            throw new Error("DOCX generation failed.");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "rfp-response.docx";
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        setRfpStatus("DOCX generated.");
    } catch (error) {
        console.error(error);
        setRfpStatus("Could not generate DOCX.");
    }
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

    items.forEach((item) => {
        const question = item.question || "";
        const answer = item.answer || "";

        const div = document.createElement("div");
        div.className = "memory-item";
        div.onclick = function () {
            useMemory(item);
        };

        div.innerHTML = `
            <div class="memory-item-header">
                <div class="memory-question">${escapeHtml(question)}</div>
                <button class="memory-delete" type="button" onclick="deleteMemory(event, '${escapeHtml(item.id || "")}')">Remove</button>
            </div>
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

function useMemory(item) {
    if (!item) return;

    lastQuery = item.question || "";
    lastAnswer = item.answer || "";
    lastMatches = [];

    document.getElementById("badge").innerHTML = "Reused from memory";
    document.getElementById("answerText").innerHTML = renderAnswer(lastAnswer);
    document.getElementById("editBox").value = lastAnswer;
    document.getElementById("source").innerHTML = "Source: Memory";
    renderResponseTags(item.tags ? item.tags.map(tag => ({
        label: tag,
        tag_type: "memory",
        value: tag,
        score: null
    })) : [], []);
    document.getElementById("result").classList.remove("hidden");
}

async function deleteMemory(event, qaId) {
    event.stopPropagation();

    if (!qaId) {
        alert("Saved answer id is missing.");
        return;
    }

    const confirmed = window.confirm("Remove this saved answer from memory?");
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/memory/${encodeURIComponent(qaId)}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            alert("Remove failed.");
            return;
        }

        await loadMemory();
    } catch (error) {
        console.error(error);
        alert("Remove failed.");
    }
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
        lastMatches = [
            ...(data.memory_matches || []),
            ...(data.document_matches || [])
        ];

        const badge = data.from_memory
            ? "Reused from memory"
            : "From documents";

        document.getElementById("badge").innerHTML = badge;
        document.getElementById("answerText").innerHTML = renderAnswer(lastAnswer);
        document.getElementById("editBox").value = lastAnswer;
        renderResponseTags(data.response_tags || [], lastMatches);

        document.getElementById("source").innerHTML =
            data.from_memory ? "Source: Memory" : "Source: Documents";

        document.getElementById("result").classList.remove("hidden");

        updateHistory(query, lastAnswer);
    } catch (error) {
        console.error(error);
        document.getElementById("badge").innerHTML = "Error";
        document.getElementById("answerText").innerHTML =
            "Could not connect to backend.";
        renderResponseTags([], []);
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
        answerText.innerHTML = renderAnswer(lastAnswer);
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
