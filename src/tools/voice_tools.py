"""
语音处理工具模块
包含 TTS（文本转语音）和 ASR（语音转文本）功能
"""
import os
import base64
import requests
from typing import Tuple
from langchain.tools import tool
from coze_coding_dev_sdk import TTSClient, ASRClient

# 默认用户ID
DEFAULT_UID = "interview_user"

# 可选音色列表
VOICE_OPTIONS = {
    "female": "zh_female_xiaohe_uranus_bigtts",
    "male": "zh_male_m191_uranus_bigtts",
    "professional": "zh_female_vv_uranus_bigtts",
}


@tool
def text_to_speech(text: str, voice: str = "female") -> str:
    """
    将文本转换为语音，返回音频URL。
    
    Args:
        text: 要转换的文本内容
        voice: 音色选择，可选 'female'（女声）、'male'（男声）、'professional'（专业女声）
    
    Returns:
        格式: "success|audio_url|audio_size" 或 "error|error_message"
    """
    try:
        speaker = VOICE_OPTIONS.get(voice, VOICE_OPTIONS["female"])
        
        client = TTSClient()
        
        audio_url, audio_size = client.synthesize(
            uid=DEFAULT_UID,
            text=text,
            speaker=speaker,
            audio_format="mp3",
            sample_rate=24000
        )
        
        return f"success|{audio_url}|{audio_size}"
    except Exception as e:
        return f"error|语音合成失败: {str(e)}"


@tool
def speech_to_text(audio_url: str) -> str:
    """
    将语音转换为文本。
    
    Args:
        audio_url: 音频文件的URL地址
    
    Returns:
        格式: "success|recognized_text" 或 "error|error_message"
    """
    try:
        client = ASRClient()
        
        text, data = client.recognize(
            uid=DEFAULT_UID,
            url=audio_url
        )
        
        if text:
            return f"success|{text}"
        else:
            return "error|未能识别到语音内容，请重试"
    except Exception as e:
        return f"error|语音识别失败: {str(e)}"


@tool
def speech_to_text_base64(audio_base64: str) -> str:
    """
    将Base64编码的音频转换为文本。
    
    Args:
        audio_base64: Base64编码的音频数据
    
    Returns:
        格式: "success|recognized_text" 或 "error|error_message"
    """
    try:
        client = ASRClient()
        
        text, data = client.recognize(
            uid=DEFAULT_UID,
            base64_data=audio_base64
        )
        
        if text:
            return f"success|{text}"
        else:
            return "error|未能识别到语音内容，请重试"
    except Exception as e:
        return f"error|语音识别失败: {str(e)}"
