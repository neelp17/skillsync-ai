const API_URL = "http://127.0.0.1:8000";

function setLoadingState(isLoading, message) {
    const loader = document.getElementById("pageLoader");
    const loaderText = document.getElementById("loaderText");
    const buttons = document.querySelectorAll("button");

    if (loaderText && message) {
        loaderText.innerText = message;
    }

    buttons.forEach(button => {
        button.disabled = isLoading;
    });

    if (!loader) {
        return;
    }

    loader.classList.toggle("visible", isLoading);
    loader.setAttribute("aria-hidden", isLoading ? "false" : "true");
}

async function uploadResume() {
    const fileInput = document.getElementById("resumeFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    try {
        setLoadingState(true, "Extracting skills from your resume...");

        let response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        let data = await response.json();

        document.getElementById("extractedSkills").innerText = data.skills;
        document.getElementById("skills").value = data.skills;

        const uploadNotices = [];
        if (data.source === "fallback") {
            uploadNotices.push("Gemini quota exceeded, so extracted skills are shown from the fallback parser.");
        }
        if (data.cached) {
            uploadNotices.push("Cached extraction used.");
        }
        localStorage.setItem("uploadNotice", uploadNotices.join(" "));
    } finally {
        setLoadingState(false);
    }
}

async function analyzeSkills() {
    const skills = document.getElementById("skills").value;
    const role = document.getElementById("role").value;

    let formData = new FormData();
    formData.append("user_skills", skills);
    formData.append("role", role);

    try {
        setLoadingState(true, "Generating your roadmap...");

        let response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            body: formData
        });

        let data = await response.json();

        localStorage.setItem("result", JSON.stringify(data));
        window.location.href = "dashboard.html";
    } finally {
        setLoadingState(false);
    }
}
