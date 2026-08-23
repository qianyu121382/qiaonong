<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'
import AdminIcon from '../components/AdminIcon.vue'
import { authState } from '../stores/auth'

const router = useRouter()
const loading = ref(true)
const products = ref([])
const slides = ref([])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const stats = computed(() => {
  const totalProducts = products.value.length
  const activeProducts = products.value.filter((p) => p.is_active).length
  const featuredProducts = products.value.filter((p) => p.is_featured).length
  const totalSlides = slides.value.length
  const activeSlides = slides.value.filter((s) => s.is_active).length

  return {
    totalProducts,
    activeProducts,
    featuredProducts,
    totalSlides,
    activeSlides,
  }
})

async function fetchStats() {
  loading.value = true
  try {
    const [pList, sList] = await Promise.all([
      api('/api/admin/catalog/products/'),
      api('/api/admin/content/slides/'),
    ])
    products.value = pList || []
    slides.value = sList || []
  } catch {
    // fallback
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<template>
  <div class="ry-page-container">
    <!-- RuoYi Welcome Header Card -->
    <div class="ry-dashboard-welcome">
      <div style="display: flex; align-items: center; gap: 16px;">
        <div class="ry-avatar" style="width: 48px; height: 48px; font-size: 20px;">
          {{ (authState.user?.display_name || authState.user?.username || '管').charAt(0).toUpperCase() }}
        </div>
        <div>
          <h2 class="ry-welcome-title">
            {{ greeting }}，{{ authState.user?.display_name || authState.user?.username || '系统管理员' }}，欢迎使用巧侬企业官网管理系统！
          </h2>
          <p class="ry-welcome-desc">
            巧侬官网运行正常 · 独立数据架构 · 当前已配置产品 {{ stats.totalProducts }} 款，轮播图 {{ stats.totalSlides }} 张
          </p>
        </div>
      </div>
      <button class="ry-btn ry-btn-default ry-btn-sm" type="button" @click="fetchStats">
        <AdminIcon name="refresh" :size="13" />
        <span>刷新统计</span>
      </button>
    </div>

    <!-- 4 Stats Cards (RuoYi Classic) -->
    <div class="ry-dashboard-stats">
      <div class="ry-stat-card">
        <div class="ry-stat-info">
          <span class="ry-stat-label">产品库总数</span>
          <span class="ry-stat-val">{{ loading ? '-' : stats.totalProducts }}</span>
        </div>
        <div class="ry-stat-icon ry-stat-icon-blue">
          <AdminIcon name="products" :size="24" />
        </div>
      </div>

      <div class="ry-stat-card">
        <div class="ry-stat-info">
          <span class="ry-stat-label">已上架公开</span>
          <span class="ry-stat-val">{{ loading ? '-' : stats.activeProducts }}</span>
        </div>
        <div class="ry-stat-icon ry-stat-icon-green">
          <AdminIcon name="check-circle" :size="24" />
        </div>
      </div>

      <div class="ry-stat-card">
        <div class="ry-stat-info">
          <span class="ry-stat-label">首页爆款推荐</span>
          <span class="ry-stat-val">{{ loading ? '-' : stats.featuredProducts }}</span>
        </div>
        <div class="ry-stat-icon ry-stat-icon-orange">
          <AdminIcon name="star" :size="24" />
        </div>
      </div>

      <div class="ry-stat-card">
        <div class="ry-stat-info">
          <span class="ry-stat-label">首页轮播横幅</span>
          <span class="ry-stat-val">{{ loading ? '-' : stats.totalSlides }}</span>
        </div>
        <div class="ry-stat-icon ry-stat-icon-purple">
          <AdminIcon name="carousel" :size="24" />
        </div>
      </div>
    </div>

    <!-- 2 Column Layout (RuoYi Standard) -->
    <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 16px;">
      <!-- Quick Navigation Card -->
      <div class="ry-card">
        <div class="ry-card-header">
          <h3 class="ry-card-title">
            <AdminIcon name="dashboard" :size="16" />
            <span>核心业务入口</span>
          </h3>
        </div>
        <div class="ry-card-body" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px;">
          <div
            style="border: 1px solid var(--ry-border-lighter); border-radius: 4px; padding: 14px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s;"
            @click="router.push('/products')"
          >
            <div class="ry-stat-icon ry-stat-icon-blue" style="width: 40px; height: 40px;">
              <AdminIcon name="products" :size="20" />
            </div>
            <div>
              <strong style="font-size: 14px; color: var(--ry-text-primary);">产品管理</strong>
              <p style="margin: 2px 0 0; font-size: 12px; color: var(--ry-text-secondary);">
                新增产品、规格与相册
              </p>
            </div>
          </div>

          <div
            style="border: 1px solid var(--ry-border-lighter); border-radius: 4px; padding: 14px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s;"
            @click="router.push('/carousel')"
          >
            <div class="ry-stat-icon ry-stat-icon-purple" style="width: 40px; height: 40px;">
              <AdminIcon name="carousel" :size="20" />
            </div>
            <div>
              <strong style="font-size: 14px; color: var(--ry-text-primary);">首页轮播</strong>
              <p style="margin: 2px 0 0; font-size: 12px; color: var(--ry-text-secondary);">
                电脑/手机端横幅配置
              </p>
            </div>
          </div>

          <div
            style="border: 1px solid var(--ry-border-lighter); border-radius: 4px; padding: 14px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s;"
            @click="router.push('/company')"
          >
            <div class="ry-stat-icon ry-stat-icon-orange" style="width: 40px; height: 40px;">
              <AdminIcon name="company" :size="20" />
            </div>
            <div>
              <strong style="font-size: 14px; color: var(--ry-text-primary);">公司信息</strong>
              <p style="margin: 2px 0 0; font-size: 12px; color: var(--ry-text-secondary);">
                主体、Logo、二维码与备案
              </p>
            </div>
          </div>

          <a
            href="/"
            target="_blank"
            style="border: 1px solid var(--ry-border-lighter); border-radius: 4px; padding: 14px; cursor: pointer; display: flex; align-items: center; gap: 12px; text-decoration: none;"
          >
            <div class="ry-stat-icon ry-stat-icon-green" style="width: 40px; height: 40px;">
              <AdminIcon name="external" :size="20" />
            </div>
            <div>
              <strong style="font-size: 14px; color: var(--ry-text-primary);">前台官网</strong>
              <p style="margin: 2px 0 0; font-size: 12px; color: var(--ry-text-secondary);">
                新窗口预览公开页面效果
              </p>
            </div>
          </a>
        </div>
      </div>

      <!-- System / Compliance Notice Card -->
      <div class="ry-card">
        <div class="ry-card-header">
          <h3 class="ry-card-title">
            <AdminIcon name="shield" :size="16" />
            <span>系统信息与合规核验</span>
          </h3>
        </div>
        <div class="ry-card-body" style="font-size: 13px; color: var(--ry-text-regular); line-height: 1.8;">
          <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed var(--ry-border-lighter); padding: 4px 0;">
            <span>系统架构：</span>
            <strong>Vue 3 + Vite + Django API</strong>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed var(--ry-border-lighter); padding: 4px 0;">
            <span>项目边界：</span>
            <span class="ry-tag ry-tag-success">巧侬独立数据库与媒体</span>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed var(--ry-border-lighter); padding: 4px 0;">
            <span>工信部备案号：</span>
            <code>辽ICP备2026018730号-1</code>
          </div>
          <div style="display: flex; justify-content: space-between; padding: 4px 0;">
            <span>运营公司主体：</span>
            <span>鞍山鼎禾生物制药有限公司</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
