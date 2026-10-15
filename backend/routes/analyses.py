from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Analysis
from schemas import AnalysisRecord, AnalysisUpdate
from services.ai_service import analyze_skills

router = APIRouter(prefix="/analyses", tags=["analyses"])


def owner_id(x_user_id: str = Header(..., alias="X-User-Id")) -> str:
    try:
        return str(UUID(x_user_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-User-Id must be a UUID") from exc


@router.get("", response_model=list[AnalysisRecord])
def list_analyses(owner: str = Depends(owner_id), db: Session = Depends(get_db)):
    return db.query(Analysis).filter_by(owner_id=owner).order_by(Analysis.updated_at.desc()).all()


@router.post("", response_model=AnalysisRecord, status_code=201)
def create_analysis(payload: AnalysisUpdate, owner: str = Depends(owner_id), db: Session = Depends(get_db)):
    if not payload.role or not payload.skills:
        raise HTTPException(status_code=422, detail="role and skills are required")
    result = analyze_skills(payload.skills, payload.role)
    record = Analysis(owner_id=owner, role=payload.role, skills=payload.skills, analysis=result["analysis"], source=result["source"])
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{analysis_id}", response_model=AnalysisRecord)
def get_analysis(analysis_id: int, owner: str = Depends(owner_id), db: Session = Depends(get_db)):
    record = db.query(Analysis).filter_by(id=analysis_id, owner_id=owner).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return record


@router.patch("/{analysis_id}", response_model=AnalysisRecord)
def update_analysis(analysis_id: int, payload: AnalysisUpdate, owner: str = Depends(owner_id), db: Session = Depends(get_db)):
    record = db.query(Analysis).filter_by(id=analysis_id, owner_id=owner).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide role and/or skills to update")
    record.role = changes.get("role", record.role)
    record.skills = changes.get("skills", record.skills)
    result = analyze_skills(record.skills, record.role)
    record.analysis, record.source = result["analysis"], result["source"]
    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: int, owner: str = Depends(owner_id), db: Session = Depends(get_db)):
    record = db.query(Analysis).filter_by(id=analysis_id, owner_id=owner).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(record)
    db.commit()
