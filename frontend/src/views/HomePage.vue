<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'
import { loadSite, siteState } from '../stores/site'


const slides = ref([])
const featuredProducts = ref([])
const seriesProducts = ref([])
const slideIndex = ref(0)
const seriesIndex = ref(0)
const loading = ref(true)
const seriesLoading = ref(false)
const autoplayPaused = ref(false)
const failedSlideIds = ref([])
const seriesProductCache = new Map()
let slideTimer
const fallbackSlide = {
  id: 'local-fallback',
  image: '/hero-fallback.svg',
  mobile_image: '/hero-fallback.svg',
  title: '',
  subtitle: '',
}
const availableSlides = computed(() => slides.value.filter((slide) => !failedSlideIds.value.includes(slide.id)))
const displaySlides = computed(() => availableSlides.value.length ? availableSlides.value : [fallbackSlide])
const currentSlide = computed(() => displaySlides.value[slideIndex.value % displaySlides.value.length])
const currentSeries = computed(() => siteState.categories[seriesIndex.value])
const heroTitle = computed(() => currentSlide.value
  ? currentSlide.value.title
  : siteState.settings.home_title || '专注品质，认真表达')
const heroSubtitle = computed(() => currentSlide.value
  ? currentSlide.value.subtitle
  : siteState.settings.home_subtitle || '巧侬企业官网正在整理经确认的品牌与产品资料。')
const showHeroCopy = computed(() => !currentSlide.value
  || Boolean(currentSlide.value.title || currentSlide.value.subtitle))

function nextSlide() {
  if (!autoplayPaused.value && displaySlides.value.length > 1) {
    slideIndex.value = (slideIndex.value + 1) % displaySlides.value.length
  }
}

function selectSlide(index) {
  slideIndex.value = index
  window.clearInterval(slideTimer)
  if (displaySlides.value.length > 1) slideTimer = window.setInterval(nextSlide, 5000)
}

function handleSlideError(slide) {
  if (slide.id === fallbackSlide.id || failedSlideIds.value.includes(slide.id)) return
  failedSlideIds.value = [...failedSlideIds.value, slide.id]
  slideIndex.value = 0
  window.clearInterval(slideTimer)
  if (displaySlides.value.length > 1) slideTimer = window.setInterval(nextSlide, 5000)
}

async function selectSeries(index) {
  seriesIndex.value = index
  const category = siteState.categories[index]
  if (!category) return
  if (seriesProductCache.has(category.slug)) {
    seriesLoading.value = false
    seriesProducts.value = seriesProductCache.get(category.slug)
    return
  }
  seriesLoading.value = true
  const requestedSlug = category.slug
  try {
    const items = await api(`/api/catalog/products/?category=${encodeURIComponent(category.slug)}`)
    const representatives = items.slice(0, 3)
    seriesProductCache.set(category.slug, representatives)
    if (currentSeries.value?.slug === requestedSlug) seriesProducts.value = representatives
  } catch {
    if (currentSeries.value?.slug === requestedSlug) seriesProducts.value = []
  } finally {
    if (currentSeries.value?.slug === requestedSlug) seriesLoading.value = false
  }
}

onMounted(async () => {
  await loadSite()
  try {
    ;[slides.value, featuredProducts.value] = await Promise.all([
      api('/api/content/slides/'),
      api('/api/catalog/products/?featured=true'),
    ])
  } catch {
    slides.value = []
    featuredProducts.value = []
  } finally {
    if (siteState.categories.length) await selectSeries(0)
    loading.value = false
    if (displaySlides.value.length > 1) slideTimer = window.setInterval(nextSlide, 5000)
  }
})

onBeforeUnmount(() => window.clearInterval(slideTimer))
</script>

<template>
  <main>
    <section class="hero" :class="{ 'hero-loading': loading, 'image-only': currentSlide?.image && !showHeroCopy, 'has-image': currentSlide?.image, 'with-copy': currentSlide?.image && showHeroCopy, clickable: currentSlide?.link_url }" @mouseenter="autoplayPaused = true" @mouseleave="autoplayPaused = false" @focusin="autoplayPaused = true" @focusout="autoplayPaused = false">
      <picture v-if="currentSlide?.image" class="hero-media">
        <source media="(max-width: 640px)" :srcset="currentSlide.mobile_image || currentSlide.image" />
        <img :src="currentSlide.image" :alt="currentSlide.title || '巧侬花田首页轮播图'" @error="handleSlideError(currentSlide)" />
      </picture>
      <router-link v-if="currentSlide?.link_url" class="hero-slide-link" :to="currentSlide.link_url" :aria-label="`查看第 ${slideIndex + 1} 张轮播图内容`"></router-link>
      <div v-if="showHeroCopy" class="hero-content">
        <p class="eyebrow">QIAONONG · EST.</p>
        <h1 v-if="heroTitle">{{ heroTitle }}</h1>
        <p v-if="heroSubtitle">{{ heroSubtitle }}</p>
        <router-link v-if="currentSlide?.link_url" class="outline-link" :to="currentSlide.link_url">了解更多</router-link>
        <router-link v-else class="outline-link" to="/products">浏览产品</router-link>
      </div>
      <div v-if="displaySlides.length > 1" class="slide-dots"><button v-for="(slide, index) in displaySlides" :key="slide.id" :class="{ active: index === slideIndex }" :aria-current="index === slideIndex ? 'true' : undefined" :aria-label="`切换到第 ${index + 1} 张`" @click.stop="selectSlide(index)"></button></div>
    </section>

    <section class="content-section series-section">
      <header class="section-heading"><p class="eyebrow">PRODUCT SERIES</p><h2>产品系列</h2><router-link to="/products">查看全部</router-link></header>
      <div v-if="siteState.categories.length" class="series-tabs" role="tablist" aria-label="产品系列">
        <button v-for="(category, index) in siteState.categories" :key="category.id" type="button" role="tab" :class="{ active: index === seriesIndex }" :aria-selected="index === seriesIndex" @click="selectSeries(index)"><small>0{{ index + 1 }}</small>{{ category.name }}</button>
      </div>
      <div v-if="currentSeries" class="series-showcase">
        <router-link class="series-banner-stage" :to="`/products/${currentSeries.slug}`" :aria-label="`查看 ${currentSeries.name} 系列全部产品`">
          <div class="series-banner-viewport">
            <img v-if="currentSeries.banner" class="series-banner-img" :src="currentSeries.banner" :alt="`${currentSeries.name} 系列横幅`" />
            <div v-else class="series-placeholder"><span>QIAONONG · {{ currentSeries.name }}</span></div>
            <div class="series-banner-overlay">
              <span class="series-banner-action">探索「{{ currentSeries.name }}」系列 <i>→</i></span>
            </div>
          </div>
        </router-link>
        <div class="series-shelf">
          <div class="series-meta">
            <div class="series-meta-header">
              <p class="eyebrow">SELECTED SERIES · 0{{ seriesIndex + 1 }}</p>
              <h3>{{ currentSeries.name }}</h3>
              <p class="series-desc">{{ currentSeries.description || `浏览巧侬${currentSeries.name}已公开的系列与产品资料。` }}</p>
            </div>
            <div v-if="currentSeries.children?.length" class="series-taxonomy">
              <span class="series-taxonomy-label">子系列分类</span>
              <div class="series-children">
                <router-link v-for="child in currentSeries.children" :key="child.id" :to="`/products/${child.slug}`">{{ child.name }}</router-link>
              </div>
            </div>
            <router-link class="series-all-btn" :to="`/products/${currentSeries.slug}`">
              <span>查看全部 {{ currentSeries.name }} 产品</span>
              <i>→</i>
            </router-link>
          </div>
          <div class="series-products-panel">
            <div class="series-products-header">
              <span class="series-products-title">精选代表单品</span>
              <span class="series-products-badge">REPRESENTATIVE PRODUCTS</span>
            </div>
            <div v-if="seriesLoading" class="series-loading-box">
              <span class="series-loading-spinner"></span>
              <span>正在加载代表产品…</span>
            </div>
            <div v-else-if="seriesProducts.length" class="series-representatives">
              <router-link v-for="product in seriesProducts" :key="product.id" class="series-product-item" :to="`/product/${product.slug}`">
                <div class="series-product-thumb">
                  <img v-if="product.cover" :src="product.cover" :alt="product.name" loading="lazy" />
                  <span v-else>QIAONONG</span>
                </div>
                <div class="series-product-info">
                  <strong>{{ product.name }}</strong>
                  <span class="series-product-hint">查看详情 →</span>
                </div>
              </router-link>
            </div>
            <p v-else class="series-empty-products">该分类暂无上架代表产品</p>
          </div>
        </div>
      </div>
      <p v-else-if="!loading" class="empty-state">产品分类资料正在整理中。</p>
    </section>

    <section v-if="featuredProducts.length" class="content-section product-section">
      <header class="section-heading"><p class="eyebrow">FEATURED</p><h2>推荐产品</h2></header>
      <div class="product-grid"><ProductCard v-for="product in featuredProducts" :key="product.id" :product="product" /></div>
    </section>

    <section class="brand-intro">
      <div class="brand-copy"><p class="eyebrow">ABOUT QIAONONG</p><h2>{{ siteState.settings.home_intro_title || '关于巧侬' }}</h2><p>{{ siteState.settings.home_intro_body || '品牌资料将在核验后由管理员后台发布。' }}</p><router-link class="text-link" to="/brand">阅读品牌介绍 →</router-link></div>
      <div class="brand-image"><img v-if="siteState.settings.home_intro_image" :src="siteState.settings.home_intro_image" alt="巧侬品牌介绍" /><span v-else>QIAONONG</span></div>
    </section>
  </main>
</template>
