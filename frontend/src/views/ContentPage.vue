<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api } from '../api'


const props = defineProps({ slug: { type: String, default: '' } })
const route = useRoute()
const page = ref(null)
const loading = ref(true)
const missing = ref(false)

async function load() {
  loading.value = true
  missing.value = false
  const slug = props.slug || route.params.slug
  try {
    page.value = await api(`/api/content/pages/${slug}/`)
    document.title = `${page.value.title} - 巧侬`
  } catch (error) {
    missing.value = error.status === 404
    page.value = null
  } finally {
    loading.value = false
  }
}

watch(() => [props.slug, route.params.slug], load, { immediate: true })
</script>

<template>
  <main>
    <p v-if="loading" class="empty-state standalone">正在加载…</p>
    <section v-else-if="page" class="editorial-page">
      <div class="page-hero compact" :class="{ 'with-image': page.image }" :style="page.image ? { backgroundImage: `linear-gradient(90deg, rgba(10,28,21,.76), rgba(10,28,21,.24) 62%, rgba(10,28,21,.08)), url(${page.image})` } : {}">
        <div class="page-hero-copy"><p class="eyebrow">QIAONONG</p><h1>{{ page.title }}</h1><p v-if="page.summary">{{ page.summary }}</p></div>
      </div>
      <div class="editorial-body"><div class="rich-text">{{ page.body }}</div></div>
    </section>
    <section v-else class="empty-state standalone"><h1>{{ missing ? '内容暂未发布' : '内容加载失败' }}</h1><p>该页面需要管理员核验资料后公开。</p><router-link class="text-link" to="/">返回首页 →</router-link></section>
  </main>
</template>
