<template>
  <div class="app-container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- 底部导航 -->
    <nav class="bottom-nav" v-if="showNav">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <span class="nav-icon">🎤</span>
        <span class="nav-label">面试</span>
      </router-link>
      <router-link to="/resume" class="nav-item" :class="{ active: $route.path === '/resume' }">
        <span class="nav-icon">📄</span>
        <span class="nav-label">简历</span>
      </router-link>
      <router-link to="/history" class="nav-item" :class="{ active: $route.path === '/history' }">
        <span class="nav-icon">📊</span>
        <span class="nav-label">记录</span>
      </router-link>
      <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
        <span class="nav-icon">⚙️</span>
        <span class="nav-label">设置</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 在面试页面隐藏导航（全屏通话体验）
const showNav = computed(() => {
  return !route.path.startsWith('/interview/')
})
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 100;
  
  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: #999;
    font-size: 10px;
    transition: all 0.2s;
    
    .nav-icon {
      font-size: 22px;
      margin-bottom: 2px;
    }
    
    .nav-label {
      font-size: 11px;
    }
    
    &.active {
      color: #667eea;
    }
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
