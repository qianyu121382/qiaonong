<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { api, appendValue } from '../api'


const categories = ref([])
const products = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const activeTab = ref('products')
const categoryForm = reactive(emptyCategory())
const productForm = reactive(emptyProduct())
const galleryFile = ref(null)
const galleryAlt = ref('')

const categoryOptions = computed(() => categories.value.map((category) => ({
  ...category,
  label: category.parent ? `　└ ${category.name}` : category.name,
})))

function emptyCategory() {
  return { id: null, name: '', slug: '', parent: '', description: '', sort_order: 0, is_active: true, legacy_id: '' }
}

function emptyProduct() {
  return { id: null, category: '', name: '', slug: '', tag: '', summary: '', specification: '', description: '', sort_order: 0, is_featured: false, is_active: false, legacy_id: '', cover: '', hover_image: '', images: [] }
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

function editCategory(category) {
  replace(categoryForm, { ...emptyCategory(), ...category, parent: category.parent || '' })
  activeTab.value = 'categories'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function editProduct(product) {
  replace(productForm, { ...emptyProduct(), ...product })
  activeTab.value = 'products'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function categoryPayload() {
  return {
    name: categoryForm.name,
    slug: categoryForm.slug,
    parent: categoryForm.parent || null,
    description: categoryForm.description,
    sort_order: Number(categoryForm.sort_order) || 0,
    is_active: categoryForm.is_active,
    legacy_id: categoryForm.legacy_id || null,
  }
}

async function saveCategory() {
  await perform(async () => {
    const path = categoryForm.id
      ? `/api/admin/catalog/categories/${categoryForm.id}/`
      : '/api/admin/catalog/categories/'
    await api(path, { method: categoryForm.id ? 'PATCH' : 'POST', body: categoryPayload() })
    replace(categoryForm, emptyCategory())
    await load()
  }, '分类已保存')
}

function productPayload() {
  const form = new FormData()
  appendValue(form, 'category', productForm.category)
  appendValue(form, 'name', productForm.name)
  appendValue(form, 'slug', productForm.slug)
  form.append('tag', productForm.tag || '')
  form.append('summary', productForm.summary || '')
  form.append('specification', productForm.specification || '')
  form.append('description', productForm.description || '')
  form.append('sort_order', Number(productForm.sort_order) || 0)
  form.append('is_featured', productForm.is_featured)
  form.append('is_active', productForm.is_active)
  if (productForm.legacy_id) form.append('legacy_id', productForm.legacy_id)
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
    const saved = await api(path, { method: productForm.id ? 'PATCH' : 'POST', body: productPayload() })
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
  const base = type === 'category' ? 'categories' : type === 'product' ? 'products' : 'product-images'
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
    <div class="page-heading"><div><p class="eyebrow">CATALOG</p><h1>产品管理</h1></div></div>
    <div class="tabs">
      <button :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">产品</button>
      <button :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'">分类</button>
    </div>
    <p v-if="error" class="message error">{{ error }}</p>
    <p v-if="message" class="message success">{{ message }}</p>

    <template v-if="activeTab === 'categories'">
      <form class="panel form-grid" @submit.prevent="saveCategory">
        <div class="panel-heading"><h2>{{ categoryForm.id ? '编辑分类' : '新增分类' }}</h2><button v-if="categoryForm.id" class="text-button" type="button" @click="replace(categoryForm, emptyCategory())">取消编辑</button></div>
        <label>名称<input v-model.trim="categoryForm.name" required /></label>
        <label>页面地址 slug<input v-model.trim="categoryForm.slug" pattern="[-a-zA-Z0-9_]+" required /></label>
        <label>上级分类<select v-model="categoryForm.parent"><option value="">一级分类</option><option v-for="item in categories.filter((item) => !item.parent && item.id !== categoryForm.id)" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
        <label>排序<input v-model.number="categoryForm.sort_order" min="0" type="number" /></label>
        <label class="wide">简介<textarea v-model="categoryForm.description" rows="3"></textarea></label>
        <label>旧站分类 ID<input v-model="categoryForm.legacy_id" min="1" type="number" /></label>
        <label class="check"><input v-model="categoryForm.is_active" type="checkbox" />启用</label>
        <div class="wide actions"><button class="primary-button" type="submit">保存分类</button></div>
      </form>
      <div class="panel"><h2>分类列表</h2><p v-if="loading">加载中…</p><div v-else class="table-wrap"><table><thead><tr><th>名称</th><th>slug</th><th>层级</th><th>状态</th><th></th></tr></thead><tbody><tr v-for="item in categoryOptions" :key="item.id"><td>{{ item.label }}</td><td>{{ item.slug }}</td><td>{{ item.parent ? '二级' : '一级' }}</td><td><span class="status" :class="{ off: !item.is_active }">{{ item.is_active ? '启用' : '停用' }}</span></td><td class="row-actions"><button class="text-button" @click="editCategory(item)">编辑</button><button class="text-button danger" @click="remove('category', item.id, item.name)">删除</button></td></tr></tbody></table></div></div>
    </template>

    <template v-else>
      <form class="panel form-grid" @submit.prevent="saveProduct">
        <div class="panel-heading"><h2>{{ productForm.id ? '编辑产品' : '新增产品' }}</h2><button v-if="productForm.id" class="text-button" type="button" @click="replace(productForm, emptyProduct())">新增另一产品</button></div>
        <label>名称<input v-model.trim="productForm.name" required /></label>
        <label>页面地址 slug<input v-model.trim="productForm.slug" pattern="[-a-zA-Z0-9_]+" required /></label>
        <label>所属分类<select v-model="productForm.category" required><option value="" disabled>请选择</option><option v-for="item in categoryOptions" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
        <label>标签<input v-model.trim="productForm.tag" /></label>
        <label>规格<input v-model.trim="productForm.specification" /></label>
        <label>排序<input v-model.number="productForm.sort_order" min="0" type="number" /></label>
        <label class="wide">摘要<textarea v-model="productForm.summary" rows="3"></textarea></label>
        <label class="wide">详情正文<textarea v-model="productForm.description" rows="8"></textarea></label>
        <label>封面图<input id="product-cover" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="productForm.cover" :href="productForm.cover" target="_blank">查看当前图片</a></label>
        <label>悬停图<input id="product-hover" accept="image/jpeg,image/png,image/webp" type="file" /><a v-if="productForm.hover_image" :href="productForm.hover_image" target="_blank">查看当前图片</a></label>
        <label>旧站产品 ID<input v-model="productForm.legacy_id" min="1" type="number" /></label>
        <label class="check"><input v-model="productForm.is_featured" type="checkbox" />首页推荐</label>
        <label class="check"><input v-model="productForm.is_active" type="checkbox" />上架公开</label>
        <div class="wide actions"><button class="primary-button" type="submit">保存产品</button></div>
      </form>
      <div v-if="productForm.id" class="panel">
        <h2>产品详情图片</h2>
        <div class="gallery-admin"><div v-for="image in productForm.images" :key="image.id"><img :src="image.image" :alt="image.alt_text" /><button class="text-button danger" @click="remove('gallery', image.id, '这张图片')">删除</button></div></div>
        <div class="inline-form"><input accept="image/jpeg,image/png,image/webp" type="file" @change="galleryFile = $event.target.files[0]" /><input v-model="galleryAlt" placeholder="图片说明（推荐填写）" /><button class="secondary-button" :disabled="!galleryFile" type="button" @click="uploadGallery">上传</button></div>
      </div>
      <div class="panel"><h2>产品列表</h2><p v-if="loading">加载中…</p><div v-else class="table-wrap"><table><thead><tr><th>产品</th><th>分类</th><th>状态</th><th>推荐</th><th></th></tr></thead><tbody><tr v-for="item in products" :key="item.id"><td>{{ item.name }}</td><td>{{ categories.find((category) => category.id === item.category)?.name }}</td><td><span class="status" :class="{ off: !item.is_active }">{{ item.is_active ? '已上架' : '已下架' }}</span></td><td>{{ item.is_featured ? '是' : '—' }}</td><td class="row-actions"><button class="text-button" @click="editProduct(item)">编辑</button><button class="text-button danger" @click="remove('product', item.id, item.name)">删除</button></td></tr></tbody></table></div></div>
    </template>
  </section>
</template>
