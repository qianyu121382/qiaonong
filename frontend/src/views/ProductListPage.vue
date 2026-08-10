<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import ProductCard from '../components/ProductCard.vue'
import { loadSite, siteState } from '../stores/site'
import { setPageSeo } from '../seo'


const props = defineProps({ searchMode: { type: Boolean, default: false } })
const route = useRoute()
const router = useRouter()
const products = ref([])
const loading = ref(true)
const error = ref('')
const searchInput = ref('')

const flatCategories = computed(() => siteState.categories.flatMap((item) => [item, ...(item.children || [])]))
const currentCategory = computed(() => flatCategories.value.find((item) => item.slug === route.params.category))
const currentRootCategory = computed(() => siteState.categories.find((item) => item.slug === route.params.category || item.children?.some((child) => child.slug === route.params.category)))
const heroImage = computed(() => props.searchMode ? '' : currentRootCategory.value?.banner || '')
const pageTitle = computed(() => props.searchMode ? `“${route.query.q || ''}”的搜索结果` : currentCategory.value?.name || '全部产品')
const pageDescription = computed(() => currentCategory.value?.description || (props.searchMode ? '按产品名称、标签、摘要和规格查找。' : ''))

async function load() {
  loading.value = true
  error.value = ''
  await loadSite()
  const params = new URLSearchParams()
  if (props.searchMode && route.query.q) params.set('search', route.query.q)
  if (!props.searchMode && route.params.category) params.set('category', route.params.category)
  searchInput.value = route.query.q || ''
  try {
    products.value = await api(`/api/catalog/products/?${params}`)
    if (!props.searchMode) {
      const title = currentCategory.value?.name || '全部产品'
      setPageSeo({
        title: `${title} - 巧侬花田`,
        description: currentCategory.value?.description || '浏览巧侬花田已公开的护肤、眼部、水光、彩妆、院护及医美产品资料。',
        path: route.params.category ? `/products/${route.params.category}` : '/products',
      })
    }
  } catch (reason) {
    error.value = reason.message
    products.value = []
  } finally {
    loading.value = false
  }
}

function search() {
  if (searchInput.value.trim()) router.push({ name: 'search', query: { q: searchInput.value.trim() } })
}

watch(() => route.fullPath, load, { immediate: true })
</script>

<template>
  <main>
    <section class="page-hero compact" :class="{ 'with-image': heroImage }" :style="heroImage ? { backgroundImage: `linear-gradient(90deg, rgba(8,24,18,.76), rgba(8,24,18,.22) 62%, rgba(8,24,18,.06)), url(${heroImage})` } : {}">
      <div class="page-hero-copy"><p class="eyebrow">PRODUCT SERIES</p><h1>{{ pageTitle }}</h1><p v-if="pageDescription">{{ pageDescription }}</p></div>
    </section>
    <section class="catalog-layout content-section">
      <aside class="category-sidebar">
        <router-link :class="{ active: !route.params.category && !searchMode }" to="/products">全部产品</router-link>
        <template v-for="category in siteState.categories" :key="category.id">
          <router-link class="root-category" :class="{ active: route.params.category === category.slug }" :to="`/products/${category.slug}`">{{ category.name }}</router-link>
          <router-link v-for="child in category.children" :key="child.id" class="child-category" :class="{ active: route.params.category === child.slug }" :to="`/products/${child.slug}`">{{ child.name }}</router-link>
        </template>
      </aside>
      <div class="catalog-content">
        <form class="catalog-search" @submit.prevent="search"><input v-model="searchInput" aria-label="搜索产品" placeholder="搜索产品" /><button>搜索</button></form>
        <p v-if="loading" class="empty-state">正在加载产品…</p>
        <p v-else-if="error" class="empty-state error-text">{{ error }}</p>
        <div v-else-if="products.length" class="product-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div>
        <p v-else class="empty-state">当前没有符合条件的公开产品。</p>
      </div>
    </section>
  </main>
</template>
