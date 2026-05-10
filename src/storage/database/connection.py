"""
SQLite 数据库连接模块
"""
import sqlite3
import os
from typing import Generator
from contextlib import contextmanager

# 数据库文件路径
DB_PATH = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "data", "interview.db")


def get_db_path() -> str:
    """获取数据库文件路径"""
    return DB_PATH


def init_db() -> None:
    """初始化数据库和表结构"""
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 启用 WAL 模式提升并发性能
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('PRAGMA foreign_keys=ON')

    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(255),
            nickname VARCHAR(100),
            avatar_url VARCHAR(500),
            settings JSON DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建简历表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100),
            phone VARCHAR(20),
            email VARCHAR(255),
            education TEXT,
            work_experience TEXT,
            skills JSON DEFAULT '[]',
            projects JSON DEFAULT '[]',
            raw_text TEXT,
            file_url VARCHAR(500),
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 创建面试记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER,
            position VARCHAR(100) NOT NULL,
            level VARCHAR(20) DEFAULT '中级',
            mode VARCHAR(20) DEFAULT '语音',
            status VARCHAR(20) DEFAULT 'pending',
            duration INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL
        )
    ''')

    # 创建对话消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT,
            audio_url VARCHAR(500),
            audio_duration FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
        )
    ''')

    # 创建评估报告表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            overall_score DECIMAL(3,1) DEFAULT 0,
            technical_score DECIMAL(3,1) DEFAULT 0,
            project_score DECIMAL(3,1) DEFAULT 0,
            communication_score DECIMAL(3,1) DEFAULT 0,
            logic_score DECIMAL(3,1) DEFAULT 0,
            pressure_score DECIMAL(3,1) DEFAULT 0,
            strengths TEXT,
            weaknesses TEXT,
            suggestions TEXT,
            feedback JSON DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 创建收藏问题表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorited_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interview_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE SET NULL
        )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_interview ON messages(interview_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interviews_user ON interviews(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id)')

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> dict:
    """将 Row 对象转换为字典"""
    if row is None:
        return None
    return dict(zip(row.keys(), row))
