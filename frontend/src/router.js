import { createRouter, createWebHistory } from 'vue-router'

import PublicLayout from './components/PublicLayout.vue'
import ContactPage from './views/ContactPage.vue'
import ContentPage from './views/ContentPage.vue'
import HomePage from './views/HomePage.vue'
import NotFoundPage from './views/NotFoundPage.vue'
import ProductDetailPage from './views/ProductDetailPage.vue'
import ProductListPage from './views/ProductListPage.vue'
import { setPageSeo } from './seo'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PublicLayout,
      children: [
        { path: '', name: 'home', component: HomePage, meta: { title: '巧侬花田官网 - 护肤、院护与医美产品' } },
        { path: 'brand', name: 'brand', component: ContentPage, props: { slug: 'brand' }, meta: { title: '品牌介绍 - 巧侬花田' } },
        { path: 'products/:category?', name: 'products', component: ProductListPage, meta: { title: '产品中心 - 巧侬花田' } },
        { path: 'product/:slug', name: 'product-detail', component: ProductDetailPage },
        { path: 'search', name: 'search', component: ProductListPage, props: { searchMode: true }, meta: { title: '站内搜索 - 巧侬花田', noindex: true } },
        { path: 'contact', name: 'contact', component: ContactPage, meta: { title: '联系我们 - 巧侬花田' } },
        { path: 'policy/:slug', name: 'policy', component: ContentPage },
        { path: ':pathMatch(.*)*', name: 'not-found', component: NotFoundPage, meta: { title: '页面未找到 - 巧侬花田', noindex: true } },
      ],
    },
  ],
})

router.afterEach((to) => {
  setPageSeo({
    title: to.meta.title || '巧侬花田官网',
    path: to.path,
    noindex: Boolean(to.meta.noindex),
  })
  window.scrollTo({ top: 0 })
})

export default router
