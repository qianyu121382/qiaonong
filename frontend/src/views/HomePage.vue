<script setup>
import { computed, onMounted, ref } from 'vue'

import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'
import { loadSite, siteState } from '../stores/site'


const slides = ref([])
const products = ref([])
const slideIndex = ref(0)
const loading = ref(true)
const currentSlide = computed(() => slides.value[slideIndex.value])

onMounted(async () => {
  await loadSite()
  try {
    ;[slides.value, products.value] = await Promise.all([
      api('/api/content/slides/'),
      api('/api/catalog/products/?featured=true'),
    ])
  } catch {
    slides.value = []
    products.value = []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main>
    <section class="hero" :style="currentSlide?.image ? { backgroundImage: `linear-gradient(90deg, rgba(15,25,20,.44), rgba(15,25,20,.05)), url(${currentSlide.image})` } : {}">
      <div class="hero-content">
        <p class="eyebrow">QIAONONG · EST.</p>
        <h1>{{ currentSlide?.title || siteState.settings.home_title || '专注品质，认真表达' }}</h1>
        <p>{{ currentSlide?.subtitle || siteState.settings.home_subtitle || '巧侬企业官网正在整理经确认的品牌与产品资料。' }}</p>
        <router-link v-if="currentSlide?.link_url" class="outline-link" :to="currentSlide.link_url">了解更多</router-link>
        <router-link v-else class="outline-link" to="/products">浏览产品</router-link>
      </div>
      <div v-if="slides.length > 1" class="slide-dots"><button v-for="(_, index) in slides" :key="index" :class="{ active: index === slideIndex }" :aria-label="`第 ${index + 1} 张`" @click="slideIndex = index"></button></div>
    </section>

    <section class="content-section category-section">
      <header class="section-heading"><p class="eyebrow">PRODUCT SERIES</p><h2>产品系列</h2><router-link to="/products">查看全部</router-link></header>
      <div v-if="siteState.categories.length" class="category-grid">
        <router-link v-for="category in siteState.categories" :key="category.id" class="category-card" :to="`/products/${category.slug}`">
          <img v-if="category.banner" :src="category.banner" :alt="category.name" loading="lazy" /><div class="category-placeholder" v-else></div>
          <span><small>{{ category.children?.length }} 个系列</small><strong>{{ category.name }}</strong></span>
        </router-link>
      </div>
      <p v-else-if="!loading" class="empty-state">产品分类资料正在整理中。</p>
    </section>

    <section v-if="products.length" class="content-section product-section">
      <header class="section-heading"><p class="eyebrow">FEATURED</p><h2>推荐产品</h2></header>
      <div class="product-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div>
    </section>

    <section class="brand-intro">
      <div class="brand-copy"><p class="eyebrow">ABOUT QIAONONG</p><h2>{{ siteState.settings.home_intro_title || '关于巧侬' }}</h2><p>{{ siteState.settings.home_intro_body || '品牌资料将在核验后由管理员后台发布。' }}</p><router-link class="text-link" to="/brand">阅读品牌介绍 →</router-link></div>
      <div class="brand-image"><img v-if="siteState.settings.home_intro_image" :src="siteState.settings.home_intro_image" alt="巧侬品牌介绍" /><span v-else>QIAONONG</span></div>
    </section>
  </main>
</template>
