from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.ai_service import analyze_skills, extract_skills
from services.resume_parser import extract_text_from_pdf

router = APIRouter()


def _friendly_error_message(exc: Exception) -> str:
    message = str(exc)

    if "quota" in message.lower() or "resource has been exhausted" in message.lower():
        return (
            "Gemini quota exceeded. Wait and try again later, or use a different Gemini API key, "
            "then try again."
        )

    if "api key not valid" in message.lower() or "permission denied" in message.lower():
        return "Gemini API key is invalid. Update GEMINI_API_KEY in backend/.env and restart the backend."

    return message


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(file.file)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded PDF.")

        result = extract_skills(text)
        return {
            "filename": file.filename,
            "skills": result["skills"],
            "source": result["source"],
            "cached": result["cached"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Resume upload failed: {_friendly_error_message(exc)}",
        ) from exc


@router.post("/analyze")
async def analyze(user_skills: str = Form(...), role: str = Form(...)):
    try:
        result = analyze_skills(user_skills, role)
        return {
            "role": role,
            "analysis": result["analysis"],
            "source": result["source"],
            "cached": result["cached"],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Skill analysis failed: {_friendly_error_message(exc)}",
        ) from exc
