import { createRouter, createWebHistory } from 'vue-router'

import BaselinePage from './views/BaselinePage.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: BaselinePage },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
