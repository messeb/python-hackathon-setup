import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/chat', name: 'chat', component: () => import('@/views/ChatView.vue') },
    { path: '/ml', name: 'ml', component: () => import('@/views/MlView.vue') },
    { path: '/items', name: 'items', component: () => import('@/views/ItemsView.vue') },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
