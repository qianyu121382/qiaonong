<script setup>
import { siteState } from '../stores/site'
</script>

<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand"><small>QIAONONG</small><strong>{{ siteState.settings.site_name || '巧侬' }}</strong><p>{{ siteState.settings.footer_text }}</p></div>
      <div><h2>网站导航</h2><router-link to="/brand">品牌介绍</router-link><router-link to="/products">产品中心</router-link><router-link to="/contact">联系我们</router-link></div>
      <div><h2>政策信息</h2><router-link to="/policy/usage-policy">使用政策</router-link><router-link to="/policy/privacy-policy">隐私条款</router-link><router-link to="/policy/cookies-policy">Cookies 政策</router-link></div>
      <div><h2>联系方式</h2><p v-if="siteState.settings.phone">{{ siteState.settings.phone }}</p><p v-if="siteState.settings.email">{{ siteState.settings.email }}</p><p v-if="siteState.settings.address">{{ siteState.settings.address }}</p><p v-if="!siteState.settings.phone && !siteState.settings.email && !siteState.settings.address">联系资料待更新</p></div>
    </div>
    <div class="footer-bottom">
      <span>© {{ new Date().getFullYear() }} {{ siteState.settings.company_name || siteState.settings.site_name || '巧侬' }}</span>
      <a v-if="siteState.settings.icp_number" :href="siteState.settings.icp_url" rel="noopener" target="_blank">{{ siteState.settings.icp_number }}</a>
    </div>
  </footer>
</template>
