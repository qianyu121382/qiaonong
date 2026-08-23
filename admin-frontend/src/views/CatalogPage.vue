<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { api, appendValue } from '../api'


const categories = ref([])
const products = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const productForm = reactive(emptyProduct())
const galleryFile = ref(null)
const galleryAlt = ref('')

const categoryOptions = computed(() => categories.value.map((category) => ({
  ...category,
  label: category.parent ? `　└ ${category.name}` : category.name,
})))

function emptyProduct() {
  return {
    id: null, category: '', name: '', tag: '', summary: '', specification: '',
    description: '', sort_order: 0, is_featured: false, is_active: false,
    cover: '', hover_image: '', images: [],
  }
}

function replace(target, source) {
  Object.keys(target).forEach((key) => { target[key] = source[key] ?? emptyValue(target[key]) })
}

function emptyValue(value) {
  if (typeof value === 'boolean') return false
  if (typeof value === 'number') return 0
  if (Array.isArray(value)) return []
  return ''
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    ;[categories.value, products.value] = await Promise.all([
      api('/api/admin/catalog/categories/'),
      api('/api/admin/catalog/products/'),
    ])
  } catch (reason) {
    error.value = reason.message
  } finally {
    loading.value = false
  }
}

function editProduct(product) {
  replace(productForm, { ...emptyProduct(), ...product })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function productPayload() {
  const form = new FormData()
  appendValue(form, 'category', productForm.category)
  appendValue(form, 'name', productForm.name)
  form.append('tag', productForm.tag || '')
  form.append('summary', productForm.summary || '')
  form.append('specification', productForm.specification || '')
  form.append('description', productForm.description || '')
  form.append('sort_order', Number(productForm.sort_order) || 0)
  form.append('is_featured', productForm.is_featured)
  form.append('is_active', productForm.is_active)
  const cover = document.querySelector('#product-cover')?.files[0]
  const hover = document.querySelector('#product-hover')?.files[0]
  if (cover) form.append('cover', cover)
  if (hover) form.append('hover_image', hover)
  return form
}

async function saveProduct() {
  await perform(async () => {
    const path = productForm.id
      ? `/api/admin/catalog/products/${productForm.id}/`
      : '/api/admin/catalog/products/'
    const saved = await api(path, {
      method: productForm.id ? 'PATCH' : 'POST',
      body: productPayload(),
    })
    replace(productForm, { ...emptyProduct(), ...saved })
    await load()
  }, '产品已保存')
}

async function uploadGallery() {
  if (!productForm.id || !galleryFile.value) return
  await perform(async () => {
    const form = new FormData()
    form.append('product', productForm.id)
    form.append('image', galleryFile.value)
    form.append('alt_text', galleryAlt.value)
    form.append('sort_order', productForm.images.length)
    await api('/api/admin/catalog/product-images/', { method: 'POST', body: form })
    galleryFile.value = null
    galleryAlt.value = ''
    const updated = await api(`/api/admin/catalog/products/${productForm.id}/`)
    replace(productForm, { ...emptyProduct(), ...updated })
    await load()
  }, '详情图片已上传')
}

async function remove(type, id, label) {
  if (!window.confirm(`确认删除“${label}”？`)) return
  const base = type === 'product' ? 'products' : 'product-images'
  await perform(async () => {
    await api(`/api/admin/catalog/${base}/${id}/`, { method: 'DELETE' })
    if (type === 'gallery') {
      const updated = await api(`/api/admin/catalog/products/${productForm.id}/`)
      replace(productForm, { ...emptyProduct(), ...updated })
    }
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
    <div class="page-heading"><div><p class="eyebrow">PRODUCTS</p><h1>产品管理</h1></div></div>
    <p v-if="error" class="message error">{{ error }}</p>
    <p v-if="message" class="message success">{{ message }}</p>

    <form class="panel form-grid" @submit.prevent="saveProduct">
      <div class="panel-heading"><h2>{{ productForm.id ? '编辑产品' : '新增产品' }}</h2><button v-if="productForm.id" class="text-button" type="button" @click="replace(productForm, emptyProduct())">新增另一产品</button></div>
      <label>名称<input v-model.trim="productForm.name" required /></label>
      <label>所属分类<select v-model="productForm.category" required><option value="" disabled>请选择</option><option v-for="item in categoryOptions" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
      <label>标签<input v-model.trim="productForm.tag" /></label>
      <label>规格<input v-model.trim="productForm.specification" /></label>
      <label>排序<input v-model.number="productForm.sort_order" min="0" type="number" /></label>
      <label class="wide">摘要<textarea v-model="productForm.summary" rows="3"></textarea></label>
      <label class="wide">详情正文<textarea v-model="productForm.description" rows="8"></textarea></label>
      <label>封面图<input id="product-cover" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="productForm.cover" :href="productForm.cover" target="_blank">查看当前图片</a></label>
      <label>悬停图<input id="product-hover" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="productForm.hover_image" :href="productForm.hover_image" target="_blank">查看当前图片</a></label>
      <label class="check"><input v-model="productForm.is_featured" type="checkbox" />首页推荐</label>
      <label class="check"><input v-model="productForm.is_active" type="checkbox" />上架公开</label>
      <div class="wide actions"><button class="primary-button" type="submit">保存产品</button></div>
    </form>

    <div v-if="productForm.id" class="panel">
      <h2>产品详情图片</h2>
      <div class="gallery-admin"><div v-for="image in productForm.images" :key="image.id"><img :src="image.image" :alt="image.alt_text" /><button class="text-button danger" @click="remove('gallery', image.id, '这张图片')">删除</button></div></div>
      <div class="inline-form"><input accept="image/jpeg,image/png,image/webp" type="file" @change="galleryFile = $event.target.files[0]" /><input v-model="galleryAlt" placeholder="图片说明（推荐填写）" /><button class="secondary-button" :disabled="!galleryFile" type="button" @click="uploadGallery">上传</button></div>
    </div>

    <div class="panel">
      <h2>产品列表</h2>
      <p v-if="loading">加载中…</p>
      <div v-else class="table-wrap"><table><thead><tr><th>产品</th><th>分类</th><th>状态</th><th>推荐</th><th></th></tr></thead><tbody><tr v-for="item in products" :key="item.id"><td>{{ item.name }}</td><td>{{ categories.find((category) => category.id === item.category)?.name }}</td><td><span class="status" :class="{ off: !item.is_active }">{{ item.is_active ? '已上架' : '已下架' }}</span></td><td>{{ item.is_featured ? '是' : '—' }}</td><td class="row-actions"><button class="text-button" @click="editProduct(item)">编辑</button><button class="text-button danger" @click="remove('product', item.id, item.name)">删除</button></td></tr></tbody></table></div>
    </div>
  </section>
</template>
