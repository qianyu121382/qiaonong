<script setup>
import { onMounted, reactive, ref } from 'vue'

import { api, appendValue } from '../api'


const activeTab = ref('site')
const pages = ref([])
const slides = ref([])
const error = ref('')
const message = ref('')
const site = reactive({
  site_name: '巧侬', home_title: '', home_subtitle: '', home_intro_title: '',
  home_intro_body: '', company_name: '', phone: '', email: '', address: '',
  footer_text: '', icp_number: '', icp_url: 'https://beian.miit.gov.cn/',
  logo: '', home_intro_image: '', social_qr: '',
})
const pageForm = reactive(emptyPage())
const slideForm = reactive(emptySlide())

function emptyPage() {
  return { id: null, slug: '', title: '', summary: '', body: '', sort_order: 0, is_active: false, legacy_id: '', image: '' }
}

function emptySlide() {
  return { id: null, title: '', subtitle: '', link_url: '', sort_order: 0, is_active: true, image: '', mobile_image: '' }
}

function replace(target, source) {
  for (const key of Object.keys(target)) target[key] = source[key] ?? ''
}

async function load() {
  try {
    const [siteData, pageData, slideData] = await Promise.all([
      api('/api/admin/content/site/'),
      api('/api/admin/content/pages/'),
      api('/api/admin/content/slides/'),
    ])
    replace(site, siteData)
    pages.value = pageData
    slides.value = slideData
  } catch (reason) {
    error.value = reason.message
  }
}

function sitePayload() {
  const form = new FormData()
  const textFields = [
    'site_name', 'home_title', 'home_subtitle', 'home_intro_title', 'home_intro_body',
    'company_name', 'phone', 'email', 'address', 'footer_text', 'icp_number', 'icp_url',
  ]
  textFields.forEach((key) => form.append(key, site[key] || ''))
  const files = { logo: '#site-logo', home_intro_image: '#site-intro-image', social_qr: '#site-social-qr' }
  Object.entries(files).forEach(([key, selector]) => {
    const file = document.querySelector(selector)?.files[0]
    if (file) form.append(key, file)
  })
  return form
}

async function saveSite() {
  await perform(async () => {
    const saved = await api('/api/admin/content/site/', { method: 'PATCH', body: sitePayload() })
    replace(site, saved)
  }, '网站设置已保存')
}

function pagePayload() {
  const form = new FormData()
  appendValue(form, 'slug', pageForm.slug)
  appendValue(form, 'title', pageForm.title)
  form.append('summary', pageForm.summary || '')
  form.append('body', pageForm.body || '')
  form.append('sort_order', Number(pageForm.sort_order) || 0)
  form.append('is_active', pageForm.is_active)
  if (pageForm.legacy_id) form.append('legacy_id', pageForm.legacy_id)
  const image = document.querySelector('#page-image')?.files[0]
  if (image) form.append('image', image)
  return form
}

async function savePage() {
  await perform(async () => {
    const path = pageForm.id ? `/api/admin/content/pages/${pageForm.id}/` : '/api/admin/content/pages/'
    await api(path, { method: pageForm.id ? 'PATCH' : 'POST', body: pagePayload() })
    replace(pageForm, emptyPage())
    await load()
  }, '内容页面已保存')
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

async function remove(kind, id, label) {
  if (!window.confirm(`确认删除“${label}”？`)) return
  await perform(async () => {
    await api(`/api/admin/content/${kind}/${id}/`, { method: 'DELETE' })
    await load()
  }, '已删除')
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
</script>

<template>
  <section class="page-section">
    <div class="page-heading"><div><p class="eyebrow">CONTENT</p><h1>网站内容</h1></div></div>
    <div class="tabs">
      <button :class="{ active: activeTab === 'site' }" @click="activeTab = 'site'">网站设置</button>
      <button :class="{ active: activeTab === 'pages' }" @click="activeTab = 'pages'">内容页面</button>
      <button :class="{ active: activeTab === 'slides' }" @click="activeTab = 'slides'">首页轮播</button>
    </div>
    <p v-if="error" class="message error">{{ error }}</p>
    <p v-if="message" class="message success">{{ message }}</p>

    <form v-if="activeTab === 'site'" class="panel form-grid" @submit.prevent="saveSite">
      <div class="panel-heading"><h2>全站与首页设置</h2></div>
      <label>网站名称<input v-model.trim="site.site_name" required /></label>
      <label>公司名称<input v-model.trim="site.company_name" placeholder="上线前必须核验" /></label>
      <label class="wide">首页标题<input v-model.trim="site.home_title" /></label>
      <label class="wide">首页副标题<textarea v-model="site.home_subtitle" rows="3"></textarea></label>
      <label>首页介绍标题<input v-model.trim="site.home_intro_title" /></label>
      <label>联系电话<input v-model.trim="site.phone" /></label>
      <label class="wide">首页介绍正文<textarea v-model="site.home_intro_body" rows="6"></textarea></label>
      <label>联系邮箱<input v-model.trim="site.email" type="email" /></label>
      <label>联系地址<input v-model.trim="site.address" /></label>
      <label>Logo<input id="site-logo" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="site.logo" :href="site.logo" target="_blank">查看当前图片</a></label>
      <label>首页介绍图片<input id="site-intro-image" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="site.home_intro_image" :href="site.home_intro_image" target="_blank">查看当前图片</a></label>
      <label>社交二维码<input id="site-social-qr" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="site.social_qr" :href="site.social_qr" target="_blank">查看当前图片</a></label>
      <label>ICP备案号<input v-model.trim="site.icp_number" placeholder="不得照搬旧站" /></label>
      <label class="wide">备案链接<input v-model.trim="site.icp_url" type="url" /></label>
      <label class="wide">页脚补充文字<input v-model.trim="site.footer_text" /></label>
      <div class="wide actions"><button class="primary-button" type="submit">保存网站设置</button></div>
    </form>

    <template v-else-if="activeTab === 'pages'">
      <form class="panel form-grid" @submit.prevent="savePage">
        <div class="panel-heading"><h2>{{ pageForm.id ? '编辑内容页面' : '新增内容页面' }}</h2><button v-if="pageForm.id" class="text-button" type="button" @click="replace(pageForm, emptyPage())">新增另一页面</button></div>
        <label>标题<input v-model.trim="pageForm.title" required /></label>
        <label>页面地址 slug<input v-model.trim="pageForm.slug" pattern="[-a-zA-Z0-9_]+" required /></label>
        <label class="wide">摘要<textarea v-model="pageForm.summary" rows="3"></textarea></label>
        <label class="wide">正文<textarea v-model="pageForm.body" rows="12"></textarea></label>
        <label>页面图片<input id="page-image" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="pageForm.image" :href="pageForm.image" target="_blank">查看当前图片</a></label>
        <label>排序<input v-model.number="pageForm.sort_order" min="0" type="number" /></label>
        <label>旧站栏目 ID<input v-model="pageForm.legacy_id" min="1" type="number" /></label>
        <label class="check"><input v-model="pageForm.is_active" type="checkbox" />公开显示</label>
        <div class="wide actions"><button class="primary-button" type="submit">保存页面</button></div>
      </form>
      <div class="panel"><h2>内容页面列表</h2><div class="table-wrap"><table><thead><tr><th>标题</th><th>slug</th><th>状态</th><th></th></tr></thead><tbody><tr v-for="item in pages" :key="item.id"><td>{{ item.title }}</td><td>{{ item.slug }}</td><td><span class="status" :class="{ off: !item.is_active }">{{ item.is_active ? '公开' : '隐藏' }}</span></td><td class="row-actions"><button class="text-button" @click="replace(pageForm, { ...emptyPage(), ...item })">编辑</button><button class="text-button danger" @click="remove('pages', item.id, item.title)">删除</button></td></tr></tbody></table></div></div>
    </template>

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
      <div class="panel"><h2>轮播图列表</h2><div class="card-list"><article v-for="item in slides" :key="item.id"><img :src="item.image" :alt="item.title" /><div><strong>{{ item.title || '无标题轮播图' }}</strong><p>{{ item.subtitle }}</p><p>手机图：<a v-if="item.mobile_image" :href="item.mobile_image" target="_blank">查看</a><span v-else>使用桌面图兜底</span></p></div><div class="row-actions"><button class="text-button" @click="replace(slideForm, { ...emptySlide(), ...item })">编辑</button><button class="text-button danger" @click="remove('slides', item.id, item.title || '轮播图')">删除</button></div></article></div></div>
    </template>
  </section>
</template>
