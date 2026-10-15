const API_URL = window.SKILLSYNC_API_URL || "/api";
const USER_ID_KEY = "skillsyncUserId";
const USER_ID = localStorage.getItem(USER_ID_KEY) || crypto.randomUUID();
localStorage.setItem(USER_ID_KEY, USER_ID);

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: { "X-User-Id": USER_ID, ...(options.headers || {}) }
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Request failed (${response.status})`);
    }
    return response.status === 204 ? null : response.json();
}

function setLoadingState(isLoading, message) {
    const loader = document.getElementById("pageLoader");
    const loaderText = document.getElementById("loaderText");
    document.querySelectorAll("button").forEach(button => button.disabled = isLoading);
    if (loaderText && message) loaderText.innerText = message;
    if (loader) {
        loader.classList.toggle("visible", isLoading);
        loader.setAttribute("aria-hidden", isLoading ? "false" : "true");
    }
}

async function uploadResume() {
    const file = document.getElementById("resumeFile")?.files[0];
    if (!file) return alert("Please select a file!");
    const formData = new FormData();
    formData.append("file", file);
    try {
        setLoadingState(true, "Extracting skills from your resume...");
        const data = await apiFetch("/upload", { method: "POST", body: formData });
        document.getElementById("extractedSkills").innerText = data.skills;
        document.getElementById("skills").value = data.skills;
        localStorage.setItem("uploadNotice", data.source === "fallback" ? "Fallback skill extraction used." : "");
    } catch (error) { alert(error.message); }
    finally { setLoadingState(false); }
}

async function analyzeSkills() {
    const skills = document.getElementById("skills").value.trim();
    const role = document.getElementById("role").value.trim();
    if (!skills || !role) return alert("Enter your skills and target role first.");
    try {
        setLoadingState(true, "Generating your roadmap...");
        const data = await apiFetch("/analyses", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ skills, role })
        });
        window.location.href = `dashboard.html?id=${data.id}`;
    } catch (error) { alert(error.message); }
    finally { setLoadingState(false); }
}

async function loadHistory() {
    const list = document.getElementById("historyList");
    if (!list) return;
    try {
        const records = await apiFetch("/analyses");
        list.replaceChildren();
        if (!records.length) list.textContent = "No saved analyses yet.";
        records.forEach(record => {
            const row = document.createElement("div"); row.className = "history-row";
            const open = document.createElement("a");
            open.href = `dashboard.html?id=${record.id}`;
            open.textContent = `${record.role} · ${new Date(record.updated_at).toLocaleString()}`;
            const remove = document.createElement("button"); remove.textContent = "Delete";
            remove.onclick = async () => {
                if (!confirm("Delete this saved analysis?")) return;
                try { await apiFetch(`/analyses/${record.id}`, { method: "DELETE" }); await loadHistory(); }
                catch (error) { alert(error.message); }
            };
            row.append(open, remove); list.append(row);
        });
    } catch (error) { list.textContent = error.message; }
}

async function loadAnalysisPage() {
    const output = document.getElementById("result");
    if (!output) return;
    const id = new URLSearchParams(location.search).get("id");
    if (!id) { output.textContent = "Select a saved analysis from history."; return; }
    try {
        const record = await apiFetch(`/analyses/${id}`);
        output.textContent = record.analysis;
        document.getElementById("analysisRole").textContent = record.role;
        document.getElementById("analysisSkills").textContent = record.skills;
        document.getElementById("editAnalysis").onclick = async () => {
            const role = prompt("Update target role:", record.role);
            if (role === null) return;
            const skills = prompt("Update skills:", record.skills);
            if (skills === null) return;
            try {
                await apiFetch(`/analyses/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role, skills }) });
                await loadAnalysisPage(); await loadHistory();
            } catch (error) { alert(error.message); }
        };
    } catch (error) { output.textContent = error.message; }
}

document.addEventListener("DOMContentLoaded", () => {
    setLoadingState(false);
    loadHistory();
    loadAnalysisPage();
});
