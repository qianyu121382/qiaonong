<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { siteState } from '../stores/site'


const router = useRouter()
const menuOpen = ref(false)
const searchOpen = ref(false)
const keyword = ref('')

function closeMenu() {
  menuOpen.value = false
}

function submitSearch() {
  const value = keyword.value.trim()
  if (!value) return
  searchOpen.value = false
  menuOpen.value = false
  router.push({ name: 'search', query: { q: value } })
}
</script>

<template>
  <header class="site-header">
    <router-link class="site-logo" to="/" @click="closeMenu">
      <img v-if="siteState.settings.logo" :src="siteState.settings.logo" :alt="siteState.settings.site_name" />
      <span v-else><small>QIAONONG</small><strong>{{ siteState.settings.site_name || '巧侬' }}</strong></span>
    </router-link>
    <button class="menu-toggle" :aria-expanded="menuOpen" aria-label="打开导航" @click="menuOpen = !menuOpen"><i></i><i></i><i></i></button>
    <nav :class="{ open: menuOpen }" @click="closeMenu">
      <router-link to="/brand">品牌介绍</router-link>
      <div v-for="category in siteState.categories" :key="category.id" class="nav-group" :class="{ 'has-children': category.children?.length }">
        <router-link :to="`/products/${category.slug}`">{{ category.name }}</router-link>
        <div v-if="category.children?.length" class="nav-dropdown" :class="{ compact: category.children.length <= 3 }">
          <div class="nav-dropdown-head">
            <span>{{ category.name }}</span>
            <small>PRODUCT SERIES</small>
          </div>
          <div class="nav-dropdown-links">
            <router-link v-for="child in category.children" :key="child.id" :to="`/products/${child.slug}`">
              <span>{{ child.name }}</span><i>→</i>
            </router-link>
          </div>
          <router-link class="nav-dropdown-all" :to="`/products/${category.slug}`">查看全部 {{ category.name }}产品 <span>→</span></router-link>
        </div>
      </div>
      <router-link to="/contact">联系我们</router-link>
    </nav>
    <button class="search-toggle" aria-label="搜索" @click="searchOpen = !searchOpen">⌕</button>
    <form v-if="searchOpen" class="search-panel" @submit.prevent="submitSearch">
      <label for="site-search">搜索产品</label>
      <div><input id="site-search" v-model="keyword" autofocus placeholder="输入产品名称或关键词" /><button type="submit">搜索</button></div>
    </form>
  </header>
</template>
