<script setup>
import { onMounted, reactive, ref, watch } from 'vue'

import { api } from '../api'


const props = defineProps({ mode: { type: String, required: true } })
const slides = ref([])
const error = ref('')
const message = ref('')
const site = reactive({
  company_name: '', phone: '', email: '', address: '', footer_text: '',
  icp_number: '', icp_url: 'https://beian.miit.gov.cn/', logo: '', social_qr: '',
})
const slideForm = reactive(emptySlide())

function emptySlide() {
  return { id: null, title: '', subtitle: '', link_url: '', sort_order: 0, is_active: true, image: '', mobile_image: '' }
}

function replace(target, source) {
  for (const key of Object.keys(target)) target[key] = source[key] ?? ''
}

async function load() {
  error.value = ''
  try {
    if (props.mode === 'company') replace(site, await api('/api/admin/content/site/'))
    else slides.value = await api('/api/admin/content/slides/')
  } catch (reason) {
    error.value = reason.message
  }
}

function sitePayload() {
  const form = new FormData()
  const textFields = ['company_name', 'phone', 'email', 'address', 'footer_text', 'icp_number', 'icp_url']
  textFields.forEach((key) => form.append(key, site[key] || ''))
  const files = { logo: '#site-logo', social_qr: '#site-social-qr' }
  Object.entries(files).forEach(([key, selector]) => {
    const file = document.querySelector(selector)?.files[0]
    if (file) form.append(key, file)
  })
  return form
}

async function saveSite() {
  await perform(async () => {
    replace(site, await api('/api/admin/content/site/', { method: 'PATCH', body: sitePayload() }))
  }, '公司信息已保存')
}

function slidePayload() {
  const form = new FormData()
  form.append('title', slideForm.title || '')
  form.append('subtitle', slideForm.subtitle || '')
  form.append('link_url', slideForm.link_url || '')
  form.append('sort_order', Number(slideForm.sort_order) || 0)
  form.append('is_active', slideForm.is_active)
  const image = document.querySelector('#slide-image')?.files[0]
  if (image) form.append('image', image)
  const mobileImage = document.querySelector('#slide-mobile-image')?.files[0]
  if (mobileImage) form.append('mobile_image', mobileImage)
  return form
}

async function saveSlide() {
  await perform(async () => {
    const path = slideForm.id ? `/api/admin/content/slides/${slideForm.id}/` : '/api/admin/content/slides/'
    await api(path, { method: slideForm.id ? 'PATCH' : 'POST', body: slidePayload() })
    replace(slideForm, emptySlide())
    await load()
  }, '轮播图已保存')
}

async function removeSlide(id, label) {
  if (!window.confirm(`确认删除“${label}”？`)) return
  await perform(async () => {
    await api(`/api/admin/content/slides/${id}/`, { method: 'DELETE' })
    await load()
  }, '轮播图已删除')
}

async function perform(action, success) {
  error.value = ''
  message.value = ''
  try {
    await action()
    message.value = success
  } catch (reason) {
    error.value = reason.message
  }
}

onMounted(load)
watch(() => props.mode, load)
</script>

<template>
  <section class="page-section">
    <div class="page-heading"><div><p class="eyebrow">{{ mode === 'company' ? 'COMPANY' : 'CAROUSEL' }}</p><h1>{{ mode === 'company' ? '公司信息' : '首页轮播' }}</h1></div></div>
    <p v-if="error" class="message error">{{ error }}</p>
    <p v-if="message" class="message success">{{ message }}</p>

    <form v-if="mode === 'company'" class="panel form-grid" @submit.prevent="saveSite">
      <div class="panel-heading"><h2>公司与联系资料</h2></div>
      <label>公司名称<input v-model.trim="site.company_name" /></label>
      <label>联系电话<input v-model.trim="site.phone" /></label>
      <label>联系邮箱<input v-model.trim="site.email" type="email" /></label>
      <label>联系地址<input v-model.trim="site.address" /></label>
      <label>Logo<input id="site-logo" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="site.logo" :href="site.logo" target="_blank">查看当前图片</a></label>
      <label>微信二维码<input id="site-social-qr" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="site.social_qr" :href="site.social_qr" target="_blank">查看当前图片</a></label>
      <label>ICP备案号<input v-model.trim="site.icp_number" /></label>
      <label>备案链接<input v-model.trim="site.icp_url" type="url" /></label>
      <label class="wide">页脚补充文字<input v-model.trim="site.footer_text" /></label>
      <div class="wide actions"><button class="primary-button" type="submit">保存公司信息</button></div>
    </form>

    <template v-else>
      <form class="panel form-grid" @submit.prevent="saveSlide">
        <div class="panel-heading"><h2>{{ slideForm.id ? '编辑轮播图' : '新增轮播图' }}</h2><button v-if="slideForm.id" class="text-button" type="button" @click="replace(slideForm, emptySlide())">新增另一张</button></div>
        <label>标题<input v-model.trim="slideForm.title" /></label><label>副标题<input v-model.trim="slideForm.subtitle" /></label>
        <label class="wide">链接<input v-model.trim="slideForm.link_url" placeholder="例如 /products/skin-care" /></label>
        <label>桌面端图片<input id="slide-image" accept="image/jpeg,image/png,image/webp" :required="!slideForm.id" type="file" /><a v-if="slideForm.image" :href="slideForm.image" target="_blank">查看当前桌面图</a></label>
        <label>手机端图片（可选）<input id="slide-mobile-image" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="slideForm.mobile_image" :href="slideForm.mobile_image" target="_blank">查看当前手机图</a><span v-else>未上传时使用桌面图兜底</span></label>
        <label>排序<input v-model.number="slideForm.sort_order" min="0" type="number" /></label>
        <label class="check"><input v-model="slideForm.is_active" type="checkbox" />启用</label>
        <div class="wide actions"><button class="primary-button" type="submit">保存轮播图</button></div>
      </form>
      <div class="panel"><h2>轮播图列表</h2><div class="card-list"><article v-for="item in slides" :key="item.id"><img :src="item.image" :alt="item.title" /><div><strong>{{ item.title || '无标题轮播图' }}</strong><p>{{ item.subtitle }}</p><p>手机图：<a v-if="item.mobile_image" :href="item.mobile_image" target="_blank">查看</a><span v-else>使用桌面图兜底</span></p></div><div class="row-actions"><button class="text-button" @click="replace(slideForm, { ...emptySlide(), ...item })">编辑</button><button class="text-button danger" @click="removeSlide(item.id, item.title || '轮播图')">删除</button></div></article></div></div>
    </template>
  </section>
</template>
