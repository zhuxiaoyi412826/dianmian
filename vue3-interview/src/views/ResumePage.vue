<template>
  <div class="resume-page page-container">
    <header class="page-header">
      <h1 class="page-title">📄 简历分析</h1>
    </header>

    <!-- 上传区域 -->
    <section class="upload-section card">
      <div
        class="upload-area"
        :class="{ dragging: isDragging, 'has-file': resumeFile }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          @change="handleFileSelect"
          style="display: none"
        >
        
        <div v-if="!resumeFile" class="upload-placeholder">
          <div class="upload-icon">📎</div>
          <p class="upload-text">点击或拖拽上传简历</p>
          <p class="upload-hint">支持 PDF、Word、TXT 格式</p>
        </div>
        
        <div v-else class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-details">
            <p class="file-name">{{ resumeFile.name }}</p>
            <p class="file-size">{{ formatFileSize(resumeFile.size) }}</p>
          </div>
          <button class="remove-btn" @click.stop="removeFile">✕</button>
        </div>
      </div>
    </section>

    <!-- 手动输入 -->
    <section class="manual-section card">
      <h3 class="section-title">或手动输入简历信息</h3>
      <textarea
        v-model="resumeText"
        class="resume-input"
        placeholder="请粘贴您的简历内容，例如：

姓名：张三
工作年限：3年
技术栈：Python, Django, Flask, MySQL, Redis
项目经验：
1. 用户行为分析系统 - 使用Flask开发
2. 电商后台管理系统 - 使用Django开发"
        rows="8"
      ></textarea>
      <button class="btn btn-primary" @click="analyzeResume" :disabled="!resumeText && !resumeFile">
        🔍 开始分析
      </button>
    </section>

    <!-- 分析结果 -->
    <section v-if="analysisResult" class="result-section card">
      <h3 class="section-title">📊 简历分析结果</h3>
      
      <!-- 基本信息 -->
      <div class="info-card">
        <h4>基本信息</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">姓名</span>
            <span class="info-value">{{ analysisResult.name || '未识别' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">工作年限</span>
            <span class="info-value">{{ analysisResult.experience || '未识别' }}</span>
          </div>
        </div>
      </div>

      <!-- 技能分析 -->
      <div class="info-card">
        <h4>技术栈</h4>
        <div class="skill-tags">
          <span
            v-for="skill in analysisResult.skills"
            :key="skill"
            class="skill-tag"
          >
            {{ skill }}
          </span>
        </div>
      </div>

      <!-- 项目经历 -->
      <div class="info-card">
        <h4>项目经历</h4>
        <div
          v-for="(project, index) in analysisResult.projects"
          :key="index"
          class="project-item"
        >
          <p class="project-name">{{ project.name }}</p>
          <p class="project-desc">{{ project.description }}</p>
        </div>
      </div>

      <!-- 面试建议 -->
      <div class="info-card highlight">
        <h4>💡 面试重点建议</h4>
        <ul class="suggestion-list">
          <li v-for="s in analysisResult.suggestions" :key="s">{{ s }}</li>
        </ul>
      </div>

      <!-- 开始面试 -->
      <button class="btn btn-primary btn-start" @click="startInterviewWithResume">
        🎯 根据简历开始面试
      </button>
    </section>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在分析简历...</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import { uploadResume, analyzeResumeText } from '../api'

const router = useRouter()
const store = useInterviewStore()

// 状态
const isDragging = ref(false)
const resumeFile = ref(null)
const resumeText = ref('')
const analysisResult = ref(null)
const isLoading = ref(false)
const fileInput = ref(null)

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    resumeFile.value = file
    analyzeFile(file)
  }
}

// 处理拖拽
const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    resumeFile.value = file
    analyzeFile(file)
  }
}

// 移除文件
const removeFile = () => {
  resumeFile.value = null
  analysisResult.value = null
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 分析简历
const analyzeResume = async () => {
  if (!resumeText.value) return
  
  isLoading.value = true
  try {
    const result = await analyzeResumeText(resumeText.value)
    analysisResult.value = result
  } catch (err) {
    console.error('分析失败:', err)
    alert('简历分析失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 分析文件
const analyzeFile = async (file) => {
  isLoading.value = true
  try {
    const result = await uploadResume(file)
    analysisResult.value = result
    resumeText.value = result.rawText || ''
  } catch (err) {
    console.error('上传失败:', err)
    alert('简历上传失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 根据简历开始面试
const startInterviewWithResume = () => {
  store.startInterview('Python后端', 'middle', analysisResult.value)
  store.currentInterview.resume = analysisResult.value
  router.push('/interview')
}
</script>

<style lang="scss" scoped>
.resume-page {
  background: var(--bg-gray);
}

.upload-section {
  margin-bottom: 16px;
  
  .upload-area {
    border: 2px dashed #e2e8f0;
    border-radius: var(--radius-lg);
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    
    &.dragging {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.05);
    }
    
    &.has-file {
      border-style: solid;
      border-color: var(--primary-color);
    }
    
    .upload-placeholder {
      .upload-icon {
        font-size: 48px;
        margin-bottom: 12px;
      }
      
      .upload-text {
        font-size: 16px;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .upload-hint {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
    
    .file-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .file-icon {
        font-size: 36px;
      }
      
      .file-details {
        flex: 1;
        text-align: left;
        
        .file-name {
          font-size: 14px;
          font-weight: 500;
        }
        
        .file-size {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
      
      .remove-btn {
        width: 28px;
        height: 28px;
        background: #fee;
        border: none;
        border-radius: 50%;
        color: #f56565;
        cursor: pointer;
      }
    }
  }
}

.manual-section {
  margin-bottom: 16px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
  }
  
  .resume-input {
    width: 100%;
    padding: 14px;
    border: 2px solid #e2e8f0;
    border-radius: var(--radius-md);
    font-size: 14px;
    line-height: 1.6;
    resize: vertical;
    margin-bottom: 12px;
    
    &:focus {
      outline: none;
      border-color: var(--primary-color);
    }
  }
  
  .btn {
    width: 100%;
  }
}

.result-section {
  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
  }
  
  .info-card {
    background: var(--bg-gray);
    border-radius: var(--radius-md);
    padding: 14px;
    margin-bottom: 12px;
    
    h4 {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 10px;
      color: var(--text-secondary);
    }
    
    &.highlight {
      background: rgba(102, 126, 234, 0.1);
      
      h4 {
        color: var(--primary-color);
      }
    }
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    
    .info-item {
      .info-label {
        font-size: 12px;
        color: var(--text-secondary);
      }
      
      .info-value {
        font-size: 15px;
        font-weight: 500;
      }
    }
  }
  
  .skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .skill-tag {
      padding: 6px 12px;
      background: white;
      border-radius: var(--radius-full);
      font-size: 13px;
      color: var(--primary-color);
    }
  }
  
  .project-item {
    padding: 10px 0;
    border-bottom: 1px solid #e2e8f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .project-name {
      font-weight: 500;
      margin-bottom: 4px;
    }
    
    .project-desc {
      font-size: 13px;
      color: var(--text-secondary);
    }
  }
  
  .suggestion-list {
    padding-left: 20px;
    
    li {
      font-size: 14px;
      line-height: 1.8;
      color: var(--text-primary);
    }
  }
  
  .btn-start {
    width: 100%;
    margin-top: 16px;
  }
}

.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 1000;
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 12px;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
