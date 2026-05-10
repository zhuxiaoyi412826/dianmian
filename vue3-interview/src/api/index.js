import axios from 'axios'

// API 配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 生成或获取 session_id
let sessionId = localStorage.getItem('chat_session_id') || generateSessionId()
localStorage.setItem('chat_session_id', sessionId)

function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 对话接口 - 非流式
export const chatCompletion = async (messages, stream = true, onChunk = null) => {
  // 将前端消息格式转换为后端期望的格式
  // 后端期望的格式: { type: 'human' | 'assistant', content: '...' }
  const apiMessages = messages.map(msg => ({
    type: msg.role === 'user' ? 'human' : 'assistant',
    content: msg.content
  }))
  
  // 调试：打印发送的消息格式
  console.log('Sending messages to API:', JSON.stringify(apiMessages, null, 2))
  
  if (!stream) {
    const response = await api.post('/v1/chat/completions', {
      model: 'interview-assistant',
      messages: apiMessages,
      stream: false,
      session_id: sessionId
    })
    return response.data
  }

  // 流式响应使用 fetch API（浏览器端不支持 axios stream）
  const payload = {
    model: 'interview-assistant',
    messages: apiMessages,
    stream: true,
    session_id: sessionId
  }
  
  console.log('Full payload:', JSON.stringify(payload, null, 2))
  
  const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    // 尝试获取错误详情
    let errorDetail = ''
    try {
      const errorResponse = await response.json()
      errorDetail = JSON.stringify(errorResponse)
    } catch (e) {
      errorDetail = await response.text()
    }
    console.error('API Error:', response.status, errorDetail)
    throw new Error(`HTTP error! status: ${response.status}, detail: ${errorDetail}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    
    // 按 SSE 格式解析
    const lines = buffer.split('\n\n')
    buffer = lines.pop() // 保留不完整的最后一行
    
    for (const line of lines) {
      const trimmedLine = line.trim()
      if (!trimmedLine) continue
      
      // 解析 data: 前缀（兼容带空格和不带空格）
      let dataStr = ''
      if (trimmedLine.startsWith('data: ')) {
        dataStr = trimmedLine.slice(6).trim()
      } else if (trimmedLine.startsWith('data:')) {
        dataStr = trimmedLine.slice(5).trim()
      }
      
      if (!dataStr) continue
      if (dataStr === '[DONE]') continue
      
      try {
        const data = JSON.parse(dataStr)
        if (data.choices && data.choices[0]?.delta?.content) {
          onChunk?.(data.choices[0].delta.content)
        }
      } catch (e) {
        console.warn('Failed to parse chunk:', e, 'raw:', dataStr)
      }
    }
  }
}

// TTS语音合成
export const textToSpeech = async (text, voice = 'female') => {
  const response = await api.post('/tts', {
    text,
    voice
  }, {
    responseType: 'blob'
  })
  return URL.createObjectURL(response.data)
}

// ASR语音识别
export const speechToText = async (audioBlob) => {
  const formData = new FormData()
  formData.append('file', audioBlob)
  const response = await api.post('/asr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data.text
}

// 简历上传解析
export const uploadResume = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload_resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

// 简历文本解析
export const analyzeResumeText = async (resumeText) => {
  const response = await api.post('/analyze_resume', {
    resume_text: resumeText
  })
  return response.data
}

// 生成面试报告
export const generateReport = async (conversationHistory, candidateBackground) => {
  const response = await api.post('/generate_report', {
    conversation_history: conversationHistory,
    candidate_background: candidateBackground
  })
  return response.data
}

// 获取面试历史
export const getInterviewHistory = async () => {
  const response = await api.get('/interview_history')
  return response.data
}

// 保存面试记录
export const saveInterview = async (data) => {
  const response = await api.post('/save_interview', data)
  return response.data
}

export default api
