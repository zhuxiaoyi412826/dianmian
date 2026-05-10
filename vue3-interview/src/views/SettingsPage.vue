<template>
  <div class="settings-page page-container">
    <header class="page-header">
      <h1 class="page-title">⚙️ 设置</h1>
    </header>

    <!-- 语音设置 -->
    <section class="settings-section card">
      <h3 class="section-title">🎤 语音设置</h3>
      
      <div class="setting-item">
        <div class="setting-label">
          <span>语音音色</span>
          <span class="setting-value">{{ getVoiceName(settings.voice) }}</span>
        </div>
        <div class="voice-options">
          <button
            v-for="v in voiceOptions"
            :key="v.value"
            :class="{ active: settings.voice === v.value }"
            @click="updateSetting('voice', v.value)"
          >
            <span class="voice-icon">{{ v.icon }}</span>
            <span class="voice-name">{{ v.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="setting-item">
        <div class="setting-label">
          <span>语速</span>
          <span class="setting-value">{{ settings.speed }}x</span>
        </div>
        <input
          type="range"
          min="0.5"
          max="2"
          step="0.1"
          :value="settings.speed"
          @input="updateSetting('speed', parseFloat($event.target.value))"
        >
        <div class="range-labels">
          <span>慢</span>
          <span>正常</span>
          <span>快</span>
        </div>
      </div>
    </section>

    <!-- 面试设置 -->
    <section class="settings-section card">
      <h3 class="section-title">🎯 面试设置</h3>
      
      <div class="setting-item">
        <span class="setting-label">默认岗位</span>
        <select v-model="settings.defaultPosition" @change="saveSettings">
          <option value="">请选择</option>
          <option value="java">Java后端</option>
          <option value="python">Python后端</option>
          <option value="frontend">前端开发</option>
          <option value="product">产品经理</option>
          <option value="operation">运营</option>
        </select>
      </div>
      
      <div class="setting-item">
        <span class="setting-label">默认职级</span>
        <select v-model="settings.defaultLevel" @change="saveSettings">
          <option value="junior">初级</option>
          <option value="middle">中级</option>
          <option value="senior">高级</option>
        </select>
      </div>
      
      <div class="setting-item">
        <span class="setting-label">面试模式</span>
        <div class="mode-toggle">
          <button
            :class="{ active: settings.interviewMode === 'interview' }"
            @click="updateSetting('interviewMode', 'interview')"
          >
            🎯 模拟面试
          </button>
          <button
            :class="{ active: settings.interviewMode === 'assist' }"
            @click="updateSetting('interviewMode', 'assist')"
          >
            💡 辅助模式
          </button>
        </div>
      </div>
    </section>

    <!-- 显示设置 -->
    <section class="settings-section card">
      <h3 class="section-title">🎨 显示设置</h3>
      
      <div class="setting-item">
        <span class="setting-label">主题颜色</span>
        <div class="theme-options">
          <button
            v-for="t in themes"
            :key="t.value"
            :class="['theme-btn', { active: settings.theme === t.value }]"
            :style="{ background: t.color }"
            @click="updateSetting('theme', t.value)"
          >
            <span v-if="settings.theme === t.value">✓</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 权限管理 -->
    <section class="settings-section card">
      <h3 class="section-title">🔐 权限管理</h3>
      
      <div class="permission-list">
        <div class="permission-item">
          <div class="permission-info">
            <span class="permission-icon">🎙️</span>
            <div class="permission-text">
              <span class="permission-name">麦克风权限</span>
              <span class="permission-desc">用于语音输入和录音</span>
            </div>
          </div>
          <button
            class="permission-btn"
            :class="{ granted: micGranted }"
            @click="requestMicPermission"
          >
            {{ micGranted ? '已授权' : '授权' }}
          </button>
        </div>
        
        <div class="permission-item">
          <div class="permission-info">
            <span class="permission-icon">📢</span>
            <div class="permission-text">
              <span class="permission-name">通知权限</span>
              <span class="permission-desc">接收面试提醒</span>
            </div>
          </div>
          <button
            class="permission-btn"
            :class="{ granted: notifGranted }"
            @click="requestNotifPermission"
          >
            {{ notifGranted ? '已授权' : '授权' }}
          </button>
        </div>
      </div>
    </section>

    <!-- 关于 -->
    <section class="settings-section card">
      <h3 class="section-title">ℹ️ 关于</h3>
      
      <div class="about-list">
        <div class="about-item" @click="showPrivacy = true">
          <span>隐私政策</span>
          <span class="arrow">›</span>
        </div>
        <div class="about-item" @click="showTerms = true">
          <span>用户协议</span>
          <span class="arrow">›</span>
        </div>
        <div class="about-item">
          <span>版本号</span>
          <span class="version">v1.0.0</span>
        </div>
      </div>
    </section>

    <!-- 弹窗 -->
    <div class="modal-overlay" v-if="showPrivacy || showTerms" @click="showPrivacy = showTerms = false">
      <div class="modal-content" @click.stop>
        <h3>{{ showPrivacy ? '隐私政策' : '用户协议' }}</h3>
        <div class="modal-body">
          <p>这里是{{ showPrivacy ? '隐私政策' : '用户协议' }}的内容...</p>
          <p>我们非常重视您的隐私保护。所有面试数据和录音都存储在本地设备上，不会上传到服务器。</p>
        </div>
        <button class="btn btn-primary" @click="showPrivacy = showTerms = false">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useInterviewStore } from '../stores/interview'

const store = useInterviewStore()

// 设置
const settings = ref({ ...store.settings })
const showPrivacy = ref(false)
const showTerms = ref(false)

// 权限状态
const micGranted = ref(false)
const notifGranted = ref(false)

// 选项
const voiceOptions = [
  { value: 'female', name: '女声', icon: '👩' },
  { value: 'male', name: '男声', icon: '👨' },
  { value: 'professional', name: '专业', icon: '👔' }
]

const themes = [
  { value: 'purple', color: '#667eea' },
  { value: 'blue', color: '#4299e1' },
  { value: 'green', color: '#48bb78' },
  { value: 'dark', color: '#1a202c' }
]

// 获取语音名称
const getVoiceName = (value) => {
  const voice = voiceOptions.find(v => v.value === value)
  return voice ? `${voice.icon} ${voice.name}` : value
}

// 更新设置
const updateSetting = (key, value) => {
  settings.value[key] = value
  store.settings[key] = value
  store.saveSettings()
}

// 保存设置
const saveSettings = () => {
  store.saveSettings()
}

// 请求麦克风权限
const requestMicPermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    micGranted.value = true
    stream.getTracks().forEach(track => track.stop())
  } catch (err) {
    alert('麦克风权限获取失败，请检查浏览器设置')
  }
}

// 请求通知权限
const requestNotifPermission = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission()
    notifGranted.value = permission === 'granted'
  }
}

onMounted(() => {
  store.initSettings()
  settings.value = { ...store.settings }
})
</script>

<style lang="scss" scoped>
.settings-page {
  background: var(--bg-gray);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.settings-section {
  margin-bottom: 16px;
}

.setting-item {
  margin-bottom: 20px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .setting-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    margin-bottom: 10px;
    
    .setting-value {
      color: var(--text-secondary);
    }
  }
  
  input[type="range"] {
    width: 100%;
    accent-color: var(--primary-color);
  }
  
  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 4px;
  }
  
  select {
    width: 100%;
    padding: 12px;
    border: 2px solid #e2e8f0;
    border-radius: var(--radius-md);
    font-size: 14px;
    background: white;
    
    &:focus {
      outline: none;
      border-color: var(--primary-color);
    }
  }
}

.voice-options {
  display: flex;
  gap: 10px;
  
  button {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 14px 8px;
    background: var(--bg-gray);
    border: 2px solid transparent;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
    
    .voice-icon {
      font-size: 24px;
      margin-bottom: 4px;
    }
    
    .voice-name {
      font-size: 12px;
    }
    
    &.active {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.1);
    }
  }
}

.mode-toggle {
  display: flex;
  gap: 10px;
  
  button {
    flex: 1;
    padding: 12px;
    background: var(--bg-gray);
    border: 2px solid transparent;
    border-radius: var(--radius-md);
    font-size: 14px;
    cursor: pointer;
    
    &.active {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.1);
      color: var(--primary-color);
    }
  }
}

.theme-options {
  display: flex;
  gap: 12px;
  
  .theme-btn {
    width: 40px;
    height: 40px;
    border: 3px solid transparent;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
    
    &.active {
      border-color: var(--text-primary);
    }
  }
}

.permission-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  .permission-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: var(--bg-gray);
    border-radius: var(--radius-md);
    
    .permission-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .permission-icon {
        font-size: 24px;
      }
      
      .permission-text {
        display: flex;
        flex-direction: column;
        
        .permission-name {
          font-size: 14px;
          font-weight: 500;
        }
        
        .permission-desc {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
    
    .permission-btn {
      padding: 8px 16px;
      background: var(--primary-color);
      color: white;
      border: none;
      border-radius: var(--radius-full);
      font-size: 13px;
      cursor: pointer;
      
      &.granted {
        background: var(--success-color);
      }
    }
  }
}

.about-list {
  .about-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    
    &:last-child {
      border-bottom: none;
    }
    
    .arrow {
      font-size: 20px;
      color: var(--text-light);
    }
    
    .version {
      color: var(--text-secondary);
    }
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: var(--radius-lg);
  padding: 24px;
  
  h3 {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .modal-body {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 20px;
    
    p {
      font-size: 14px;
      line-height: 1.6;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }
  }
  
  .btn {
    width: 100%;
  }
}
</style>
