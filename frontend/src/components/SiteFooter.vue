<script setup>
import { siteState } from '../stores/site'

const publicSecurityRecord = {
  number: '辽公网安备21030302000219号',
  url: 'https://beian.mps.gov.cn/#/query/webSearch?code=21030302000219',
}
</script>

<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand"><small>QIAONONG</small><strong>{{ siteState.settings.site_name || '巧侬' }}</strong><p>{{ siteState.settings.footer_text }}</p></div>
      <nav class="footer-links" aria-label="页脚导航"><router-link to="/">首页</router-link><router-link to="/brand">品牌介绍</router-link><router-link to="/products">产品中心</router-link><router-link to="/contact">联系我们</router-link></nav>
      <div class="footer-contact">
        <a v-if="siteState.settings.phone" class="footer-phone" :href="`tel:${siteState.settings.phone}`">{{ siteState.settings.phone }}</a>
        <div v-if="siteState.settings.social_qr" class="footer-wechat">
          <button type="button" aria-label="查看巧侬微信二维码">
            <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M9.6 4C5.4 4 2 6.8 2 10.2c0 1.9 1.1 3.6 2.8 4.7l-.7 2.2 2.6-1.3c.9.3 1.9.5 2.9.5h.6a5.4 5.4 0 0 1-.2-1.4c0-3.2 3-5.8 6.7-5.8h.7C16.7 6.2 13.5 4 9.6 4Zm-2.5 4.9a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm5 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"/><path d="M22 14.9c0-2.7-2.7-4.9-5.9-4.9s-5.9 2.2-5.9 4.9 2.7 4.9 5.9 4.9c.8 0 1.6-.1 2.3-.4l2.1 1-.5-1.8c1.2-.9 2-2.2 2-3.7Zm-7.9-.8a.8.8 0 1 1 0-1.6.8.8 0 0 1 0 1.6Zm4 0a.8.8 0 1 1 0-1.6.8.8 0 0 1 0 1.6Z"/></svg>
            <span>微信</span>
          </button>
          <div class="footer-qr-popover"><img :src="siteState.settings.social_qr" alt="巧侬微信二维码" /><small>微信扫码关注</small></div>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {{ new Date().getFullYear() }} {{ siteState.settings.company_name || siteState.settings.site_name || '巧侬' }}</span>
      <div class="footer-records">
        <a v-if="siteState.settings.icp_number" :href="siteState.settings.icp_url" rel="noopener" target="_blank">{{ siteState.settings.icp_number }}</a>
        <a class="public-security-record" :href="publicSecurityRecord.url" rel="noopener noreferrer" target="_blank">
          <img src="/gongan-beian.png" alt="" width="18" height="20" />
          <span>{{ publicSecurityRecord.number }}</span>
        </a>
      </div>
    </div>
  </footer>
</template>
