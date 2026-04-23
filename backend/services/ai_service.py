import hashlib
import httpx
import re

from config import GEMINI_API_KEY, GEMINI_MODEL

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
CACHE = {"extract": {}, "analyze": {}}


def _cache_key(*parts: str) -> str:
    joined = "||".join(part.strip().lower() for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _generate_text(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = httpx.post(
            GEMINI_API_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=60.0,
        )

        data = response.json()

        if response.status_code >= 400:
            error_message = data.get("error", {}).get("message", "Gemini request failed.")
            raise RuntimeError(error_message)

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates.")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()

        if not text:
            raise RuntimeError("Empty response from Gemini")

        return text

    except Exception as exc:
        print("GEMINI ERROR:", exc)
        raise exc


KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "html", "css", "react", "angular", "vue",
    "node.js", "node", "express", "fastapi", "django", "flask", "sql", "mysql", "postgresql",
    "mongodb", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git", "github",
    "jenkins", "terraform", "ansible", "redis", "ci/cd", "rest api", "microservices",
    "pandas", "numpy", "machine learning",
]

ROLE_SKILLS = {
    "devops engineer": ["linux", "docker", "kubernetes", "aws", "terraform", "jenkins", "ansible", "git", "ci/cd"],
    "backend developer": ["python", "fastapi", "sql", "postgresql", "docker", "rest api", "git"],
    "full stack developer": ["html", "css", "javascript", "react", "node.js", "sql", "git"],
    "data analyst": ["python", "sql", "pandas", "numpy", "excel"],
}


def _normalize_skill_list(text: str):
    found = []
    haystack = text.lower()

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, haystack) and skill not in found:
            found.append(skill)

    return found


def _fallback_extract_skills(text: str):
    skills = _normalize_skill_list(text)
    return ", ".join(skills) if skills else "No common technical skills detected."


def _match_role_skills(role: str):
    role_lower = role.lower()

    for role_name, skills in ROLE_SKILLS.items():
        if role_name in role_lower:
            return skills

    return ["communication", "problem solving", "git"]


def _fallback_analyze_skills(user_skills: str, role: str):
    current_skills = set(_normalize_skill_list(user_skills))
    target_skills = _match_role_skills(role)
    missing_skills = [skill for skill in target_skills if skill not in current_skills]

    return f"""
Target Role: {role}

Current Skills: {', '.join(sorted(current_skills))}

Missing Skills: {', '.join(missing_skills)}

Roadmap:
1. Learn missing skills step by step
2. Build projects
3. Practice interviews

(Note: fallback used)
"""


def extract_skills(text):
    text = text[:3000]
    cache_key = _cache_key(text)

    if cache_key in CACHE["extract"]:
        cached = CACHE["extract"][cache_key].copy()
        cached["cached"] = True
        return cached

    prompt = f"""
    Extract all technical skills from this resume.
    Return only comma-separated skills.

    {text}
    """

    try:
        result = {"skills": _generate_text(prompt), "source": "gemini", "cached": False}
    except Exception:
        print("FALLBACK: extract_skills")
        result = {"skills": _fallback_extract_skills(text), "source": "fallback", "cached": False}

    CACHE["extract"][cache_key] = result.copy()
    return result


def analyze_skills(user_skills, role):
    cache_key = _cache_key(user_skills, role)

    if cache_key in CACHE["analyze"]:
        cached = CACHE["analyze"][cache_key].copy()
        cached["cached"] = True
        return cached

    prompt = f"""
    User Skills: {user_skills}
    Target Role: {role}

    Give:
    - Missing skills
    - Roadmap
    - Suggestions
    """

    try:
        result = {"analysis": _generate_text(prompt), "source": "gemini", "cached": False}
    except Exception:
        print("FALLBACK: analyze_skills")
        result = {"analysis": _fallback_analyze_skills(user_skills, role), "source": "fallback", "cached": False}

    CACHE["analyze"][cache_key] = result.copy()
    return result
