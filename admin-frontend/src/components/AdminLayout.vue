<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AdminIcon from './AdminIcon.vue'
import AdminToast from './AdminToast.vue'
import { authState, logout } from '../stores/auth'
import { addView, closeView, tagsViewState } from '../stores/tagsView'
import { showToast } from '../stores/toast'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const routeBreadcrumbs = computed(() => {
  if (route.name === 'dashboard' || route.path === '/') {
    return [{ title: '首页', path: '/' }]
  }
  const map = {
    products: { parent: '业务管理', title: '产品管理' },
    carousel: { parent: '内容管理', title: '首页轮播' },
    company: { parent: '系统设置', title: '公司信息' },
  }
  const item = map[route.name] || { parent: '系统管理', title: '当前页面' }
  return [
    { title: '首页', path: '/' },
    { title: item.parent },
    { title: item.title, active: true },
  ]
})

function handleTabClick(tag) {
  router.push(tag.path)
}

function handleTabClose(tag) {
  const next = closeView(tag.path)
  if (next && route.path === tag.path) {
    router.push(next.path)
  }
}

async function handleLogout() {
  try {
    await logout()
    showToast('退出登录成功', 'success')
    router.replace({ name: 'login' })
  } catch (err) {
    showToast(err.message || '退出失败', 'error')
  }
}

onMounted(() => {
  addView(route)
})

watch(
  () => route.path,
  () => {
    addView(route)
  }
)
</script>

<template>
  <div class="ry-app-wrapper">
    <!-- Global RuoYi Toast Notification -->
    <AdminToast />

    <!-- Left Sidebar -->
    <aside class="ry-sidebar-container" :style="{ width: isCollapse ? '64px' : '220px' }">
      <div class="ry-sidebar-logo">
        <div class="ry-logo-icon">Q</div>
        <span v-if="!isCollapse" class="ry-logo-title">巧侬官网管理系统</span>
      </div>

      <ul class="ry-menu">
        <router-link to="/" class="ry-menu-item" title="工作台">
          <AdminIcon name="dashboard" class="ry-menu-icon" :size="16" />
          <span v-if="!isCollapse">工作台</span>
        </router-link>

        <router-link to="/products" class="ry-menu-item" title="产品管理">
          <AdminIcon name="products" class="ry-menu-icon" :size="16" />
          <span v-if="!isCollapse">产品管理</span>
        </router-link>

        <router-link to="/carousel" class="ry-menu-item" title="首页轮播">
          <AdminIcon name="carousel" class="ry-menu-icon" :size="16" />
          <span v-if="!isCollapse">首页轮播</span>
        </router-link>

        <router-link to="/company" class="ry-menu-item" title="公司信息">
          <AdminIcon name="company" class="ry-menu-icon" :size="16" />
          <span v-if="!isCollapse">公司信息</span>
        </router-link>
      </ul>
    </aside>

    <!-- Right Main Container -->
    <div class="ry-main-container" :style="{ marginLeft: isCollapse ? '64px' : '220px' }">
      <!-- Navbar -->
      <header class="ry-navbar">
        <div class="ry-navbar-left">
          <div class="ry-hamburger" @click="isCollapse = !isCollapse">
            <AdminIcon name="menu" :size="18" />
          </div>

          <div class="ry-breadcrumb">
            <template v-for="(crumb, idx) in routeBreadcrumbs" :key="idx">
              <span
                v-if="crumb.path"
                class="ry-breadcrumb-item"
                style="cursor: pointer"
                @click="router.push(crumb.path)"
              >
                {{ crumb.title }}
              </span>
              <span v-else-if="crumb.active" class="ry-breadcrumb-active">
                {{ crumb.title }}
              </span>
              <span v-else class="ry-breadcrumb-item">
                {{ crumb.title }}
              </span>
              <span v-if="idx < routeBreadcrumbs.length - 1" class="ry-breadcrumb-separator">/</span>
            </template>
          </div>
        </div>

        <div class="ry-navbar-right">
          <a
            href="/"
            target="_blank"
            class="ry-nav-btn"
            title="新窗口打开公开官网首页"
          >
            <AdminIcon name="external" :size="14" />
            <span>前台官网</span>
          </a>

          <div class="ry-user-dropdown" @click="handleLogout" title="点击退出登录">
            <div class="ry-avatar">
              {{ (authState.user?.display_name || authState.user?.username || '管').charAt(0).toUpperCase() }}
            </div>
            <span class="ry-user-name">
              {{ authState.user?.display_name || authState.user?.username || '系统管理员' }}
            </span>
            <AdminIcon name="logout" :size="14" style="color: #909399;" />
          </div>
        </div>
      </header>

      <!-- RuoYi TagsView (Multi-tab bar) -->
      <nav class="ry-tags-view-container">
        <div
          v-for="tag in tagsViewState.visitedViews"
          :key="tag.path"
          class="ry-tags-view-item"
          :class="{ active: route.path === tag.path }"
          @click="handleTabClick(tag)"
        >
          <span>{{ tag.title }}</span>
          <span
            v-if="!tag.affix"
            class="ry-tags-close-icon"
            @click.stop="handleTabClose(tag)"
          >
            ✕
          </span>
        </div>
      </nav>

      <!-- Main Page Content -->
      <main class="ry-app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>
