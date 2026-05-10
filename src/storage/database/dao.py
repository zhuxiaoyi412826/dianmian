"""
用户数据访问层
"""
import json
from typing import Optional, List
from .connection import get_connection, dict_from_row


class UserDAO:
    """用户数据访问对象"""

    @staticmethod
    def create(phone: str = None, email: str = None, nickname: str = None) -> int:
        """创建新用户"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO users (phone, email, nickname) VALUES (?, ?, ?)''',
                (phone, email, nickname)
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_id(user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict_from_row(row)

    @staticmethod
    def get_by_phone(phone: str) -> Optional[dict]:
        """根据手机号获取用户"""
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,))
            row = cursor.fetchone()
            return dict_from_row(row)

    @staticmethod
    def update(user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['phone', 'email', 'nickname', 'avatar_url', 'settings']:
                fields.append(f"{key} = ?")
                if key == 'settings' and isinstance(value, dict):
                    value = json.dumps(value)
                values.append(value)
        
        if not fields:
            return False

        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        with get_connection() as conn:
            cursor = conn.execute(sql, values)
            return cursor.rowcount > 0

    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        with get_connection() as conn:
            cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            return cursor.rowcount > 0


class ResumeDAO:
    """简历数据访问对象"""

    @staticmethod
    def create(user_id: int, data: dict) -> int:
        """创建简历"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO resumes 
                (user_id, name, phone, email, education, work_experience, skills, projects, raw_text, file_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    data.get('name'),
                    data.get('phone'),
                    data.get('email'),
                    data.get('education'),
                    data.get('work_experience'),
                    json.dumps(data.get('skills', [])),
                    json.dumps(data.get('projects', [])),
                    data.get('raw_text'),
                    data.get('file_url')
                )
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_id(resume_id: int) -> Optional[dict]:
        """根据ID获取简历"""
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
            row = cursor.fetchone()
            result = dict_from_row(row)
            if result and result.get('skills'):
                result['skills'] = json.loads(result['skills'])
            if result and result.get('projects'):
                result['projects'] = json.loads(result['projects'])
            return result

    @staticmethod
    def get_by_user(user_id: int) -> List[dict]:
        """获取用户的所有简历"""
        with get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM resumes WHERE user_id = ? ORDER BY is_default DESC, created_at DESC',
                (user_id,)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict_from_row(row)
                if result.get('skills'):
                    result['skills'] = json.loads(result['skills'])
                if result.get('projects'):
                    result['projects'] = json.loads(result['projects'])
                results.append(result)
            return results

    @staticmethod
    def update(resume_id: int, **kwargs) -> bool:
        """更新简历"""
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'phone', 'email', 'education', 'work_experience', 'skills', 'projects', 'raw_text', 'file_url']:
                fields.append(f"{key} = ?")
                if key in ['skills', 'projects'] and isinstance(value, (list, dict)):
                    value = json.dumps(value)
                values.append(value)
        
        if not fields:
            return False

        values.append(resume_id)
        sql = f"UPDATE resumes SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        with get_connection() as conn:
            cursor = conn.execute(sql, values)
            return cursor.rowcount > 0

    @staticmethod
    def delete(resume_id: int) -> bool:
        """删除简历"""
        with get_connection() as conn:
            cursor = conn.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
            return cursor.rowcount > 0

    @staticmethod
    def set_default(user_id: int, resume_id: int) -> bool:
        """设置默认简历"""
        with get_connection() as conn:
            # 先取消所有默认
            conn.execute('UPDATE resumes SET is_default = 0 WHERE user_id = ?', (user_id,))
            # 设置新的默认
            cursor = conn.execute('UPDATE resumes SET is_default = 1 WHERE id = ? AND user_id = ?', 
                                 (resume_id, user_id))
            return cursor.rowcount > 0


class InterviewDAO:
    """面试记录数据访问对象"""

    @staticmethod
    def create(user_id: int, position: str, resume_id: int = None, 
               level: str = '中级', mode: str = '语音') -> int:
        """创建面试记录"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO interviews 
                (user_id, resume_id, position, level, mode, status, started_at)
                VALUES (?, ?, ?, ?, ?, 'ongoing', CURRENT_TIMESTAMP)''',
                (user_id, resume_id, position, level, mode)
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_id(interview_id: int) -> Optional[dict]:
        """根据ID获取面试记录"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''SELECT i.*, r.name as resume_name 
                FROM interviews i 
                LEFT JOIN resumes r ON i.resume_id = r.id 
                WHERE i.id = ?''',
                (interview_id,)
            )
            return dict_from_row(cursor.fetchone())

    @staticmethod
    def get_by_user(user_id: int, limit: int = 20, offset: int = 0) -> List[dict]:
        """获取用户的所有面试记录"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''SELECT i.*, r.name as resume_name,
                   (SELECT content FROM messages WHERE interview_id = i.id AND role = 'assistant' LIMIT 1) as first_question
                FROM interviews i 
                LEFT JOIN resumes r ON i.resume_id = r.id 
                WHERE i.user_id = ? 
                ORDER BY i.created_at DESC 
                LIMIT ? OFFSET ?''',
                (user_id, limit, offset)
            )
            return [dict_from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def update(interview_id: int, **kwargs) -> bool:
        """更新面试记录"""
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['status', 'duration', 'level', 'mode']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False

        values.append(interview_id)
        sql = f"UPDATE interviews SET {', '.join(fields)} WHERE id = ?"
        
        with get_connection() as conn:
            cursor = conn.execute(sql, values)
            return cursor.rowcount > 0

    @staticmethod
    def end(interview_id: int, duration: int = 0) -> bool:
        """结束面试"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''UPDATE interviews 
                SET status = 'completed', ended_at = CURRENT_TIMESTAMP, duration = ?
                WHERE id = ?''',
                (duration, interview_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete(interview_id: int) -> bool:
        """删除面试记录"""
        with get_connection() as conn:
            cursor = conn.execute('DELETE FROM interviews WHERE id = ?', (interview_id,))
            return cursor.rowcount > 0

    @staticmethod
    def get_stats(user_id: int) -> dict:
        """获取用户面试统计"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'ongoing' THEN 1 ELSE 0 END) as ongoing,
                    AVG(duration) as avg_duration
                FROM interviews WHERE user_id = ?''',
                (user_id,)
            )
            row = cursor.fetchone()
            return dict_from_row(row)


class MessageDAO:
    """对话消息数据访问对象"""

    @staticmethod
    def create(interview_id: int, role: str, content: str, 
               audio_url: str = None, audio_duration: float = 0) -> int:
        """创建消息"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO messages (interview_id, role, content, audio_url, audio_duration)
                VALUES (?, ?, ?, ?, ?)''',
                (interview_id, role, content, audio_url, audio_duration)
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_interview(interview_id: int) -> List[dict]:
        """获取面试的所有消息"""
        with get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM messages WHERE interview_id = ? ORDER BY created_at ASC',
                (interview_id,)
            )
            return [dict_from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def get_conversation_text(interview_id: int) -> str:
        """获取对话文本（用于生成报告）"""
        messages = MessageDAO.get_by_interview(interview_id)
        text_parts = []
        for msg in messages:
            role = "面试官" if msg['role'] == 'assistant' else "候选人"
            text_parts.append(f"【{role}】{msg['content']}")
        return "\n\n".join(text_parts)


class ReportDAO:
    """评估报告数据访问对象"""

    @staticmethod
    def create(interview_id: int, user_id: int, data: dict) -> int:
        """创建评估报告"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO reports 
                (interview_id, user_id, overall_score, technical_score, project_score,
                 communication_score, logic_score, pressure_score, 
                 strengths, weaknesses, suggestions, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    interview_id, user_id,
                    data.get('overall_score', 0),
                    data.get('technical_score', 0),
                    data.get('project_score', 0),
                    data.get('communication_score', 0),
                    data.get('logic_score', 0),
                    data.get('pressure_score', 0),
                    data.get('strengths'),
                    data.get('weaknesses'),
                    data.get('suggestions'),
                    json.dumps(data.get('feedback', {}))
                )
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_id(report_id: int) -> Optional[dict]:
        """根据ID获取报告"""
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
            row = cursor.fetchone()
            if row:
                result = dict_from_row(row)
                if result.get('feedback'):
                    result['feedback'] = json.loads(result['feedback'])
                return result
            return None

    @staticmethod
    def get_by_interview(interview_id: int) -> Optional[dict]:
        """根据面试ID获取报告"""
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM reports WHERE interview_id = ?', (interview_id,))
            row = cursor.fetchone()
            if row:
                result = dict_from_row(row)
                if result.get('feedback'):
                    result['feedback'] = json.loads(result['feedback'])
                return result
            return None

    @staticmethod
    def get_by_user(user_id: int, limit: int = 20, offset: int = 0) -> List[dict]:
        """获取用户的所有报告"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''SELECT r.*, i.position, i.level, i.duration
                FROM reports r
                JOIN interviews i ON r.interview_id = i.id
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC
                LIMIT ? OFFSET ?''',
                (user_id, limit, offset)
            )
            return [dict_from_row(row) for row in cursor.fetchall()]


class FavoriteQuestionDAO:
    """收藏问题数据访问对象"""

    @staticmethod
    def create(user_id: int, interview_id: int, question: str, 
               answer: str = None, notes: str = None) -> int:
        """收藏问题"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO favorited_questions (user_id, interview_id, question, answer, notes)
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, interview_id, question, answer, notes)
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_user(user_id: int) -> List[dict]:
        """获取用户收藏的所有问题"""
        with get_connection() as conn:
            cursor = conn.execute(
                '''SELECT fq.*, i.position
                FROM favorited_questions fq
                LEFT JOIN interviews i ON fq.interview_id = i.id
                WHERE fq.user_id = ?
                ORDER BY fq.created_at DESC''',
                (user_id,)
            )
            return [dict_from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def delete(question_id: int) -> bool:
        """取消收藏"""
        with get_connection() as conn:
            cursor = conn.execute('DELETE FROM favorited_questions WHERE id = ?', (question_id,))
            return cursor.rowcount > 0
