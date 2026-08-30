<script setup>
import { computed } from 'vue'

import { siteState } from '../stores/site'


const phoneHref = computed(() => `tel:${String(siteState.settings.phone || '').replace(/[^\d+]/g, '')}`)
</script>

<template>
  <nav class="mobile-contact-bar" aria-label="快捷联系">
    <a v-if="siteState.settings.phone" :href="phoneHref">电话</a>
    <router-link to="/products">产品</router-link>
    <router-link to="/contact">联系</router-link>
  </nav>
</template>
