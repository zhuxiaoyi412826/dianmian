import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue')
  },
  {
    path: '/interview/:id?',
    name: 'Interview',
    component: () => import('../views/InterviewPage.vue'),
    meta: { hideNav: true }
  },
  {
    path: '/resume',
    name: 'Resume',
    component: () => import('../views/ResumePage.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryPage.vue')
  },
  {
    path: '/report/:id',
    name: 'Report',
    component: () => import('../views/ReportPage.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
