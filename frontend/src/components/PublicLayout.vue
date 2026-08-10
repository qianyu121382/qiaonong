<script setup>
import { onMounted } from 'vue'

import SiteFooter from './SiteFooter.vue'
import SiteHeader from './SiteHeader.vue'
import { loadSite } from '../stores/site'

onMounted(loadSite)
</script>

<template>
  <div class="site-shell">
    <SiteHeader />
    <router-view />
    <SiteFooter />
  </div>
</template>
