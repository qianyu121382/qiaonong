<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { api, appendValue } from '../api'
import AdminIcon from '../components/AdminIcon.vue'
import AdminImageUploader from '../components/AdminImageUploader.vue'
import { showToast } from '../stores/toast'

const categories = ref([])
const products = ref([])
const loading = ref(true)
const saving = ref(false)
const showSearch = ref(true)
const uploadingGallery = ref(false)

// Query Form State (RuoYi standard inline query)
const queryParams = reactive({
  name: '',
  category: '',
  isActive: '', // '' | 'true' | 'false'
  isFeatured: '', // '' | 'true' | 'false'
})

// Pagination State (RuoYi standard pagination)
const pageNum = ref(1)
const pageSize = ref(10)

// Dialog State (RuoYi standard dialog)
const dialogOpen = ref(false)
const dialogTitle = ref('添加产品')
const productForm = reactive(emptyProduct())

// Local File Uploads for Dialog
const coverFile = ref(null)
const hoverFile = ref(null)
const galleryFile = ref(null)
const galleryAlt = ref('')
const galleryFileInputRef = ref(null)

function triggerGallerySelect() {
  galleryFileInputRef.value?.click()
}

const categoryOptions = computed(() => {
  const roots = categories.value
    .filter((cat) => !cat.parent)
    .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)

  return roots.flatMap((root) => {
    const children = categories.value
      .filter((cat) => cat.parent === root.id)
      .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
      .map((child) => ({
        ...child,
        label: `　└ ${child.name}（所属：${root.name}）`,
        effectiveActive: child.is_active && root.is_active,
      }))

    return [
      {
        ...root,
        label: `[一级] ${root.name}`,
        effectiveActive: root.is_active,
      },
      ...children,
    ]
  })
})

function getCategoryName(categoryId) {
  const c = categories.value.find((item) => item.id === categoryId)
  return c ? c.name : '未分类'
}

function emptyProduct() {
  return {
    id: null,
    category: '',
    name: '',
    tag: '',
    summary: '',
    specification: '',
    description: '',
    sort_order: 0,
    is_featured: false,
    is_active: true,
    cover: '',
    hover_image: '',
    images: [],
  }
}

function replace(target, source) {
  Object.keys(target).forEach((key) => {
    target[key] = source[key] ?? emptyValue(target[key])
  })
}

function emptyValue(value) {
  if (typeof value === 'boolean') return false
  if (typeof value === 'number') return 0
  if (Array.isArray(value)) return []
  return ''
}

async function loadData() {
  loading.value = true
  try {
    const [catList, prodList] = await Promise.all([
      api('/api/admin/catalog/categories/'),
      api('/api/admin/catalog/products/'),
    ])
    categories.value = catList || []
    products.value = prodList || []
  } catch (err) {
    showToast(err.message || '加载产品列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// Client-side Query Filtering
const filteredProducts = computed(() => {
  return products.value.filter((item) => {
    // Name keyword
    if (queryParams.name) {
      const q = queryParams.name.toLowerCase()
      const matchName = item.name?.toLowerCase().includes(q)
      const matchTag = item.tag?.toLowerCase().includes(q)
      const matchSpec = item.specification?.toLowerCase().includes(q)
      if (!matchName && !matchTag && !matchSpec) return false
    }
    // Category
    if (queryParams.category) {
      const selected = categories.value.find((cat) => cat.id === queryParams.category)
      const matchingIds = selected && !selected.parent
        ? new Set([selected.id, ...categories.value.filter((cat) => cat.parent === selected.id).map((cat) => cat.id)])
        : new Set([queryParams.category])
      if (!matchingIds.has(item.category)) return false
    }
    // Is Active
    if (queryParams.isActive === 'true' && !item.is_active) return false
    if (queryParams.isActive === 'false' && item.is_active) return false

    // Is Featured
    if (queryParams.isFeatured === 'true' && !item.is_featured) return false
    if (queryParams.isFeatured === 'false' && item.is_featured) return false

    return true
  })
})

const total = computed(() => filteredProducts.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

const paginatedList = computed(() => {
  const start = (pageNum.value - 1) * pageSize.value
  return filteredProducts.value.slice(start, start + pageSize.value)
})

function handleQuery() {
  pageNum.value = 1
}

function resetQuery() {
  queryParams.name = ''
  queryParams.category = ''
  queryParams.isActive = ''
  queryParams.isFeatured = ''
  pageNum.value = 1
}

// Dialog Handlers
function handleAdd() {
  replace(productForm, emptyProduct())
  const defaultCategory = categoryOptions.value.find((cat) => cat.parent && cat.effectiveActive)
    || categoryOptions.value.find((cat) => cat.effectiveActive)
  if (defaultCategory) {
    productForm.category = defaultCategory.id
  }
  coverFile.value = null
  hoverFile.value = null
  galleryFile.value = null
  galleryAlt.value = ''
  dialogTitle.value = '添加产品'
  dialogOpen.value = true
}

function handleUpdate(row) {
  replace(productForm, { ...emptyProduct(), ...row })
  coverFile.value = null
  hoverFile.value = null
  galleryFile.value = null
  galleryAlt.value = ''
  dialogTitle.value = '修改产品'
  dialogOpen.value = true
}

function cancelDialog() {
  dialogOpen.value = false
}

function buildProductPayload() {
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

  const cover = coverFile.value || document.querySelector('#product-cover')?.files[0]
  const hover = hoverFile.value || document.querySelector('#product-hover')?.files[0]
  if (cover) form.append('cover', cover)
  if (hover) form.append('hover_image', hover)
  return form
}

async function submitForm() {
  if (!productForm.name) {
    showToast('产品名称不能为空', 'error')
    return
  }
  if (!productForm.category) {
    showToast('请选择所属分类', 'error')
    return
  }

  saving.value = true
  try {
    const path = productForm.id
      ? `/api/admin/catalog/products/${productForm.id}/`
      : '/api/admin/catalog/products/'
    const saved = await api(path, {
      method: productForm.id ? 'PATCH' : 'POST',
      body: buildProductPayload(),
    })

    showToast(productForm.id ? '修改成功' : '新增成功', 'success')
    replace(productForm, { ...emptyProduct(), ...saved })
    dialogOpen.value = false
    await loadData()
  } catch (err) {
    showToast(err.message || '操作失败', 'error')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  if (!window.confirm(`是否确认删除产品名称为"${row.name}"的数据项？`)) return
  try {
    await api(`/api/admin/catalog/products/${row.id}/`, { method: 'DELETE' })
    showToast('删除成功', 'success')
    await loadData()
  } catch (err) {
    showToast(err.message || '删除失败', 'error')
  }
}

async function uploadGallery() {
  if (!productForm.id || !galleryFile.value) return
  uploadingGallery.value = true
  try {
    const form = new FormData()
    form.append('product', productForm.id)
    form.append('image', galleryFile.value)
    form.append('alt_text', galleryAlt.value || '')
    form.append('sort_order', productForm.images.length)

    await api('/api/admin/catalog/product-images/', { method: 'POST', body: form })
    galleryFile.value = null
    galleryAlt.value = ''
    showToast('详情图片上传成功', 'success')

    const updated = await api(`/api/admin/catalog/products/${productForm.id}/`)
    replace(productForm, { ...emptyProduct(), ...updated })
    await loadData()
  } catch (err) {
    showToast(err.message || '上传失败', 'error')
  } finally {
    uploadingGallery.value = false
  }
}

async function removeGalleryImage(imageId) {
  if (!window.confirm('确定删除该详情图片？')) return
  try {
    await api(`/api/admin/catalog/product-images/${imageId}/`, { method: 'DELETE' })
    showToast('删除成功', 'success')
    const updated = await api(`/api/admin/catalog/products/${productForm.id}/`)
    replace(productForm, { ...emptyProduct(), ...updated })
    await loadData()
  } catch (err) {
    showToast(err.message || '删除失败', 'error')
  }
}

onMounted(loadData)
</script>

<template>
  <div class="ry-page-container">
    <!-- RuoYi Standard Search Form -->
    <div v-show="showSearch" class="ry-query-card">
      <form class="ry-form-inline" @submit.prevent="handleQuery">
        <div class="ry-form-item">
          <span class="ry-form-label">产品名称：</span>
          <input
            v-model.trim="queryParams.name"
            class="ry-input"
            style="width: 200px;"
            placeholder="请输入产品名称"
          />
        </div>

        <div class="ry-form-item">
          <span class="ry-form-label">所属分类：</span>
          <select
            v-model="queryParams.category"
            class="ry-select"
            style="width: 160px;"
          >
            <option value="">全部</option>
            <option v-for="cat in categoryOptions" :key="cat.id" :value="cat.id">
              {{ cat.label }}{{ cat.effectiveActive ? '' : '（当前隐藏）' }}
            </option>
          </select>
        </div>

        <div class="ry-form-item">
          <span class="ry-form-label">上架状态：</span>
          <select
            v-model="queryParams.isActive"
            class="ry-select"
            style="width: 120px;"
          >
            <option value="">全部</option>
            <option value="true">已上架</option>
            <option value="false">已下架</option>
          </select>
        </div>

        <div class="ry-form-item">
          <span class="ry-form-label">首页推荐：</span>
          <select
            v-model="queryParams.isFeatured"
            class="ry-select"
            style="width: 120px;"
          >
            <option value="">全部</option>
            <option value="true">推荐</option>
            <option value="false">不推荐</option>
          </select>
        </div>

        <div class="ry-form-item" style="margin-left: auto;">
          <button class="ry-btn ry-btn-primary" type="submit">
            <AdminIcon name="search" :size="13" />
            <span>搜索</span>
          </button>
          <button class="ry-btn ry-btn-default" type="button" @click="resetQuery">
            <AdminIcon name="refresh" :size="13" />
            <span>重置</span>
          </button>
        </div>
      </form>
    </div>

    <!-- RuoYi Standard Table & Toolbar Card -->
    <div class="ry-table-card">
      <!-- Toolbar -->
      <div class="ry-toolbar-row">
        <div class="ry-toolbar-left">
          <button class="ry-btn ry-btn-primary-plain" type="button" @click="handleAdd">
            <AdminIcon name="plus" :size="13" />
            <span>新增</span>
          </button>
          <button class="ry-btn ry-btn-success-plain" type="button" @click="loadData">
            <AdminIcon name="refresh" :size="13" />
            <span>刷新</span>
          </button>
        </div>

        <div class="ry-toolbar-right">
          <button
            class="ry-tool-btn"
            type="button"
            :title="showSearch ? '隐藏搜索' : '显示搜索'"
            @click="showSearch = !showSearch"
          >
            <AdminIcon name="search" :size="14" />
          </button>
          <button
            class="ry-tool-btn"
            type="button"
            title="刷新表格"
            @click="loadData"
          >
            <AdminIcon name="refresh" :size="14" />
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="ry-table-wrap">
        <table class="ry-table">
          <thead>
            <tr>
              <th style="width: 60px; text-align: center;">序号</th>
              <th style="width: 70px; text-align: center;">封面图</th>
              <th style="min-width: 180px;">产品名称</th>
              <th style="width: 130px;">所属分类</th>
              <th style="width: 100px;">包装规格</th>
              <th style="width: 70px; text-align: center;">排序</th>
              <th style="width: 90px; text-align: center;">首页推荐</th>
              <th style="width: 90px; text-align: center;">状态</th>
              <th style="width: 140px; text-align: center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="9" style="text-align: center; padding: 30px; color: var(--ry-text-secondary);">
                正在加载产品数据…
              </td>
            </tr>
            <tr v-else-if="paginatedList.length === 0">
              <td colspan="9" style="text-align: center; padding: 30px; color: var(--ry-text-secondary);">
                暂无产品数据
              </td>
            </tr>
            <tr v-else v-for="(item, index) in paginatedList" :key="item.id">
              <td style="text-align: center;">
                {{ (pageNum - 1) * pageSize + index + 1 }}
              </td>
              <td style="text-align: center;">
                <img
                  v-if="item.cover"
                  :src="item.cover"
                  :alt="item.name"
                  class="ry-product-thumb"
                  style="margin: 0 auto;"
                />
                <span v-else style="color: #c0c4cc; font-size: 12px;">无</span>
              </td>
              <td>
                <div style="display: flex; align-items: center; gap: 6px;">
                  <strong style="color: var(--ry-text-primary);">{{ item.name }}</strong>
                  <span v-if="item.tag" class="ry-tag ry-tag-warning" style="height: 20px; line-height: 18px; font-size: 11px;">
                    {{ item.tag }}
                  </span>
                </div>
              </td>
              <td>
                <span class="ry-tag ry-tag-info">
                  {{ getCategoryName(item.category) }}
                </span>
              </td>
              <td>{{ item.specification || '—' }}</td>
              <td style="text-align: center;">{{ item.sort_order }}</td>
              <td style="text-align: center;">
                <span v-if="item.is_featured" class="ry-tag ry-tag-warning">推荐</span>
                <span v-else class="ry-tag ry-tag-info">否</span>
              </td>
              <td style="text-align: center;">
                <span v-if="item.is_active" class="ry-tag ry-tag-success">已上架</span>
                <span v-else class="ry-tag ry-tag-danger">已下架</span>
              </td>
              <td style="text-align: center;">
                <div style="display: flex; justify-content: center; gap: 8px;">
                  <button class="ry-link-btn" type="button" @click="handleUpdate(item)">
                    <AdminIcon name="edit" :size="13" />
                    <span>修改</span>
                  </button>
                  <button class="ry-link-btn danger" type="button" @click="handleDelete(item)">
                    <AdminIcon name="trash" :size="13" />
                    <span>删除</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- RuoYi Standard Pagination Bar -->
      <div class="ry-pagination-container">
        <span>共 {{ total }} 条</span>
        <select v-model="pageSize" class="ry-select" style="height: 28px; width: 95px; font-size: 12px;" @change="pageNum = 1">
          <option :value="10">10条/页</option>
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
        </select>

        <div style="display: flex; align-items: center; gap: 4px;">
          <button
            class="ry-page-btn"
            type="button"
            :disabled="pageNum <= 1"
            @click="pageNum--"
          >
            &lt;
          </button>
          <button
            v-for="p in totalPages"
            :key="p"
            class="ry-page-btn"
            :class="{ 'ry-page-current': p === pageNum }"
            type="button"
            @click="pageNum = p"
          >
            {{ p }}
          </button>
          <button
            class="ry-page-btn"
            type="button"
            :disabled="pageNum >= totalPages"
            @click="pageNum++"
          >
            &gt;
          </button>
        </div>
      </div>
    </div>

    <!-- RuoYi Standard Add / Edit Dialog -->
    <div v-if="dialogOpen" class="ry-dialog-backdrop" @click.self="cancelDialog">
      <div class="ry-dialog">
        <div class="ry-dialog-header">
          <h3 class="ry-dialog-title">{{ dialogTitle }}</h3>
          <button class="ry-dialog-close" type="button" @click="cancelDialog">✕</button>
        </div>

        <form class="ry-dialog-body ry-dialog-form" @submit.prevent="submitForm">
          <!-- Row 1 -->
          <div class="ry-form-row">
            <div class="ry-form-field">
              <label class="ry-field-label">
                <span class="required">*</span>产品名称
              </label>
              <input
                v-model.trim="productForm.name"
                class="ry-input"
                placeholder="请输入产品名称"
                required
              />
            </div>

            <div class="ry-form-field">
              <label class="ry-field-label">
                <span class="required">*</span>所属分类
              </label>
              <select v-model="productForm.category" class="ry-select" required>
                <option value="" disabled>请选择所属分类</option>
                <option
                  v-for="cat in categoryOptions"
                  :key="cat.id"
                  :value="cat.id"
                  :disabled="!cat.effectiveActive && cat.id !== productForm.category"
                >
                  {{ cat.label }}{{ cat.effectiveActive ? '' : '（当前隐藏）' }}
                </option>
              </select>
            </div>
          </div>

          <!-- Row 2 -->
          <div class="ry-form-row">
            <div class="ry-form-field">
              <label class="ry-field-label">排序权重</label>
              <input
                v-model.number="productForm.sort_order"
                type="number"
                min="0"
                class="ry-input"
                placeholder="数字越大越靠前"
              />
            </div>

            <div class="ry-form-field">
              <label class="ry-field-label">包装规格</label>
              <input
                v-model.trim="productForm.specification"
                class="ry-input"
                placeholder="例如：50g / 100ml"
              />
            </div>
          </div>

          <!-- Row 3 -->
          <div class="ry-form-row">
            <div class="ry-form-field">
              <label class="ry-field-label">亮点标签</label>
              <input
                v-model.trim="productForm.tag"
                class="ry-input"
                placeholder="例如：热销爆款、院线专研"
              />
            </div>

            <div class="ry-form-field">
              <label class="ry-field-label">状态设置</label>
              <div class="ry-radio-group">
                <label class="ry-radio-label">
                  <input v-model="productForm.is_active" type="checkbox" />
                  <span>已上架</span>
                </label>
                <label class="ry-radio-label">
                  <input v-model="productForm.is_featured" type="checkbox" />
                  <span>首页推荐</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Images -->
          <div class="ry-form-row">
            <div class="ry-form-field">
              <AdminImageUploader
                v-model="coverFile"
                input-id="product-cover"
                label="产品封面图"
                hint="支持 JPG、PNG、WebP 格式"
                :current-url="productForm.cover"
              />
            </div>

            <div class="ry-form-field">
              <AdminImageUploader
                v-model="hoverFile"
                input-id="product-hover"
                label="悬停过渡图（可选）"
                hint="鼠标滑过卡片时过渡展示"
                :current-url="productForm.hover_image"
              />
            </div>
          </div>

          <!-- Description Fields -->
          <div class="ry-form-field full">
            <label class="ry-field-label">产品摘要简介</label>
            <textarea
              v-model="productForm.summary"
              class="ry-textarea"
              rows="2"
              placeholder="简要概括产品卖点"
            ></textarea>
          </div>

          <div class="ry-form-field full">
            <label class="ry-field-label">产品详情正文</label>
            <textarea
              v-model="productForm.description"
              class="ry-textarea"
              rows="6"
              placeholder="填写产品核心成分、功效特点、使用方法等详细内容"
            ></textarea>
          </div>

          <!-- Gallery Photos (If productForm.id exists) -->
          <div v-if="productForm.id" class="ry-form-field full">
            <label class="ry-field-label">详情相册 ({{ productForm.images?.length || 0 }})</label>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
              <div
                v-for="img in productForm.images"
                :key="img.id"
                style="position: relative; width: 80px; height: 80px; border-radius: 4px; overflow: hidden; border: 1px solid #dcdfe6;"
              >
                <img :src="img.image" :alt="img.alt_text" style="width: 100%; height: 100%; object-fit: cover;" />
                <button
                  type="button"
                  style="position: absolute; top: 2px; right: 2px; background: rgba(245, 108, 108, 0.9); color: #fff; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 11px; cursor: pointer;"
                  @click="removeGalleryImage(img.id)"
                >
                  ✕
                </button>
              </div>
            </div>

            <!-- Upload input -->
            <input
              ref="galleryFileInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              style="display: none;"
              @change="galleryFile = $event.target.files[0]"
            />
            <div style="display: flex; gap: 10px; align-items: center; background: #fafafa; padding: 10px 12px; border-radius: 4px; border: 1px dashed #dcdfe6; flex-wrap: wrap;">
              <button
                class="ry-btn ry-btn-primary-plain ry-btn-sm"
                type="button"
                @click="triggerGallerySelect"
              >
                <AdminIcon name="upload" :size="13" />
                <span>{{ galleryFile ? '更换文件' : '选择图片文件' }}</span>
              </button>
              <span v-if="galleryFile" class="ry-tag ry-tag-success" style="font-size: 12px;">
                {{ galleryFile.name }}
              </span>
              <span v-else style="font-size: 12px; color: var(--ry-text-secondary);">
                未选择任何文件
              </span>

              <input
                v-model.trim="galleryAlt"
                class="ry-input"
                style="flex: 1; min-width: 160px; height: 28px;"
                placeholder="图片描述（例如：成分特写、包装展示）"
              />

              <button
                class="ry-btn ry-btn-primary ry-btn-sm"
                type="button"
                :disabled="!galleryFile || uploadingGallery"
                @click="uploadGallery"
              >
                <AdminIcon name="plus" :size="13" />
                <span>{{ uploadingGallery ? '上传中…' : '上传至相册' }}</span>
              </button>
            </div>
          </div>
        </form>

        <div class="ry-dialog-footer">
          <button class="ry-btn ry-btn-default" type="button" @click="cancelDialog">取 消</button>
          <button class="ry-btn ry-btn-primary" type="button" :disabled="saving" @click="submitForm">
            {{ saving ? '保存中…' : '确 定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
