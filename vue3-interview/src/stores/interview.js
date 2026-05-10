import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useInterviewStore = defineStore('interview', () => {
  // 状态
  const isInterviewing = ref(false)
  const isPaused = ref(false)
  const isMuted = ref(false)
  const isHandsfree = ref(false) // 免提
  const showText = ref(true) // 显示对话文本
  const isRecording = ref(false)
  
  // 当前面试信息
  const currentInterview = ref({
    id: null,
    position: '',
    level: '',
    startTime: null,
    resume: null,
    messages: [],
    audioRecord: null
  })
  
  // 设置
  const settings = ref({
    voice: 'female', // female, male, professional
    speed: 1.0, // 0.5 - 2.0
    theme: 'purple', // purple, blue, green, dark
    defaultPosition: '',
    defaultLevel: 'middle'
  })
  
  // 初始化设置
  const initSettings = () => {
    const saved = localStorage.getItem('interview_settings')
    if (saved) {
      settings.value = { ...settings.value, ...JSON.parse(saved) }
    }
  }
  
  // 保存设置
  const saveSettings = () => {
    localStorage.setItem('interview_settings', JSON.stringify(settings.value))
  }
  
  // 开始面试
  const startInterview = (position, level, resume = null) => {
    currentInterview.value = {
      id: Date.now().toString(),
      position,
      level,
      startTime: new Date(),
      resume,
      messages: [],
      audioRecord: null
    }
    isInterviewing.value = true
    isPaused.value = false
    isRecording.value = true
  }
  
  // 结束面试
  const endInterview = () => {
    isInterviewing.value = false
    isPaused.value = false
    isRecording.value = false
  }
  
  // 添加消息
  const addMessage = (role, content, audioUrl = null) => {
    currentInterview.value.messages.push({
      id: Date.now(),
      role,
      content,
      audioUrl,
      timestamp: new Date()
    })
  }
  
  // 计算属性
  const interviewDuration = computed(() => {
    if (!currentInterview.value.startTime) return '00:00'
    const diff = Date.now() - new Date(currentInterview.value.startTime).getTime()
    const minutes = Math.floor(diff / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })
  
  return {
    // 状态
    isInterviewing,
    isPaused,
    isMuted,
    isHandsfree,
    showText,
    isRecording,
    currentInterview,
    settings,
    // 方法
    initSettings,
    saveSettings,
    startInterview,
    endInterview,
    addMessage,
    interviewDuration
  }
})
