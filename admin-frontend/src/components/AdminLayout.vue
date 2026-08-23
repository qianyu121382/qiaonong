<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { authState, logout } from '../stores/auth'


const router = useRouter()
const menuOpen = ref(false)

async function signOut() {
  await logout()
  router.replace({ name: 'login' })
}
</script>

<template>
  <div class="admin-shell">
    <header class="mobile-bar">
      <strong>巧侬管理</strong>
      <button class="ghost-button" type="button" @click="menuOpen = !menuOpen">菜单</button>
    </header>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand-mark">
        <span>QIAONONG</span>
        <strong>巧侬网站管理</strong>
      </div>
      <nav @click="menuOpen = false">
        <router-link to="/">工作台</router-link>
        <router-link to="/products">产品管理</router-link>
        <router-link to="/carousel">首页轮播</router-link>
        <router-link to="/company">公司信息</router-link>
      </nav>
      <div class="account-block">
        <span>{{ authState.user?.display_name }}</span>
        <button class="text-button" type="button" @click="signOut">退出登录</button>
      </div>
    </aside>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>
