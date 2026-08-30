<script setup>
import { onMounted, ref } from 'vue'

import { api } from '../api'
import { loadSite, siteState } from '../stores/site'


const page = ref(null)

onMounted(async () => {
  await loadSite()
  page.value = await api('/api/content/pages/contact/').catch(() => null)
})
</script>

<template>
  <main>
    <section class="page-hero compact"><p class="eyebrow">CONTACT</p><h1>{{ page?.title || '联系我们' }}</h1><p v-if="page?.summary">{{ page.summary }}</p></section>
    <section class="contact-grid content-section">
      <div class="contact-copy"><h2>{{ siteState.settings.company_name || '巧侬' }}</h2><div v-if="page?.body" class="rich-text">{{ page.body }}</div><p v-else>如需了解产品资料，请通过已公布的联系方式与我们联系。</p></div>
      <dl class="contact-details">
        <div><dt>联系电话</dt><dd><a v-if="siteState.settings.phone" :href="`tel:${siteState.settings.phone}`">{{ siteState.settings.phone }}</a><span v-else>待更新</span></dd></div>
        <div><dt>联系邮箱</dt><dd>{{ siteState.settings.email || '待更新' }}</dd></div>
        <div><dt>联系地址</dt><dd>{{ siteState.settings.address || '待更新' }}</dd></div>
      </dl>
      <img v-if="siteState.settings.social_qr" class="contact-qr" :src="siteState.settings.social_qr" alt="巧侬联系二维码" />
    </section>
  </main>
</template>
