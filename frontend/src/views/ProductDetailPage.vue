<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api } from '../api'


const route = useRoute()
const product = ref(null)
const selectedImage = ref('')
const loading = ref(true)
const error = ref('')
const gallery = computed(() => {
  if (!product.value) return []
  const images = []
  if (product.value.cover) images.push({ id: 'cover', image: product.value.cover, alt_text: product.value.name })
  images.push(...(product.value.images || []))
  return images
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    product.value = await api(`/api/catalog/products/${route.params.slug}/`)
    selectedImage.value = product.value.cover || product.value.images?.[0]?.image || ''
    document.title = `${product.value.name} - 巧侬`
  } catch (reason) {
    error.value = reason.message
  } finally {
    loading.value = false
  }
}

watch(() => route.params.slug, load, { immediate: true })
</script>

<template>
  <main class="content-section product-detail-page">
    <p v-if="loading" class="empty-state">正在加载产品资料…</p>
    <p v-else-if="error" class="empty-state error-text">{{ error }}</p>
    <template v-else-if="product">
      <nav class="breadcrumb"><router-link to="/products">产品中心</router-link><span>/</span><router-link :to="`/products/${product.category.slug}`">{{ product.category.name }}</router-link><span>/</span><span>{{ product.name }}</span></nav>
      <section class="product-overview">
        <div class="product-gallery">
          <div class="thumbnails"><button v-for="image in gallery" :key="image.id" :class="{ active: selectedImage === image.image }" @click="selectedImage = image.image"><img :src="image.image" :alt="image.alt_text || product.name" /></button></div>
          <div class="main-product-image"><img v-if="selectedImage" :src="selectedImage" :alt="product.name" /><span v-else>QIAONONG</span></div>
        </div>
        <div class="product-summary"><p class="eyebrow">{{ product.tag || product.category.name }}</p><h1>{{ product.name }}</h1><p class="lead">{{ product.summary }}</p><dl v-if="product.specification"><dt>产品规格</dt><dd>{{ product.specification }}</dd></dl><router-link class="outline-link dark" to="/contact">联系我们</router-link></div>
      </section>
      <section v-if="product.description" class="product-description"><p class="eyebrow">PRODUCT DETAILS</p><h2>产品详情</h2><div class="rich-text">{{ product.description }}</div></section>
      <section v-if="product.images?.length" class="detail-images"><img v-for="image in product.images" :key="image.id" :src="image.image" :alt="image.alt_text || product.name" loading="lazy" /></section>
    </template>
  </main>
</template>
