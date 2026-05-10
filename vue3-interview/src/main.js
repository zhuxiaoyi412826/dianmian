import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './styles/main.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 隐藏加载动画
window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('loadingScreen')?.classList.add('hidden')
  }, 500)
})

app.mount('#app')
