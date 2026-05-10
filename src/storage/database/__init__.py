"""
数据库存储模块
"""
from .connection import get_connection, init_db, get_db_path, dict_from_row
from .dao import (
    UserDAO,
    ResumeDAO,
    InterviewDAO,
    MessageDAO,
    ReportDAO,
    FavoriteQuestionDAO
)

__all__ = [
    'get_connection',
    'init_db', 
    'get_db_path',
    'dict_from_row',
    'UserDAO',
    'ResumeDAO',
    'InterviewDAO',
    'MessageDAO',
    'ReportDAO',
    'FavoriteQuestionDAO'
]
