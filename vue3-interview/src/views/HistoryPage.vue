<template>
  <div class="history-page page-container">
    <header class="page-header">
      <h1 class="page-title">📊 面试记录</h1>
    </header>

    <!-- 筛选 -->
    <div class="filter-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- 记录列表 -->
    <div class="history-list" v-if="filteredHistory.length > 0">
      <div
        v-for="item in filteredHistory"
        :key="item.id"
        class="history-card card"
        @click="viewReport(item)"
      >
        <div class="card-header">
          <div class="position-info">
            <span class="position-name">{{ item.position }}</span>
            <span class="position-level">{{ getLevelName(item.level) }}</span>
          </div>
          <span class="score-badge" :class="getScoreClass(item.score)">
            {{ item.score }}分
          </span>
        </div>
        
        <div class="card-body">
          <div class="info-row">
            <span class="info-icon">📅</span>
            <span>{{ formatDate(item.date) }}</span>
          </div>
          <div class="info-row">
            <span class="info-icon">⏱️</span>
            <span>{{ item.duration }}</span>
          </div>
          <div class="info-row">
            <span class="info-icon">💬</span>
            <span>{{ item.messageCount }}条对话</span>
          </div>
        </div>
        
        <div class="card-footer">
          <div class="tags">
            <span v-for="tag in item.tags" :key="tag" class="tag" :class="getTagClass(tag)">
              {{ tag }}
            </span>
          </div>
          <span class="view-more">查看报告 ›</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📋</div>
      <p class="empty-text">暂无面试记录</p>
      <button class="btn btn-primary" @click="$router.push('/')">
        开始第一次面试
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 标签页
const tabs = [
  { name: '全部', value: 'all' },
  { name: '技术', value: 'tech' },
  { name: '产品', value: 'product' },
  { name: '运营', value: 'operation' }
]

const activeTab = ref('all')

// 模拟历史数据
const historyData = ref([
  {
    id: '1',
    position: 'Python后端开发',
    level: 'middle',
    score: 78,
    date: '2025-01-15T14:30:00',
    duration: '25分钟',
    messageCount: 18,
    tags: ['Python', 'Django', '项目经验']
  },
  {
    id: '2',
    position: '前端开发',
    level: 'junior',
    score: 65,
    date: '2025-01-14T10:00:00',
    duration: '20分钟',
    messageCount: 12,
    tags: ['Vue', 'React', '基础']
  },
  {
    id: '3',
    position: '产品经理',
    level: 'senior',
    score: 82,
    date: '2025-01-12T16:00:00',
    duration: '35分钟',
    messageCount: 24,
    tags: ['需求分析', '项目管理', '用户体验']
  }
])

// 筛选
const filteredHistory = computed(() => {
  if (activeTab.value === 'all') return historyData.value
  // 简单过滤演示
  return historyData.value
})

// 获取职级名称
const getLevelName = (level) => {
  const map = { junior: '初级', middle: '中级', senior: '高级' }
  return map[level] || level
}

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取分数样式
const getScoreClass = (score) => {
  if (score >= 80) return 'good'
  if (score >= 60) return 'medium'
  return 'poor'
}

// 获取标签样式
const getTagClass = (tag) => {
  if (tag.includes('项目') || tag.includes('经验')) return 'success'
  if (tag.includes('基础')) return 'warning'
  return ''
}

// 查看报告
const viewReport = (item) => {
  router.push(`/report/${item.id}`)
}
</script>

<style lang="scss" scoped>
.history-page {
  background: var(--bg-gray);
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
  
  button {
    padding: 8px 16px;
    background: var(--bg-white);
    border: none;
    border-radius: var(--radius-full);
    font-size: 14px;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.2s;
    
    &.active {
      background: var(--primary-color);
      color: white;
    }
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  cursor: pointer;
  transition: transform 0.2s;
  
  &:active {
    transform: scale(0.98);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    
    .position-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .position-name {
        font-size: 16px;
        font-weight: 600;
      }
      
      .position-level {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
    
    .score-badge {
      padding: 4px 10px;
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
  }
  
  .card-body {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    
    .info-row {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: var(--text-secondary);
      
      .info-icon {
        font-size: 14px;
      }
    }
  }
  
  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
    
    .tags {
      display: flex;
      gap: 6px;
    }
    
    .view-more {
      font-size: 13px;
      color: var(--primary-color);
    }
  }
}

.empty-state {
  .empty-icon {
    font-size: 64px;
    opacity: 0.5;
  }
  
  .empty-text {
    margin: 16px 0 20px;
    color: var(--text-secondary);
  }
}
</style>
