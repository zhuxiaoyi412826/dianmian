<template>
  <div class="interview-page" :class="{ 'text-hidden': !store.showText }">
    <!-- 顶部状态栏 -->
    <header class="interview-header safe-area-top">
      <div class="header-left">
        <button class="btn btn-icon" @click="goBack">‹</button>
      </div>
      <div class="header-center">
        <div class="interview-info">
          <span class="position-name">{{ store.currentInterview.position }}</span>
          <span class="interview-time">{{ store.interviewDuration }}</span>
        </div>
      </div>
      <div class="header-right">
        <button class="btn btn-icon" @click="showSettings = true">⚙️</button>
      </div>
    </header>

    <!-- 通话状态指示 -->
    <div class="call-status" v-if="!store.showText">
      <div class="avatar-container">
        <div class="avatar" :class="{ speaking: isAISpeaking }">🤖</div>
        <div class="status-dot" :class="{ recording: store.isRecording }"></div>
      </div>
      <p class="status-text">{{ statusText }}</p>
      <p class="status-hint">{{ statusHint }}</p>
    </div>

    <!-- 聊天消息区域 -->
    <div class="messages-container" v-show="store.showText" ref="messagesContainer">
      <div class="messages-list">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-avatar">🤖</div>
          <div class="welcome-text">
            <p>您好，我是您的AI面试官。</p>
            <p>我将根据您的简历和岗位要求进行面试。</p>
            <p>请准备好后，点击下方麦克风开始。</p>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-avatar" v-if="msg.role === 'assistant'">🤖</div>
          <div class="message-content">
            <div class="message-bubble">{{ msg.content }}</div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <!-- AI正在输入 -->
        <div v-if="isLoading" class="message-item assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-bubble loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部控制区 -->
    <div class="control-panel safe-area-bottom">
      <!-- 文字显示切换 -->
      <div class="text-toggle">
        <button class="toggle-btn" @click="store.showText = !store.showText">
          {{ store.showText ? '🙈 隐藏文字' : '👁️ 显示文字' }}
        </button>
      </div>

      <!-- 录音状态 -->
      <div class="recording-indicator" v-if="isRecordingAudio">
        <span class="recording-dot"></span>
        <span>正在录音...</span>
        <span class="recording-time">{{ recordingDuration }}</span>
      </div>

      <!-- 文字输入框 -->
      <div class="text-input-container" v-show="store.showText">
        <input
          v-model="textInput"
          type="text"
          class="text-input"
          placeholder="输入文字回答..."
          @keyup.enter="sendTextMessage"
          :disabled="isLoading || isRecordingAudio"
        />
        <button
          class="send-btn"
          @click="sendTextMessage"
          :disabled="!textInput.trim() || isLoading || isRecordingAudio"
        >
          ➤
        </button>
      </div>

      <!-- 主控制按钮 -->
      <div class="main-controls">
        <!-- 静音 -->
        <button
          class="btn btn-icon control-btn"
          :class="{ active: store.isMuted }"
          @click="toggleMute"
        >
          {{ store.isMuted ? '🔇' : '🔊' }}
        </button>

        <!-- 麦克风（主要） -->
        <button
          class="btn btn-icon large primary-btn"
          :class="{ recording: isRecordingAudio, speaking: isAISpeaking }"
          @mousedown="startRecording"
          @mouseup="stopRecording"
          @touchstart.prevent="startRecording"
          @touchend.prevent="stopRecording"
          @click="toggleRecording"
        >
          {{ isRecordingAudio ? '⏹️' : '🎤' }}
        </button>

        <!-- 免提 -->
        <button
          class="btn btn-icon control-btn"
          :class="{ active: store.isHandsfree }"
          @click="toggleHandsfree"
        >
          📞
        </button>
      </div>

      <!-- 次要操作 -->
      <div class="secondary-controls">
        <button class="action-btn" @click="replayLastQuestion" :disabled="messages.length === 0">
          🔄 重播
        </button>
        <button class="action-btn" @click="pauseInterview" :disabled="!store.isInterviewing">
          ⏸️ 暂停
        </button>
        <button class="action-btn end-btn" @click="endInterview">
          📴 结束
        </button>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <div class="modal-overlay" v-if="showSettings" @click="showSettings = false">
      <div class="modal-content" @click.stop>
        <h3>面试设置</h3>
        
        <div class="setting-item">
          <label>语音音色</label>
          <div class="voice-options">
            <button
              v-for="v in voiceOptions"
              :key="v.value"
              :class="{ active: settings.voice === v.value }"
              @click="settings.voice = v.value"
            >
              {{ v.icon }} {{ v.name }}
            </button>
          </div>
        </div>

        <div class="setting-item">
          <label>语速: {{ settings.speed }}x</label>
          <input type="range" v-model="settings.speed" min="0.5" max="2" step="0.1">
        </div>

        <div class="setting-item">
          <label>面试模式</label>
          <div class="mode-options">
            <button :class="{ active: interviewMode === 'interview' }" @click="interviewMode = 'interview'">
              🎯 模拟面试
            </button>
            <button :class="{ active: interviewMode === 'assist' }" @click="interviewMode = 'assist'">
              💡 辅助模式
            </button>
          </div>
        </div>

        <button class="btn btn-primary" @click="showSettings = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import { chatCompletion, textToSpeech, speechToText } from '../api'

const router = useRouter()
const store = useInterviewStore()

// 状态
const messages = ref([])
const isLoading = ref(false)
const isRecordingAudio = ref(false)
const isAISpeaking = ref(false)
const showSettings = ref(false)
const interviewMode = ref('interview')
const messagesContainer = ref(null)
const textInput = ref('')

// 录音相关
let mediaRecorder = null
let audioChunks = []
let recordingStartTime = null
let recordingTimer = null
const recordingDuration = ref('00:00')

// 设置
const settings = ref({ ...store.settings })
const voiceOptions = [
  { value: 'female', name: '女声', icon: '👩' },
  { value: 'male', name: '男声', icon: '👨' },
  { value: 'professional', name: '专业', icon: '👔' }
]

// 状态文本
const statusText = computed(() => {
  if (isAISpeaking.value) return 'AI面试官正在说话...'
  if (isRecordingAudio.value) return '正在聆听您的回答...'
  if (isLoading.value) return 'AI正在思考...'
  return '准备就绪'
})

const statusHint = computed(() => {
  if (isAISpeaking.value) return '点击麦克风可打断'
  if (isRecordingAudio.value) return '请开始回答'
  return '点击麦克风开始面试'
})

// 格式化时间
const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 返回
const goBack = () => {
  if (store.isInterviewing) {
    if (confirm('面试进行中，确定要退出吗？')) {
      store.endInterview()
      router.back()
    }
  } else {
    router.back()
  }
}

// 切换静音
const toggleMute = () => {
  store.isMuted = !store.isMuted
}

// 切换免提
const toggleHandsfree = () => {
  store.isHandsfree = !store.isHandsfree
}

// 开始录音
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    
    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data)
    }
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      await processAudio(audioBlob)
      stream.getTracks().forEach(track => track.stop())
    }
    
    mediaRecorder.start()
    isRecordingAudio.value = true
    recordingStartTime = Date.now()
    
    // 更新录音时长
    recordingTimer = setInterval(() => {
      const diff = Date.now() - recordingStartTime
      const s = Math.floor(diff / 1000)
      recordingDuration.value = `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`
    }, 1000)
    
  } catch (err) {
    console.error('录音失败:', err)
    alert('无法访问麦克风，请检查权限设置')
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop()
    isRecordingAudio.value = false
    clearInterval(recordingTimer)
  }
}

// 切换录音
const toggleRecording = () => {
  if (isRecordingAudio.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 处理音频
const processAudio = async (audioBlob) => {
  try {
    // 语音转文字
    const text = await speechToText(audioBlob)
    
    if (text) {
      // 添加用户消息
      addMessage('user', text)
      
      // 发送到AI
      await sendToAI(text)
    }
  } catch (err) {
    console.error('处理音频失败:', err)
    addMessage('assistant', '抱歉，我没有听清楚，请再说一遍。')
    playTTS('抱歉，我没有听清楚，请再说一遍。')
  }
}

// 添加消息
const addMessage = (role, content) => {
  messages.value.push({
    id: Date.now(),
    role,
    content,
    timestamp: new Date()
  })
  scrollToBottom()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 发送文字消息
const sendTextMessage = async () => {
  if (!textInput.value.trim() || isLoading.value || isRecordingAudio.value) return
  
  const text = textInput.value.trim()
  textInput.value = ''
  
  // 添加用户消息
  addMessage('user', text)
  
  // 发送到AI
  await sendToAI(text)
}

// 发送到AI
const sendToAI = async (userMessage) => {
  isLoading.value = true
  
  try {
    const conversationMessages = messages.value.map(m => ({
      role: m.role,
      content: m.content
    }))
    
    // 收集流式响应
    let fullResponse = ''
    
    await chatCompletion(conversationMessages, true, (chunk) => {
      fullResponse += chunk
      // 实时更新消息
      if (messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'assistant') {
        messages.value[messages.value.length - 1].content = fullResponse
      } else {
        addMessage('assistant', fullResponse)
      }
    })
    
    // 确保有AI消息
    if (messages.value[messages.value.length - 1]?.role !== 'assistant') {
      addMessage('assistant', fullResponse)
    } else {
      messages.value[messages.value.length - 1].content = fullResponse
    }
    
    // 播放TTS（可选，失败不影响对话）
    if (store.settings.enableTTS !== false) {
      playTTS(fullResponse).catch(e => {
        console.warn('TTS播放被跳过或失败:', e)
        // TTS失败不影响核心功能
      })
    }
    
  } catch (err) {
    console.error('AI响应失败:', err)
    addMessage('assistant', '抱歉，服务出现问题，请稍后重试。')
  } finally {
    isLoading.value = false
  }
}

// 播放TTS（简化版本）
const playTTS = async (text) => {
  try {
    isAISpeaking.value = true
    const audioUrl = await textToSpeech(text, settings.value.voice)
    
    if (!audioUrl || audioUrl === 'undefined') {
      throw new Error('音频URL无效')
    }
    
    const audio = new Audio(audioUrl)
    audio.playbackRate = settings.value.speed
    
    if (store.isMuted) {
      audio.muted = true
    }
    
    audio.onended = () => {
      isAISpeaking.value = false
    }
    
    audio.onerror = () => {
      console.warn('音频播放失败')
      isAISpeaking.value = false
    }
    
    await audio.play()
  } catch (err) {
    console.warn('TTS播放失败:', err)
    isAISpeaking.value = false
  }
}

// 重播上一题
const replayLastQuestion = () => {
  const lastAI = [...messages.value].reverse().find(m => m.role === 'assistant')
  if (lastAI) {
    playTTS(lastAI.content)
  }
}

// 暂停面试
const pauseInterview = () => {
  store.isPaused = !store.isPaused
  isAISpeaking.value = false
}

// 结束面试
const endInterview = () => {
  if (confirm('确定要结束面试吗？')) {
    store.endInterview()
    store.currentInterview.messages = messages.value
    router.push('/report/new')
  }
}

// 监听设置变化
watch(settings, (val) => {
  Object.assign(store.settings, val)
  store.saveSettings()
}, { deep: true })

onMounted(() => {
  store.initSettings()
  
  // 初始化欢迎消息
  if (store.currentInterview.position) {
    addMessage('assistant', `您好，我是您的AI面试官。今天我们将进行${store.currentInterview.position}的面试。请问您准备好了吗？准备好后，请点击麦克风开始。`)
  }
})

onUnmounted(() => {
  if (mediaRecorder) {
    mediaRecorder.stream?.getTracks().forEach(track => track.stop())
  }
  clearInterval(recordingTimer)
})
</script>

<style lang="scss" scoped>
.interview-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: white;
  
  &.text-hidden {
    .messages-container {
      display: none;
    }
  }
}

.interview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  
  .header-left, .header-right {
    width: 44px;
  }
  
  .header-center {
    flex: 1;
    text-align: center;
    
    .interview-info {
      display: flex;
      flex-direction: column;
      
      .position-name {
        font-size: 16px;
        font-weight: 600;
      }
      
      .interview-time {
        font-size: 12px;
        opacity: 0.7;
      }
    }
  }
  
  .btn-icon {
    background: rgba(255, 255, 255, 0.1);
    font-size: 20px;
  }
}

.call-status {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  .avatar-container {
    position: relative;
    margin-bottom: 20px;
    
    .avatar {
      width: 120px;
      height: 120px;
      background: rgba(102, 126, 234, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 60px;
      transition: all 0.3s;
      
      &.speaking {
        background: rgba(102, 126, 234, 0.4);
        animation: pulse 1.5s infinite;
      }
    }
    
    .status-dot {
      position: absolute;
      bottom: 10px;
      right: 10px;
      width: 16px;
      height: 16px;
      background: #718096;
      border-radius: 50%;
      border: 3px solid #1a1a2e;
      
      &.recording {
        background: #f56565;
        animation: pulse 1s infinite;
      }
    }
  }
  
  .status-text {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  
  .status-hint {
    font-size: 14px;
    opacity: 0.7;
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
  }
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  
  .welcome-avatar {
    font-size: 36px;
  }
  
  .welcome-text {
    p {
      margin-bottom: 8px;
      line-height: 1.6;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.message-item {
  display: flex;
  gap: 10px;
  max-width: 85%;
  
  &.user {
    align-self: flex-end;
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-bubble {
      background: var(--primary-color);
      color: white;
      border-radius: 18px 18px 4px 18px;
    }
  }
  
  &.assistant {
    align-self: flex-start;
    
    .message-bubble {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 18px 18px 18px 4px;
    }
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    background: rgba(102, 126, 234, 0.3);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }
  
  .message-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .message-bubble {
      padding: 12px 16px;
      font-size: 15px;
      line-height: 1.5;
      
      &.loading {
        display: flex;
        gap: 4px;
        padding: 16px 20px;
        
        .dot {
          width: 8px;
          height: 8px;
          background: rgba(255, 255, 255, 0.5);
          border-radius: 50%;
          animation: bounce 1.4s infinite;
          
          &:nth-child(2) { animation-delay: 0.2s; }
          &:nth-child(3) { animation-delay: 0.4s; }
        }
      }
    }
    
    .message-time {
      font-size: 11px;
      opacity: 0.5;
    }
  }
}

.control-panel {
  padding: 16px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  
  .text-input-container {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    
    .text-input {
      flex: 1;
      padding: 12px 16px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: var(--radius-lg);
      color: white;
      font-size: 14px;
      outline: none;
      transition: all 0.3s;
      
      &::placeholder {
        color: rgba(255, 255, 255, 0.4);
      }
      
      &:focus {
        border-color: var(--primary-color);
        background: rgba(255, 255, 255, 0.15);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
    
    .send-btn {
      padding: 12px 20px;
      background: var(--primary-color);
      border: none;
      border-radius: var(--radius-lg);
      color: white;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover:not(:disabled) {
        background: var(--primary-color-dark);
      }
      
      &:disabled {
        background: rgba(255, 255, 255, 0.2);
        cursor: not-allowed;
      }
    }
  }
  
  .text-toggle {
    text-align: center;
    margin-bottom: 12px;
    
    .toggle-btn {
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: white;
      padding: 8px 16px;
      border-radius: var(--radius-full);
      font-size: 13px;
      cursor: pointer;
    }
  }
  
  .recording-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 13px;
    color: #f56565;
    
    .recording-dot {
      width: 8px;
      height: 8px;
      background: #f56565;
      border-radius: 50%;
      animation: pulse 1s infinite;
    }
    
    .recording-time {
      font-weight: 600;
    }
  }
  
  .main-controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    margin-bottom: 16px;
    
    .control-btn {
      background: rgba(255, 255, 255, 0.1);
      font-size: 20px;
      
      &.active {
        background: rgba(102, 126, 234, 0.3);
      }
    }
    
    .primary-btn {
      width: 72px;
      height: 72px;
      background: var(--primary-color);
      font-size: 32px;
      box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
      
      &.recording {
        background: #f56565;
        animation: pulse 1s infinite;
      }
      
      &.speaking {
        background: var(--success-color);
      }
    }
  }
  
  .secondary-controls {
    display: flex;
    justify-content: center;
    gap: 16px;
    
    .action-btn {
      background: transparent;
      border: none;
      color: white;
      font-size: 13px;
      padding: 8px 12px;
      border-radius: var(--radius-full);
      cursor: pointer;
      opacity: 0.8;
      
      &:disabled {
        opacity: 0.4;
      }
      
      &:active {
        background: rgba(255, 255, 255, 0.1);
      }
      
      &.end-btn {
        color: #f56565;
      }
    }
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  background: #1a1a2e;
  border-radius: 24px 24px 0 0;
  padding: 24px;
  color: white;
  
  h3 {
    font-size: 18px;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .setting-item {
    margin-bottom: 20px;
    
    label {
      display: block;
      font-size: 14px;
      color: rgba(255, 255, 255, 0.7);
      margin-bottom: 10px;
    }
    
    input[type="range"] {
      width: 100%;
      accent-color: var(--primary-color);
    }
    
    .voice-options, .mode-options {
      display: flex;
      gap: 10px;
      
      button {
        flex: 1;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid transparent;
        border-radius: var(--radius-md);
        color: white;
        font-size: 13px;
        cursor: pointer;
        
        &.active {
          border-color: var(--primary-color);
          background: rgba(102, 126, 234, 0.2);
        }
      }
    }
  }
  
  .btn-primary {
    width: 100%;
    margin-top: 10px;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
</style>
