<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import AdminIcon from '../components/AdminIcon.vue'
import AdminToast from '../components/AdminToast.vue'
import { login } from '../stores/auth'
import { showToast } from '../stores/toast'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  error.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    showToast('登录成功', 'success')
    await router.replace({ name: 'dashboard' })
  } catch (err) {
    error.value = err.message || '登录失败，请检查用户名或密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="ry-login-wrapper">
    <AdminToast />

    <form class="ry-login-form" @submit.prevent="handleLogin">
      <h3 class="ry-login-title">巧侬企业官网管理系统</h3>
      <p class="ry-login-sub">QIAONONG MANAGEMENT SYSTEM</p>

      <div
        v-if="error"
        style="background: #fef0f0; border: 1px solid #fde2e2; color: #f56c6c; padding: 8px 12px; border-radius: 4px; font-size: 13px; margin-bottom: 16px; display: flex; align-items: center; gap: 6px;"
      >
        <AdminIcon name="alert-circle" :size="14" />
        <span>{{ error }}</span>
      </div>

      <div class="ry-login-item">
        <AdminIcon name="user" class="ry-login-icon" :size="16" />
        <input
          v-model.trim="username"
          class="ry-login-input"
          placeholder="请输入账号"
          autocomplete="username"
          required
        />
      </div>

      <div class="ry-login-item">
        <AdminIcon name="lock" class="ry-login-icon" :size="16" />
        <input
          v-model="password"
          type="password"
          class="ry-login-input"
          placeholder="请输入密码"
          autocomplete="current-password"
          required
        />
      </div>

      <button
        class="ry-btn ry-btn-primary ry-login-btn"
        :disabled="loading"
        type="submit"
      >
        <span v-if="loading">登 录 中…</span>
        <span v-else>登 录</span>
      </button>

      <div class="ry-login-footer">
        <span>Copyright © 2026 巧侬花田 · 鞍山鼎禾生物制药有限公司</span>
      </div>
    </form>
  </div>
</template>
