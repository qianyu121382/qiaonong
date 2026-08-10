import { createRouter, createWebHistory } from 'vue-router'

import PublicLayout from './components/PublicLayout.vue'
import ContactPage from './views/ContactPage.vue'
import ContentPage from './views/ContentPage.vue'
import HomePage from './views/HomePage.vue'
import NotFoundPage from './views/NotFoundPage.vue'
import ProductDetailPage from './views/ProductDetailPage.vue'
import ProductListPage from './views/ProductListPage.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        { path: '', name: 'home', component: HomePage, meta: { title: '首页' } },
        { path: 'brand', name: 'brand', component: ContentPage, props: { slug: 'brand' }, meta: { title: '品牌介绍' } },
        { path: 'products/:category?', name: 'products', component: ProductListPage, meta: { title: '产品中心' } },
        { path: 'product/:slug', name: 'product-detail', component: ProductDetailPage },
        { path: 'search', name: 'search', component: ProductListPage, props: { searchMode: true }, meta: { title: '站内搜索' } },
        { path: 'contact', name: 'contact', component: ContactPage, meta: { title: '联系我们' } },
        { path: 'policy/:slug', name: 'policy', component: ContentPage },
        { path: ':pathMatch(.*)*', name: 'not-found', component: NotFoundPage, meta: { title: '页面未找到' } },
      ],
    },
  ],
})

router.afterEach((to) => {
  const title = to.meta.title
  document.title = title ? `${title} - 巧侬` : '巧侬企业官网'
  window.scrollTo({ top: 0 })
})

export default router
