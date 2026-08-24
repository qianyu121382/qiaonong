import { createRouter, createWebHistory } from 'vue-router'

import { authState, restoreSession } from './stores/auth'
import AdminLayout from './components/AdminLayout.vue'
import CategoryPage from './views/CategoryPage.vue'
import CatalogPage from './views/CatalogPage.vue'
import ContentPage from './views/ContentPage.vue'
import DashboardPage from './views/DashboardPage.vue'
import LoginPage from './views/LoginPage.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginPage, meta: { public: true } },
    {
      path: '/',
      component: AdminLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardPage },
        { path: 'categories', name: 'categories', component: CategoryPage },
        { path: 'products', name: 'products', component: CatalogPage },
        { path: 'carousel', name: 'carousel', component: ContentPage, props: { mode: 'carousel' } },
        { path: 'company', name: 'company', component: ContentPage, props: { mode: 'company' } },
        { path: 'catalog', redirect: '/products' },
        { path: 'content', redirect: '/company' },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (!authState.ready) await restoreSession()
  if (!to.meta.public && !authState.authenticated) return { name: 'login' }
  if (to.name === 'login' && authState.authenticated) return { name: 'dashboard' }
  return true
})

export default router
