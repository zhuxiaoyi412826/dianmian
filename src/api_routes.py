"""
数据库 REST API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from storage.database import (
    init_db,
    UserDAO,
    ResumeDAO,
    InterviewDAO,
    MessageDAO,
    ReportDAO,
    FavoriteQuestionDAO
)
import json
import os

router = APIRouter(prefix="/api/v1", tags=["database"])


# ==================== 用户接口 ====================

class CreateUserRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None


class UpdateUserRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


@router.post("/users/init")
async def init_database():
    """初始化数据库"""
    try:
        init_db()
        return {"status": "ok", "message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
async def create_user(request: CreateUserRequest):
    """创建用户"""
    try:
        user_id = UserDAO.create(
            phone=request.phone,
            email=request.email,
            nickname=request.nickname or f"用户{request.phone or ''}"
        )
        user = UserDAO.get_by_id(user_id)
        return {"status": "ok", "data": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    user = UserDAO.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "ok", "data": user}


@router.get("/users/phone/{phone}")
async def get_user_by_phone(phone: str):
    """根据手机号获取用户"""
    user = UserDAO.get_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "ok", "data": user}


@router.put("/users/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest):
    """更新用户信息"""
    data = request.model_dump(exclude_none=True)
    if UserDAO.update(user_id, **data):
        user = UserDAO.get_by_id(user_id)
        return {"status": "ok", "data": user}
    raise HTTPException(status_code=404, detail="User not found")


# ==================== 简历接口 ====================

class CreateResumeRequest(BaseModel):
    user_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    education: Optional[str] = None
    work_experience: Optional[str] = None
    skills: Optional[List[str]] = []
    projects: Optional[List[dict]] = []
    raw_text: Optional[str] = None
    file_url: Optional[str] = None


@router.post("/resumes")
async def create_resume(request: CreateResumeRequest):
    """创建简历"""
    try:
        data = request.model_dump()
        resume_id = ResumeDAO.create(request.user_id, data)
        resume = ResumeDAO.get_by_id(resume_id)
        return {"status": "ok", "data": resume}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: int):
    """获取简历"""
    resume = ResumeDAO.get_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"status": "ok", "data": resume}


@router.get("/users/{user_id}/resumes")
async def get_user_resumes(user_id: int):
    """获取用户的所有简历"""
    resumes = ResumeDAO.get_by_user(user_id)
    return {"status": "ok", "data": resumes}


@router.post("/resumes/{resume_id}/set-default")
async def set_default_resume(user_id: int, resume_id: int):
    """设置默认简历"""
    if ResumeDAO.set_default(user_id, resume_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Resume not found")


@router.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: int):
    """删除简历"""
    if ResumeDAO.delete(resume_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Resume not found")


# ==================== 面试接口 ====================

class CreateInterviewRequest(BaseModel):
    user_id: int
    position: str
    resume_id: Optional[int] = None
    level: Optional[str] = "中级"
    mode: Optional[str] = "语音"


@router.post("/interviews")
async def create_interview(request: CreateInterviewRequest):
    """创建面试"""
    try:
        interview_id = InterviewDAO.create(
            user_id=request.user_id,
            position=request.position,
            resume_id=request.resume_id,
            level=request.level,
            mode=request.mode
        )
        interview = InterviewDAO.get_by_id(interview_id)
        return {"status": "ok", "data": interview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interviews/{interview_id}")
async def get_interview(interview_id: int):
    """获取面试"""
    interview = InterviewDAO.get_by_id(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {"status": "ok", "data": interview}


@router.get("/users/{user_id}/interviews")
async def get_user_interviews(user_id: int, limit: int = 20, offset: int = 0):
    """获取用户的面试列表"""
    interviews = InterviewDAO.get_by_user(user_id, limit, offset)
    stats = InterviewDAO.get_stats(user_id)
    return {"status": "ok", "data": {"list": interviews, "stats": stats}}


@router.post("/interviews/{interview_id}/end")
async def end_interview(interview_id: int, duration: int = 0):
    """结束面试"""
    if InterviewDAO.end(interview_id, duration):
        interview = InterviewDAO.get_by_id(interview_id)
        return {"status": "ok", "data": interview}
    raise HTTPException(status_code=404, detail="Interview not found")


@router.delete("/interviews/{interview_id}")
async def delete_interview(interview_id: int):
    """删除面试"""
    if InterviewDAO.delete(interview_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Interview not found")


# ==================== 消息接口 ====================

class CreateMessageRequest(BaseModel):
    interview_id: int
    role: str  # 'user' or 'assistant'
    content: str
    audio_url: Optional[str] = None
    audio_duration: Optional[float] = 0


@router.post("/messages")
async def create_message(request: CreateMessageRequest):
    """创建消息"""
    try:
        message_id = MessageDAO.create(
            interview_id=request.interview_id,
            role=request.role,
            content=request.content,
            audio_url=request.audio_url,
            audio_duration=request.audio_duration or 0
        )
        return {"status": "ok", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interviews/{interview_id}/messages")
async def get_interview_messages(interview_id: int):
    """获取面试的所有消息"""
    messages = MessageDAO.get_by_interview(interview_id)
    return {"status": "ok", "data": messages}


# ==================== 报告接口 ====================

class CreateReportRequest(BaseModel):
    interview_id: int
    user_id: int
    overall_score: float
    technical_score: float
    project_score: float
    communication_score: float
    logic_score: float
    pressure_score: float
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None
    feedback: Optional[dict] = {}


@router.post("/reports")
async def create_report(request: CreateReportRequest):
    """创建评估报告"""
    try:
        data = request.model_dump()
        report_id = ReportDAO.create(request.interview_id, request.user_id, data)
        report = ReportDAO.get_by_id(report_id)
        return {"status": "ok", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(report_id: int):
    """获取报告"""
    report = ReportDAO.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "ok", "data": report}


@router.get("/interviews/{interview_id}/report")
async def get_report_by_interview(interview_id: int):
    """根据面试获取报告"""
    report = ReportDAO.get_by_interview(interview_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "ok", "data": report}


@router.get("/users/{user_id}/reports")
async def get_user_reports(user_id: int, limit: int = 20, offset: int = 0):
    """获取用户的所有报告"""
    reports = ReportDAO.get_by_user(user_id, limit, offset)
    return {"status": "ok", "data": reports}


# ==================== 收藏问题接口 ====================

class CreateFavoriteRequest(BaseModel):
    user_id: int
    interview_id: Optional[int] = None
    question: str
    answer: Optional[str] = None
    notes: Optional[str] = None


@router.post("/favorites")
async def create_favorite(request: CreateFavoriteRequest):
    """收藏问题"""
    try:
        favorite_id = FavoriteQuestionDAO.create(
            user_id=request.user_id,
            interview_id=request.interview_id,
            question=request.question,
            answer=request.answer,
            notes=request.notes
        )
        return {"status": "ok", "favorite_id": favorite_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/favorites")
async def get_user_favorites(user_id: int):
    """获取用户收藏的问题"""
    favorites = FavoriteQuestionDAO.get_by_user(user_id)
    return {"status": "ok", "data": favorites}


@router.delete("/favorites/{favorite_id}")
async def delete_favorite(favorite_id: int):
    """取消收藏"""
    if FavoriteQuestionDAO.delete(favorite_id):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Favorite not found")
