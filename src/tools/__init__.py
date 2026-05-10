"""
面试Agent工具集
"""
from tools.voice_tools import text_to_speech, speech_to_text, speech_to_text_base64
from tools.resume_tools import analyze_resume_text, analyze_resume_from_url, extract_resume_highlights
from tools.evaluation_tools import generate_interview_report, generate_quick_score, export_report_markdown

__all__ = [
    # 语音工具
    "text_to_speech",
    "speech_to_text",
    "speech_to_text_base64",
    # 简历工具
    "analyze_resume_text",
    "analyze_resume_from_url",
    "extract_resume_highlights",
    # 评估工具
    "generate_interview_report",
    "generate_quick_score",
    "export_report_markdown",
]
