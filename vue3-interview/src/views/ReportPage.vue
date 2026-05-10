<template>
  <div class="report-page page-container">
    <header class="page-header">
      <button class="back-btn" @click="$router.back()">‹ 返回</button>
      <h1 class="page-title">面试评估报告</h1>
    </header>

    <!-- 概览 -->
    <section class="overview-section">
      <div class="score-circle">
        <svg viewBox="0 0 100 100">
          <circle
            cx="50" cy="50" r="45"
            stroke="#e2e8f0"
            stroke-width="8"
            fill="none"
          />
          <circle
            cx="50" cy="50" r="45"
            :stroke="getScoreColor(reportData.score)"
            stroke-width="8"
            fill="none"
            :stroke-dasharray="`${reportData.score * 2.83} 283`"
            stroke-linecap="round"
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div class="score-text">
          <span class="score-value">{{ reportData.score }}</span>
          <span class="score-label">综合评分</span>
        </div>
      </div>
      
      <div class="overall-status">
        <span class="status-badge" :class="getStatusClass(reportData.score)">
          {{ getStatusText(reportData.score) }}
        </span>
        <p class="status-hint">{{ reportData.hint }}</p>
      </div>
    </section>

    <!-- 维度评分 -->
    <section class="dimensions-section card">
      <h3 class="section-title">📊 各维度评分</h3>
      
      <div class="dimension-list">
        <div
          v-for="dim in reportData.dimensions"
          :key="dim.name"
          class="dimension-item"
        >
          <div class="dim-header">
            <span class="dim-name">{{ dim.name }}</span>
            <span class="dim-score" :style="{ color: getScoreColor(dim.score) }">
              {{ dim.score }}/{{ dim.max }}
            </span>
          </div>
          <div class="dim-bar">
            <div
              class="dim-progress"
              :style="{
                width: `${(dim.score / dim.max) * 100}%`,
                background: getScoreColor(dim.score)
              }"
            ></div>
          </div>
          <p class="dim-comment">{{ dim.comment }}</p>
        </div>
      </div>
    </section>

    <!-- 技术能力 -->
    <section class="skills-section card">
      <h3 class="section-title">💪 技术能力分析</h3>
      
      <div class="skills-grid">
        <div class="skill-card strength">
          <h4>✅ 优势领域</h4>
          <ul>
            <li v-for="skill in reportData.strengths" :key="skill">{{ skill }}</li>
          </ul>
        </div>
        
        <div class="skill-card weakness">
          <h4>⚠️ 待提升领域</h4>
          <ul>
            <li v-for="skill in reportData.weaknesses" :key="skill">{{ skill }}</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 改进建议 -->
    <section class="suggestions-section card">
      <h3 class="section-title">💡 改进建议</h3>
      
      <div class="suggestion-list">
        <div
          v-for="(s, index) in reportData.suggestions"
          :key="index"
          class="suggestion-item"
        >
          <span class="sug-number">{{ index + 1 }}</span>
          <div class="sug-content">
            <p class="sug-title">{{ s.title }}</p>
            <p class="sug-desc">{{ s.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 面试问答回顾 -->
    <section class="qa-section card">
      <h3 class="section-title">💬 面试问答回顾</h3>
      
      <div class="qa-list">
        <div
          v-for="(qa, index) in reportData.qaHistory"
          :key="index"
          class="qa-item"
        >
          <div class="qa-q">
            <span class="qa-label">Q{{ index + 1 }}</span>
            <p class="qa-text">{{ qa.question }}</p>
          </div>
          <div class="qa-a">
            <span class="qa-label">你的回答</span>
            <p class="qa-text">{{ qa.answer }}</p>
            <div class="qa-feedback">
              <span class="feedback-score">得分: {{ qa.score }}</span>
              <span class="feedback-comment">{{ qa.feedback }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 操作按钮 -->
    <section class="actions-section">
      <button class="btn btn-outline" @click="replayInterview">
        🔄 重新面试
      </button>
      <button class="btn btn-primary" @click="shareReport">
        📤 分享报告
      </button>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 模拟报告数据
const reportData = ref({
  score: 78,
  hint: '技术基础扎实，项目经验有亮点，建议加强系统设计能力',
  dimensions: [
    { name: '技术基础', score: 8, max: 10, comment: 'Python核心概念掌握扎实' },
    { name: '技术深度', score: 6, max: 10, comment: '对底层原理理解有待加强' },
    { name: '项目经验', score: 8, max: 10, comment: '能清晰描述项目架构和解决的问题' },
    { name: '逻辑思维', score: 7, max: 10, comment: '回答问题有一定条理性' },
    { name: '沟通表达', score: 8, max: 10, comment: '表达清晰流畅' },
    { name: '抗压能力', score: 7, max: 10, comment: '面对追问时略显紧张' }
  ],
  strengths: [
    'Python基础扎实，list/tuple、GIL等概念清晰',
    '有实际项目经验，能描述系统架构',
    '具备线上问题排查能力',
    '表达清晰，沟通顺畅'
  ],
  weaknesses: [
    '对常用库底层原理理解不足',
    '技术选型时缺乏方案对比思维',
    '复杂问题缺乏结构化思考'
  ],
  suggestions: [
    {
      title: '深入学习技术原理',
      description: '建议阅读pydantic、SQLAlchemy等库的源码，理解其核心实现机制'
    },
    {
      title: '建立对比思维',
      description: '每次技术选型时，列出2-3种方案对比，锻炼方案评估能力'
    },
    {
      title: '结构化复盘问题',
      description: '按"现象→根因→方案→决策"的链路复盘每个线上问题'
    }
  ],
  qaHistory: [
    {
      question: 'Python中list和tuple的区别？GIL是什么？',
      answer: 'list是可变的，tuple是不可变的...',
      score: 8,
      feedback: '回答准确，概念清晰'
    },
    {
      question: '如何绕过GIL限制？',
      answer: '对于IO密集型可以用多线程，对于CPU密集型可以用多进程...',
      score: 7,
      feedback: '基本正确，可补充asyncio方案'
    }
  ]
})

// 获取分数颜色
const getScoreColor = (score) => {
  if (score >= 8) return '#48bb78'
  if (score >= 6) return '#ed8936'
  return '#f56565'
}

// 获取状态
const getStatusText = (score) => {
  if (score >= 80) return '推荐录用'
  if (score >= 60) return '可以考虑'
  return '建议继续提升'
}

const getStatusClass = (score) => {
  if (score >= 80) return 'good'
  if (score >= 60) return 'medium'
  return 'poor'
}

// 重新面试
const replayInterview = () => {
  router.push('/')
}

// 分享报告
const shareReport = () => {
  if (navigator.share) {
    navigator.share({
      title: 'AI面试评估报告',
      text: `我的面试评分：${reportData.value.score}分`,
      url: window.location.href
    })
  } else {
    alert('复制链接分享')
  }
}
</script>

<style lang="scss" scoped>
.report-page {
  background: var(--bg-gray);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  
  .back-btn {
    background: none;
    border: none;
    font-size: 28px;
    color: var(--text-primary);
    cursor: pointer;
  }
  
  .page-title {
    font-size: 20px;
    font-weight: 700;
  }
}

.overview-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: white;
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
  
  .score-circle {
    position: relative;
    width: 120px;
    height: 120px;
    flex-shrink: 0;
    
    svg {
      width: 100%;
      height: 100%;
    }
    
    .score-text {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      
      .score-value {
        font-size: 32px;
        font-weight: 700;
        color: var(--primary-color);
      }
      
      .score-label {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
  
  .overall-status {
    flex: 1;
    
    .status-badge {
      display: inline-block;
      padding: 6px 16px;
      border-radius: var(--radius-full);
      font-size: 14px;
      font-weight: 600;
      
      &.good {
        background: rgba(72, 187, 120, 0.1);
        color: var(--success-color);
      }
      
      &.medium {
        background: rgba(237, 137, 54, 0.1);
        color: var(--warning-color);
      }
      
      &.poor {
        background: rgba(245, 101, 101, 0.1);
        color: var(--danger-color);
      }
    }
    
    .status-hint {
      margin-top: 8px;
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.5;
    }
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.dimensions-section {
  margin-bottom: 16px;
  
  .dimension-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .dimension-item {
    .dim-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
      
      .dim-name {
        font-size: 14px;
        font-weight: 500;
      }
      
      .dim-score {
        font-size: 14px;
        font-weight: 600;
      }
    }
    
    .dim-bar {
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 4px;
      
      .dim-progress {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
      }
    }
    
    .dim-comment {
      font-size: 12px;
      color: var(--text-secondary);
    }
  }
}

.skills-section {
  margin-bottom: 16px;
  
  .skills-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    
    .skill-card {
      padding: 14px;
      border-radius: var(--radius-md);
      
      h4 {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
      }
      
      ul {
        padding-left: 16px;
        
        li {
          font-size: 12px;
          line-height: 1.8;
          color: var(--text-secondary);
        }
      }
      
      &.strength {
        background: rgba(72, 187, 120, 0.1);
        
        h4 {
          color: var(--success-color);
        }
      }
      
      &.weakness {
        background: rgba(245, 101, 101, 0.1);
        
        h4 {
          color: var(--danger-color);
        }
      }
    }
  }
}

.suggestions-section {
  margin-bottom: 16px;
  
  .suggestion-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .suggestion-item {
    display: flex;
    gap: 12px;
    
    .sug-number {
      width: 24px;
      height: 24px;
      background: var(--primary-color);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      flex-shrink: 0;
    }
    
    .sug-content {
      flex: 1;
      
      .sug-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      .sug-desc {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
      }
    }
  }
}

.qa-section {
  margin-bottom: 16px;
  
  .qa-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .qa-item {
    padding: 14px;
    background: var(--bg-gray);
    border-radius: var(--radius-md);
    
    .qa-q, .qa-a {
      margin-bottom: 10px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .qa-label {
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      color: var(--primary-color);
      margin-bottom: 4px;
    }
    
    .qa-text {
      font-size: 14px;
      line-height: 1.5;
    }
    
    .qa-feedback {
      display: flex;
      gap: 12px;
      margin-top: 8px;
      font-size: 12px;
      
      .feedback-score {
        color: var(--warning-color);
        font-weight: 600;
      }
      
      .feedback-comment {
        color: var(--text-secondary);
      }
    }
  }
}

.actions-section {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  
  .btn {
    flex: 1;
    padding: 14px;
  }
}
</style>
