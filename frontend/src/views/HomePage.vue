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
const seriesProductCache = new Map()
let slideTimer
const currentSlide = computed(() => slides.value[slideIndex.value])
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
  if (!autoplayPaused.value && slides.value.length > 1) {
    slideIndex.value = (slideIndex.value + 1) % slides.value.length
  }
}

function selectSlide(index) {
  slideIndex.value = index
  window.clearInterval(slideTimer)
  slideTimer = window.setInterval(nextSlide, 5000)
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
    if (slides.value.length > 1) slideTimer = window.setInterval(nextSlide, 5000)
  }
})

onBeforeUnmount(() => window.clearInterval(slideTimer))
</script>

<template>
  <main>
    <section class="hero" :class="{ 'image-only': currentSlide?.image && !showHeroCopy, 'has-image': currentSlide?.image, 'with-copy': currentSlide?.image && showHeroCopy, clickable: currentSlide?.link_url }" @mouseenter="autoplayPaused = true" @mouseleave="autoplayPaused = false" @focusin="autoplayPaused = true" @focusout="autoplayPaused = false">
      <picture v-if="currentSlide?.image" class="hero-media">
        <source media="(max-width: 640px)" :srcset="currentSlide.mobile_image || currentSlide.image" />
        <img :src="currentSlide.image" :alt="currentSlide.title || '巧侬花田首页轮播图'" />
      </picture>
      <router-link v-if="currentSlide?.link_url" class="hero-slide-link" :to="currentSlide.link_url" :aria-label="`查看第 ${slideIndex + 1} 张轮播图内容`"></router-link>
      <div v-if="showHeroCopy" class="hero-content">
        <p class="eyebrow">QIAONONG · EST.</p>
        <h1 v-if="heroTitle">{{ heroTitle }}</h1>
        <p v-if="heroSubtitle">{{ heroSubtitle }}</p>
        <router-link v-if="currentSlide?.link_url" class="outline-link" :to="currentSlide.link_url">了解更多</router-link>
        <router-link v-else class="outline-link" to="/products">浏览产品</router-link>
      </div>
      <div v-if="slides.length > 1" class="slide-dots"><button v-for="(_, index) in slides" :key="index" :class="{ active: index === slideIndex }" :aria-current="index === slideIndex ? 'true' : undefined" :aria-label="`切换到第 ${index + 1} 张`" @click.stop="selectSlide(index)"></button></div>
    </section>

    <section class="content-section series-section">
      <header class="section-heading"><p class="eyebrow">PRODUCT SERIES</p><h2>产品系列</h2><router-link to="/products">查看全部</router-link></header>
      <div v-if="siteState.categories.length" class="series-tabs" role="tablist" aria-label="产品系列">
        <button v-for="(category, index) in siteState.categories" :key="category.id" type="button" role="tab" :class="{ active: index === seriesIndex }" :aria-selected="index === seriesIndex" @click="selectSeries(index)"><small>0{{ index + 1 }}</small>{{ category.name }}</button>
      </div>
      <div v-if="currentSeries" class="series-showcase">
        <div class="series-backdrop" aria-hidden="true">
          <template v-if="currentSeries.banner">
            <img class="series-backdrop-ambient" :src="currentSeries.banner" alt="" />
            <img class="series-backdrop-artwork" :src="currentSeries.banner" alt="" />
          </template>
          <div v-else class="series-placeholder"><span>QIAONONG</span></div>
        </div>
        <router-link class="series-visual" :to="`/products/${currentSeries.slug}`">
          <span class="series-visual-label">探索 {{ currentSeries.name }} <i>→</i></span>
        </router-link>
        <div class="series-copy">
          <div>
            <p class="eyebrow">SELECTED SERIES</p>
            <h3>{{ currentSeries.name }}</h3>
            <p>{{ currentSeries.description || `浏览巧侬${currentSeries.name}已公开的系列与产品资料。` }}</p>
            <div v-if="currentSeries.children?.length" class="series-children">
              <router-link v-for="child in currentSeries.children" :key="child.id" :to="`/products/${child.slug}`">{{ child.name }}</router-link>
            </div>
          </div>
          <div class="series-representatives">
            <p v-if="seriesLoading" class="series-loading">正在加载代表产品…</p>
            <template v-else>
              <router-link v-for="product in seriesProducts" :key="product.id" :to="`/product/${product.slug}`">
                <img v-if="product.cover" :src="product.cover" :alt="product.name" loading="lazy" />
                <span v-else>QIAONONG</span>
                <strong>{{ product.name }}</strong>
              </router-link>
            </template>
          </div>
          <router-link class="series-all-link" :to="`/products/${currentSeries.slug}`">查看全部 {{ currentSeries.name }}产品 <span>→</span></router-link>
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
