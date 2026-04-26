"""日记路由 - /api/v1/diary"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.diary import Diary, DiaryAnalysis
from app.models.user import User
from app.services.auth import get_current_user
from app.services.diary import diagnose_diary

router = APIRouter(prefix="/diary", tags=["diary"])


class DiaryCreate(BaseModel):
    context: str
    other_party: str
    their_words: str
    my_response: str
    outcome: str


@router.post("")
async def create_diary(
    body: DiaryCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    diary = Diary(
        user_id=user.id,
        context=body.context,
        other_party=body.other_party,
        their_words=body.their_words,
        my_response=body.my_response,
        outcome=body.outcome,
    )
    session.add(diary)
    session.commit()
    session.refresh(diary)

    result = await diagnose_diary(
        context=body.context,
        other_party=body.other_party,
        their_words=body.their_words,
        my_response=body.my_response,
        outcome=body.outcome,
        session=session,
    )

    import json
    analysis = DiaryAnalysis(
        diary_id=diary.id,
        identified_skills=json.dumps(result["identified_skills"], ensure_ascii=False),
        diagnosis_brief=result["diagnosis_brief"],
        socratic_questions=json.dumps(result["socratic_questions"], ensure_ascii=False),
        rewrite_suggestion_hidden=result["rewrite_suggestion_hidden"],
        referenced_style=result["referenced_style"],
    )
    session.add(analysis)
    session.commit()
    session.refresh(analysis)

    return {
        "diary_id": diary.id,
        "analysis_id": analysis.id,
        "identified_skills": result["identified_skills"],
        "diagnosis_brief": result["diagnosis_brief"],
        "socratic_questions": result["socratic_questions"],
        "referenced_style": result["referenced_style"],
        # 改写示范默认不返回，等前端主动请求
    }


@router.get("/{diary_id}/rewrite")
def get_rewrite(
    diary_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """用户主动要求才返回改写示范"""
    diary = session.get(Diary, diary_id)
    if not diary or diary.user_id != user.id:
        raise HTTPException(404, "日记不存在")
    analysis = session.exec(
        select(DiaryAnalysis).where(DiaryAnalysis.diary_id == diary_id)
    ).first()
    if not analysis:
        raise HTTPException(404, "分析不存在")
    return {"rewrite_suggestion": analysis.rewrite_suggestion_hidden}


@router.get("")
def list_diaries(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    diaries = session.exec(
        select(Diary).where(Diary.user_id == user.id).order_by(Diary.created_at.desc()).limit(20)  # type: ignore
    ).all()
    return [
        {
            "id": d.id,
            "context": d.context[:50] + "..." if len(d.context) > 50 else d.context,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in diaries
    ]
