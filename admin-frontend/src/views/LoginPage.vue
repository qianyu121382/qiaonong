<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { login } from '../stores/auth'


const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await login(username.value, password.value)
    await router.replace({ name: 'dashboard' })
  } catch (reason) {
    error.value = reason.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <form class="login-card" @submit.prevent="submit">
      <p class="eyebrow">QIAONONG MANAGEMENT</p>
      <h1>巧侬网站管理</h1>
      <p class="muted">使用巧侬独立管理员账号登录</p>
      <label>用户名<input v-model.trim="username" autocomplete="username" required /></label>
      <label>密码<input v-model="password" type="password" autocomplete="current-password" required /></label>
      <p v-if="error" class="message error">{{ error }}</p>
      <button class="primary-button" :disabled="submitting" type="submit">
        {{ submitting ? '登录中…' : '登录' }}
      </button>
    </form>
  </main>
</template>
