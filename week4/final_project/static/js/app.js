const form = document.querySelector("#mission-form");
const descriptionInput = document.querySelector("#description");
const characterCount = document.querySelector("#character-count");
const analyzeButton = document.querySelector("#analyze-button");
const loadingPanel = document.querySelector("#loading");
const messageBox = document.querySelector("#message");
const resultPanel = document.querySelector("#result");
const historyList = document.querySelector("#history-list");
const historyEmpty = document.querySelector("#history-empty");
const historyTemplate = document.querySelector("#history-template");
const refreshHistoryButton = document.querySelector("#refresh-history");
const downloadButton = document.querySelector("#download-report");

let currentMissionId = null;

async function api(url, options = {}) {
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json") ? await response.json() : null;

    if (!response.ok) {
        throw new Error(body?.error || `Request failed with status ${response.status}.`);
    }
    return body;
}

function setMessage(text = "", type = "error") {
    messageBox.hidden = !text;
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
}

function setLoading(isLoading) {
    loadingPanel.hidden = !isLoading;
    analyzeButton.disabled = isLoading;
    analyzeButton.querySelector(".button-label").textContent = isLoading
        ? "Analyzing…"
        : "Analyze mission";
}

function setText(selector, value) {
    document.querySelector(selector).textContent = value ?? "—";
}

function formatNumber(value) {
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

function itemText(item) {
    if (typeof item !== "object" || item === null) return String(item);
    if (item.subsystem) return `${item.subsystem} — ${item.reason}`;
    if (item.payload_type) return `${item.payload_type} — ${item.use_when}`;
    if (item.condition) return `${item.condition} — ${item.recommendation}`;
    return Object.values(item).filter(Boolean).join(" — ");
}

function renderList(selector, items = []) {
    const list = document.querySelector(selector);
    list.replaceChildren();
    for (const item of items) {
        const element = document.createElement("li");
        element.textContent = itemText(item);
        list.append(element);
    }
}

function renderMission(mission) {
    const recommendation = mission.ai_recommendation;
    const knowledge = mission.engineering_knowledge || {};
    currentMissionId = mission.mission_id;

    setText("#result-description", mission.mission_description);
    setText("#metric-mission", recommendation.mission_type);
    setText("#metric-orbit", recommendation.recommended_orbit);
    setText("#metric-altitude", `${formatNumber(recommendation.altitude_km)} km`);
    setText("#metric-power", `${formatNumber(recommendation.power_watts)} W`);
    setText("#metric-mass", recommendation.mass_class);
    setText("#metric-lifetime", `${formatNumber(recommendation.lifetime_years)} years`);
    setText("#result-payload", recommendation.payload);
    setText("#result-adcs", recommendation.adcs_type);
    setText("#result-justification", recommendation.justification);

    renderList("#knowledge-drivers", knowledge.design_drivers);
    renderList("#knowledge-subsystems", knowledge.required_subsystems);
    renderList("#knowledge-advantages", knowledge.advantages);
    renderList("#knowledge-limitations", knowledge.limitations);

    resultPanel.hidden = false;
    document.querySelectorAll(".history-item").forEach((item) => {
        item.classList.toggle("active", Number(item.dataset.id) === currentMissionId);
    });
    resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function formatDate(value) {
    const date = new Date(value);
    return Number.isNaN(date.valueOf())
        ? value
        : new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(date);
}

async function openMission(missionId) {
    setMessage();
    try {
        renderMission(await api(`/mission/${missionId}`));
    } catch (error) {
        setMessage(error.message);
    }
}

async function removeMission(missionId) {
    if (!window.confirm("Delete this mission and its recommendation?")) return;

    try {
        await api(`/mission/${missionId}`, { method: "DELETE" });
        if (currentMissionId === missionId) {
            currentMissionId = null;
            resultPanel.hidden = true;
        }
        setMessage("Mission deleted.", "success");
        await loadHistory();
    } catch (error) {
        setMessage(error.message);
    }
}

async function loadHistory() {
    try {
        const { missions } = await api("/missions");
        historyList.replaceChildren();
        historyEmpty.hidden = missions.length !== 0;

        for (const mission of missions) {
            const fragment = historyTemplate.content.cloneNode(true);
            const item = fragment.querySelector(".history-item");
            item.dataset.id = mission.id;
            item.classList.toggle("active", mission.id === currentMissionId);
            fragment.querySelector(".history-type").textContent = mission.mission_type;
            fragment.querySelector(".history-description").textContent = mission.description;
            fragment.querySelector(".history-meta").textContent = `${mission.recommended_orbit} • ${formatDate(mission.created_at)}`;
            fragment.querySelector(".history-open").addEventListener("click", () => openMission(mission.id));
            fragment.querySelector(".history-delete").addEventListener("click", () => removeMission(mission.id));
            historyList.append(fragment);
        }
    } catch (error) {
        setMessage(error.message);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage();
    setLoading(true);

    try {
        const mission = await api("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: descriptionInput.value }),
        });
        renderMission(mission);
        setMessage("Mission analyzed and saved.", "success");
        await loadHistory();
    } catch (error) {
        setMessage(error.message);
    } finally {
        setLoading(false);
    }
});

descriptionInput.addEventListener("input", () => {
    characterCount.textContent = `${descriptionInput.value.length.toLocaleString()} / 2,000`;
});

document.querySelectorAll(".prompt-chip").forEach((button) => {
    button.addEventListener("click", () => {
        descriptionInput.value = button.dataset.prompt;
        descriptionInput.dispatchEvent(new Event("input"));
        descriptionInput.focus();
    });
});

refreshHistoryButton.addEventListener("click", loadHistory);
downloadButton.addEventListener("click", () => {
    if (currentMissionId !== null) window.location.assign(`/download/${currentMissionId}`);
});

loadHistory();
