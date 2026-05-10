<template>
  <div class="home-page page-container">
    <!-- 顶部区域 -->
    <header class="home-header">
      <div class="header-content">
        <h1 class="app-title">🎯 AI面试助手</h1>
        <p class="app-subtitle">模拟真实面试，提升求职竞争力</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-value">{{ totalInterviews }}</span>
          <span class="stat-label">已面试</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ totalPractice }}</span>
          <span class="stat-label">练习时长</span>
        </div>
      </div>
    </header>

    <!-- 快速开始 -->
    <section class="quick-start card">
      <h2 class="section-title">🚀 快速开始</h2>
      
      <!-- 岗位选择 -->
      <div class="form-group">
        <label class="form-label">选择面试岗位</label>
        <div class="position-grid">
          <button
            v-for="pos in positions"
            :key="pos.value"
            class="position-btn"
            :class="{ active: selectedPosition === pos.value }"
            @click="selectedPosition = pos.value"
          >
            <span class="pos-icon">{{ pos.icon }}</span>
            <span class="pos-name">{{ pos.name }}</span>
          </button>
        </div>
      </div>

      <!-- 职级选择 -->
      <div class="form-group">
        <label class="form-label">选择职级</label>
        <div class="level-tabs">
          <button
            v-for="level in levels"
            :key="level.value"
            class="level-tab"
            :class="{ active: selectedLevel === level.value }"
            @click="selectedLevel = level.value"
          >
            {{ level.name }}
          </button>
        </div>
      </div>

      <!-- 开始按钮 -->
      <button class="btn btn-primary btn-start" @click="startInterview">
        <span class="btn-icon">🎤</span>
        开始模拟面试
      </button>
    </section>

    <!-- 功能入口 -->
    <section class="feature-cards">
      <div class="feature-card card" @click="$router.push('/resume')">
        <div class="feature-icon">📄</div>
        <div class="feature-info">
          <h3>简历分析</h3>
          <p>上传简历，AI定制面试问题</p>
        </div>
        <span class="feature-arrow">›</span>
      </div>

      <div class="feature-card card" @click="$router.push('/history')">
        <div class="feature-icon">📊</div>
        <div class="feature-info">
          <h3>面试记录</h3>
          <p>查看历史面试和评估报告</p>
        </div>
        <span class="feature-arrow">›</span>
      </div>
    </section>

    <!-- 面试技巧 -->
    <section class="tips-section card">
      <h2 class="section-title">💡 面试小贴士</h2>
      <div class="tips-list">
        <div class="tip-item" v-for="tip in tips" :key="tip.id">
          <span class="tip-icon">{{ tip.icon }}</span>
          <span class="tip-text">{{ tip.text }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'

const router = useRouter()
const store = useInterviewStore()

// 统计数据
const totalInterviews = ref(12)
const totalPractice = ref('5.2h')

// 岗位选项
const positions = [
  { value: 'java', name: 'Java后端', icon: '☕' },
  { value: 'python', name: 'Python', icon: '🐍' },
  { value: 'frontend', name: '前端', icon: '📱' },
  { value: 'product', name: '产品经理', icon: '💼' },
  { value: 'operation', name: '运营', icon: '📈' },
  { value: 'data', name: '数据分析', icon: '📊' }
]

const levels = [
  { value: 'junior', name: '初级' },
  { value: 'middle', name: '中级' },
  { value: 'senior', name: '高级' }
]

// 选中的岗位和职级
const selectedPosition = ref('python')
const selectedLevel = ref('middle')

// 面试技巧
const tips = [
  { id: 1, icon: '🎯', text: '用STAR法则回答面试问题' },
  { id: 2, icon: '⏱️', text: '控制回答时间在2-3分钟' },
  { id: 3, icon: '💪', text: '遇到不会的问题，展示思考过程' },
  { id: 4, icon: '🎤', text: '语速适中，保持自信' }
]

// 开始面试
const startInterview = () => {
  const position = positions.find(p => p.value === selectedPosition.value)
  store.startInterview(position?.name, selectedLevel.value)
  router.push('/interview')
}
</script>

<style lang="scss" scoped>
.home-page {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  min-height: 100dvh;
}

.home-header {
  text-align: center;
  padding: 20px 0 30px;
  color: white;
  
  .app-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
  }
  
  .app-subtitle {
    font-size: 14px;
    opacity: 0.9;
  }
  
  .header-stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 24px;
    
    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .stat-value {
        font-size: 24px;
        font-weight: 700;
      }
      
      .stat-label {
        font-size: 12px;
        opacity: 0.8;
      }
    }
  }
}

.quick-start {
  margin-bottom: 16px;
  
  .section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
  }
}

.form-group {
  margin-bottom: 16px;
  
  .form-label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 10px;
  }
}

.position-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  
  .position-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 14px 8px;
    background: var(--bg-gray);
    border: 2px solid transparent;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
    
    .pos-icon {
      font-size: 24px;
      margin-bottom: 6px;
    }
    
    .pos-name {
      font-size: 12px;
      color: var(--text-primary);
    }
    
    &.active {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.1);
    }
    
    &:active {
      transform: scale(0.95);
    }
  }
}

.level-tabs {
  display: flex;
  gap: 10px;
  
  .level-tab {
    flex: 1;
    padding: 12px;
    background: var(--bg-gray);
    border: 2px solid transparent;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    
    &.active {
      border-color: var(--primary-color);
      background: rgba(102, 126, 234, 0.1);
      color: var(--primary-color);
    }
    
    &:active {
      transform: scale(0.98);
    }
  }
}

.btn-start {
  width: 100%;
  padding: 16px;
  font-size: 18px;
  margin-top: 20px;
  border-radius: var(--radius-lg);
  
  .btn-icon {
    margin-right: 8px;
    font-size: 20px;
  }
}

.feature-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  
  .feature-card {
    display: flex;
    align-items: center;
    padding: 16px;
    cursor: pointer;
    transition: transform 0.2s;
    
    &:active {
      transform: scale(0.98);
    }
    
    .feature-icon {
      font-size: 32px;
      margin-right: 14px;
    }
    
    .feature-info {
      flex: 1;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      p {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
    
    .feature-arrow {
      font-size: 24px;
      color: var(--text-light);
    }
  }
}

.tips-section {
  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 14px;
  }
  
  .tips-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    
    .tip-item {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      color: var(--text-secondary);
      
      .tip-icon {
        font-size: 18px;
      }
    }
  }
}
</style>
