"""
简历分析工具模块
支持解析 PDF、Word、图片等格式的简历
"""
import os
import json
import base64
import requests
from typing import Dict, Any, Optional
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# 简历分析的System Prompt
RESUME_ANALYSIS_PROMPT = """你是一个专业的HR招聘专家，擅长从简历中提取关键信息。请分析以下简历内容，提取结构化的候选人信息。

请按以下JSON格式输出：
{
    "name": "姓名",
    "contact": {
        "phone": "手机号",
        "email": "邮箱",
        "location": "所在地"
    },
    "summary": "个人简介/概述（100字以内）",
    "skills": {
        "technical": ["技术技能1", "技术技能2"],
        "tools": ["工具/框架1", "工具/框架2"],
        "soft": ["软技能1", "软技能2"]
    },
    "experience": [
        {
            "company": "公司名",
            "position": "职位",
            "duration": "在职时间",
            "description": "工作描述"
        }
    ],
    "education": {
        "degree": "学历",
        "school": "学校",
        "major": "专业",
        "graduation": "毕业时间"
    },
    "highlights": ["亮点1", "亮点2", "亮点3"]
}

请确保输出是合法的JSON格式，不要包含其他文字说明。"""


def _get_text_content(response) -> str:
    """安全地获取响应的文本内容"""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 处理list类型，提取文本
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if 'text' in item:
                        parts.append(item['text'])
                    elif 'type' in item and item['type'] == 'text':
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            return '\n'.join(parts)
        else:
            return str(content)
    return str(response)


@tool
def analyze_resume_text(resume_text: str) -> str:
    """
    分析文本格式的简历内容，提取关键信息。
    
    Args:
        resume_text: 简历的文本内容（支持纯文本或Markdown格式）
    
    Returns:
        JSON格式的简历分析结果
    """
    try:
        # 使用 DeepSeek API
        api_key = "sk-0ab12c9e84ae4d75b5b78fc6a4f2edab"
        base_url = "https://api.deepseek.com"
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,
            max_tokens=2000
        )
        
        messages = [
            SystemMessage(content=RESUME_ANALYSIS_PROMPT),
            HumanMessage(content=f"请分析以下简历：\n\n{resume_text}")
        ]
        
        response = llm.invoke(messages)
        raw_content = _get_text_content(response)
        
        # 去除可能的markdown代码块
        content = raw_content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        # 去除首尾空白
        content = content.strip()
        
        # 验证JSON并返回
        parsed = json.loads(content)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
            
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": "JSON解析失败",
            "raw_content": raw_content[:500] if raw_content else "",
            "message": "请检查简历格式或手动输入信息"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "简历分析失败，请稍后重试"
        }, ensure_ascii=False, indent=2)


@tool
def analyze_resume_from_url(resume_url: str) -> str:
    """
    从URL下载并分析简历内容。
    
    Args:
        resume_url: 简历文件的URL
    
    Returns:
        JSON格式的简历分析结果
    """
    try:
        response = requests.get(resume_url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'image' in content_type.lower() or resume_url.lower().endswith(('.jpg', '.jpeg', '.png')):
            return json.dumps({
                "error": "图片格式暂不支持OCR",
                "message": "请提供文本格式的简历"
            }, ensure_ascii=False, indent=2)
        
        # 尝试作为文本处理
        try:
            text = response.content.decode('utf-8')
            return analyze_resume_text(text)
        except:
            return json.dumps({
                "error": "文件格式不支持",
                "message": "请上传文本格式简历或粘贴内容"
            }, ensure_ascii=False, indent=2)
                
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "简历下载失败，请检查URL是否正确"
        }, ensure_ascii=False, indent=2)


@tool
def extract_resume_highlights(resume_json: str) -> str:
    """
    从已分析的简历JSON中提取面试亮点，用于生成针对性问题。
    
    Args:
        resume_json: 简历分析后的JSON字符串
    
    Returns:
        面试亮点总结
    """
    try:
        resume_data = json.loads(resume_json)
        
        if "error" in resume_data:
            return resume_json
        
        highlights = []
        
        # 提取技术亮点
        if "skills" in resume_data:
            skills = resume_data.get("skills", {})
            technical = skills.get("technical", [])
            if technical:
                highlights.append(f"技术栈: {', '.join(technical[:5])}")
        
        # 提取工作经验亮点
        if "experience" in resume_data:
            experiences = resume_data.get("experience", [])
            if experiences:
                latest = experiences[0]
                highlights.append(f"最近职位: {latest.get('position', '未知')} @ {latest.get('company', '未知')}")
        
        # 提取教育背景
        if "education" in resume_data:
            edu = resume_data.get("education", {})
            if edu:
                highlights.append(f"学历: {edu.get('degree', '未知')} - {edu.get('school', '未知')}")
        
        return json.dumps({
            "candidate_name": resume_data.get("name", "未知"),
            "highlights": highlights,
            "summary": resume_data.get("summary", ""),
            "suggested_focus": _suggest_interview_focus(resume_data)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)


def _suggest_interview_focus(resume_data: Dict) -> list:
    """根据简历建议面试重点"""
    focus_areas = []
    
    if "skills" in resume_data:
        skills = str(resume_data.get("skills", {}))
        
        if "Python" in skills:
            focus_areas.append("Python高级特性与性能优化")
        if "Django" in skills or "Flask" in skills:
            focus_areas.append("Web框架实战经验")
        if "MySQL" in skills or "PostgreSQL" in skills:
            focus_areas.append("数据库设计与优化")
        if "Redis" in skills:
            focus_areas.append("缓存系统设计与实践")
    
    if not focus_areas:
        focus_areas = ["项目经验深挖", "技术原理理解", "问题解决能力"]
    
    return focus_areas
