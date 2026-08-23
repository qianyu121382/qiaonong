<script setup>
import { onMounted, reactive, ref, watch } from 'vue'

import { api } from '../api'
import AdminIcon from '../components/AdminIcon.vue'
import AdminImageUploader from '../components/AdminImageUploader.vue'
import { showToast } from '../stores/toast'

const props = defineProps({
  mode: {
    type: String,
    required: true,
  },
})

const loading = ref(true)
const saving = ref(false)

// Carousel State
const slides = ref([])
const slideDialogOpen = ref(false)
const slideDialogTitle = ref('添加首页轮播')
const slideForm = reactive(emptySlide())
const desktopImageFile = ref(null)
const mobileImageFile = ref(null)

// Company State
const site = reactive({
  company_name: '',
  phone: '',
  email: '',
  address: '',
  footer_text: '',
  icp_number: '',
  icp_url: 'https://beian.miit.gov.cn/',
  logo: '',
  social_qr: '',
})
const logoFile = ref(null)
const qrFile = ref(null)

function emptySlide() {
  return {
    id: null,
    title: '',
    subtitle: '',
    link_url: '',
    sort_order: 0,
    is_active: true,
    image: '',
    mobile_image: '',
  }
}

function replace(target, source) {
  for (const key of Object.keys(target)) {
    target[key] = source[key] ?? ''
  }
}

async function loadData() {
  loading.value = true
  try {
    if (props.mode === 'company') {
      const data = await api('/api/admin/content/site/')
      replace(site, data || {})
    } else {
      const data = await api('/api/admin/content/slides/')
      slides.value = data || []
    }
  } catch (reason) {
    showToast(reason.message || '加载数据失败', 'error')
  } finally {
    loading.value = false
  }
}

// ---------------- Slide CRUD ----------------
function handleAddSlide() {
  replace(slideForm, emptySlide())
  desktopImageFile.value = null
  mobileImageFile.value = null
  slideDialogTitle.value = '添加首页轮播'
  slideDialogOpen.value = true
}

function handleUpdateSlide(row) {
  replace(slideForm, { ...emptySlide(), ...row })
  desktopImageFile.value = null
  mobileImageFile.value = null
  slideDialogTitle.value = '修改首页轮播'
  slideDialogOpen.value = true
}

function cancelSlideDialog() {
  slideDialogOpen.value = false
}

function buildSlidePayload() {
  const form = new FormData()
  form.append('title', slideForm.title || '')
  form.append('subtitle', slideForm.subtitle || '')
  form.append('link_url', slideForm.link_url || '')
  form.append('sort_order', Number(slideForm.sort_order) || 0)
  form.append('is_active', slideForm.is_active)

  const image = desktopImageFile.value || document.querySelector('#slide-image')?.files[0]
  if (image) form.append('image', image)

  const mobileImage = mobileImageFile.value || document.querySelector('#slide-mobile-image')?.files[0]
  if (mobileImage) form.append('mobile_image', mobileImage)

  return form
}

async function submitSlideForm() {
  if (!slideForm.id && !desktopImageFile.value && !slideForm.image) {
    showToast('请上传桌面端横幅图片', 'error')
    return
  }

  saving.value = true
  try {
    const path = slideForm.id
      ? `/api/admin/content/slides/${slideForm.id}/`
      : '/api/admin/content/slides/'
    await api(path, {
      method: slideForm.id ? 'PATCH' : 'POST',
      body: buildSlidePayload(),
    })

    showToast(slideForm.id ? '修改成功' : '新增成功', 'success')
    slideDialogOpen.value = false
    await loadData()
  } catch (reason) {
    showToast(reason.message || '操作失败', 'error')
  } finally {
    saving.value = false
  }
}

async function handleDeleteSlide(row) {
  const label = row.title || '该轮播图'
  if (!window.confirm(`是否确认删除"${label}"？`)) return
  try {
    await api(`/api/admin/content/slides/${row.id}/`, { method: 'DELETE' })
    showToast('删除成功', 'success')
    await loadData()
  } catch (reason) {
    showToast(reason.message || '删除失败', 'error')
  }
}

// ---------------- Company Settings ----------------
function buildSitePayload() {
  const form = new FormData()
  const textFields = ['company_name', 'phone', 'email', 'address', 'footer_text', 'icp_number', 'icp_url']
  textFields.forEach((key) => form.append(key, site[key] || ''))

  const logo = logoFile.value || document.querySelector('#site-logo')?.files[0]
  if (logo) form.append('logo', logo)

  const qr = qrFile.value || document.querySelector('#site-social-qr')?.files[0]
  if (qr) form.append('social_qr', qr)

  return form
}

async function handleSaveSite() {
  if (!window.confirm('确定要修改并保存公司信息吗？')) return

  saving.value = true
  try {
    const updated = await api('/api/admin/content/site/', {
      method: 'PATCH',
      body: buildSitePayload(),
    })
    replace(site, updated || {})
    logoFile.value = null
    qrFile.value = null
    showToast('公司信息保存成功', 'success')
  } catch (reason) {
    showToast(reason.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
watch(() => props.mode, loadData)
</script>

<template>
  <div class="ry-page-container">
    <!-- ================= Company Mode ================= -->
    <div v-if="mode === 'company'">
      <div class="ry-card">
        <div class="ry-card-header">
          <h3 class="ry-card-title">
            <AdminIcon name="company" :size="16" />
            <span>企业资料与网站基础配置</span>
          </h3>
          <button class="ry-btn ry-btn-primary" type="button" :disabled="saving" @click="handleSaveSite">
            <AdminIcon name="check" :size="14" />
            <span>{{ saving ? '保存中…' : '保存配置' }}</span>
          </button>
        </div>

        <div class="ry-card-body" style="max-width: 900px;">
          <form class="ry-dialog-form" @submit.prevent="handleSaveSite">
            <!-- Part 1: Company Profile -->
            <div style="font-weight: 600; font-size: 14px; color: var(--ry-text-primary); border-left: 3px solid var(--ry-primary); padding-left: 8px; margin: 4px 0 8px 0;">
              主体基本信息
            </div>

            <div class="ry-form-row">
              <div class="ry-form-field">
                <label class="ry-field-label">公司名称（运营主体）</label>
                <input
                  v-model.trim="site.company_name"
                  class="ry-input"
                  placeholder="例如：鞍山鼎禾生物制药有限公司"
                />
              </div>

              <div class="ry-form-field">
                <label class="ry-field-label">页脚补充文字</label>
                <input
                  v-model.trim="site.footer_text"
                  class="ry-input"
                  placeholder="例如：专注天然草本护肤研制"
                />
              </div>
            </div>

            <!-- Part 2: Contact Info -->
            <div style="font-weight: 600; font-size: 14px; color: var(--ry-text-primary); border-left: 3px solid var(--ry-primary); padding-left: 8px; margin: 16px 0 8px 0;">
              联系服务方式
            </div>

            <div class="ry-form-row">
              <div class="ry-form-field">
                <label class="ry-field-label">官方客服电话</label>
                <input
                  v-model.trim="site.phone"
                  class="ry-input"
                  placeholder="例如：13596956311"
                />
              </div>

              <div class="ry-form-field">
                <label class="ry-field-label">联系邮箱</label>
                <input
                  v-model.trim="site.email"
                  type="email"
                  class="ry-input"
                  placeholder="例如：service@zgqnht.com"
                />
              </div>
            </div>

            <div class="ry-form-field full">
              <label class="ry-field-label">公司办公地址</label>
              <input
                v-model.trim="site.address"
                class="ry-input"
                placeholder="公司注册或实际办公地址"
              />
            </div>

            <!-- Part 3: Brand & QR Code -->
            <div style="font-weight: 600; font-size: 14px; color: var(--ry-text-primary); border-left: 3px solid var(--ry-primary); padding-left: 8px; margin: 16px 0 8px 0;">
              品牌素材与二维码
            </div>

            <div class="ry-form-row">
              <div class="ry-form-field">
                <AdminImageUploader
                  v-model="logoFile"
                  input-id="site-logo"
                  label="网站 Logo"
                  hint="建议透明底 PNG 或 WebP 格式"
                  :current-url="site.logo"
                />
              </div>

              <div class="ry-form-field">
                <AdminImageUploader
                  v-model="qrFile"
                  input-id="site-social-qr"
                  label="客服/微信二维码"
                  hint="展示在官网页脚联系区域"
                  :current-url="site.social_qr"
                />
              </div>
            </div>

            <!-- Part 4: ICP Compliance -->
            <div style="font-weight: 600; font-size: 14px; color: var(--ry-text-primary); border-left: 3px solid var(--ry-primary); padding-left: 8px; margin: 16px 0 8px 0;">
              网站备案与合规资质
            </div>

            <div class="ry-form-row">
              <div class="ry-form-field">
                <label class="ry-field-label">工信部 ICP 备案号</label>
                <input
                  v-model.trim="site.icp_number"
                  class="ry-input"
                  placeholder="例如：辽ICP备2026018730号-1"
                />
              </div>

              <div class="ry-form-field">
                <label class="ry-field-label">工信部系统链接</label>
                <input
                  v-model.trim="site.icp_url"
                  type="url"
                  class="ry-input"
                  placeholder="https://beian.miit.gov.cn/"
                />
              </div>
            </div>

            <div style="margin-top: 10px;">
              <button class="ry-btn ry-btn-primary" type="submit" :disabled="saving">
                <AdminIcon name="check" :size="14" />
                <span>{{ saving ? '正在保存…' : '保 存 配 置' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ================= Carousel Mode ================= -->
    <div v-else>
      <div class="ry-table-card">
        <!-- Toolbar -->
        <div class="ry-toolbar-row">
          <div class="ry-toolbar-left">
            <button class="ry-btn ry-btn-primary-plain" type="button" @click="handleAddSlide">
              <AdminIcon name="plus" :size="13" />
              <span>新增轮播</span>
            </button>
            <button class="ry-btn ry-btn-success-plain" type="button" @click="loadData">
              <AdminIcon name="refresh" :size="13" />
              <span>刷新</span>
            </button>
          </div>

          <div class="ry-toolbar-right">
            <button class="ry-tool-btn" type="button" title="刷新表格" @click="loadData">
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
                <th style="width: 140px; text-align: center;">预览图</th>
                <th>轮播标题</th>
                <th>副标题</th>
                <th>跳转链接</th>
                <th style="width: 110px; text-align: center;">手机端适配</th>
                <th style="width: 70px; text-align: center;">排序</th>
                <th style="width: 80px; text-align: center;">状态</th>
                <th style="width: 140px; text-align: center;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="9" style="text-align: center; padding: 30px; color: var(--ry-text-secondary);">
                  正在加载轮播图数据…
                </td>
              </tr>
              <tr v-else-if="slides.length === 0">
                <td colspan="9" style="text-align: center; padding: 30px; color: var(--ry-text-secondary);">
                  暂无轮播图数据
                </td>
              </tr>
              <tr v-else v-for="(item, index) in slides" :key="item.id">
                <td style="text-align: center;">{{ index + 1 }}</td>
                <td style="text-align: center;">
                  <img
                    :src="item.image"
                    :alt="item.title || '轮播图'"
                    style="width: 120px; height: 45px; object-fit: cover; border-radius: 3px; border: 1px solid var(--ry-border-light); margin: 0 auto; display: block;"
                  />
                </td>
                <td>
                  <strong style="color: var(--ry-text-primary);">{{ item.title || '（未填写标题）' }}</strong>
                </td>
                <td>{{ item.subtitle || '—' }}</td>
                <td>
                  <span v-if="item.link_url" style="color: var(--ry-primary); font-family: monospace;">{{ item.link_url }}</span>
                  <span v-else style="color: #c0c4cc;">无跳转</span>
                </td>
                <td style="text-align: center;">
                  <span v-if="item.mobile_image" class="ry-tag ry-tag-primary">专属手机图</span>
                  <span v-else class="ry-tag ry-tag-info">桌面图兜底</span>
                </td>
                <td style="text-align: center;">{{ item.sort_order }}</td>
                <td style="text-align: center;">
                  <span v-if="item.is_active" class="ry-tag ry-tag-success">启用</span>
                  <span v-else class="ry-tag ry-tag-info">停用</span>
                </td>
                <td style="text-align: center;">
                  <div style="display: flex; justify-content: center; gap: 8px;">
                    <button class="ry-link-btn" type="button" @click="handleUpdateSlide(item)">
                      <AdminIcon name="edit" :size="13" />
                      <span>修改</span>
                    </button>
                    <button class="ry-link-btn danger" type="button" @click="handleDeleteSlide(item)">
                      <AdminIcon name="trash" :size="13" />
                      <span>删除</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Slide Create/Edit Dialog -->
      <div v-if="slideDialogOpen" class="ry-dialog-backdrop" @click.self="cancelSlideDialog">
        <div class="ry-dialog">
          <div class="ry-dialog-header">
            <h3 class="ry-dialog-title">{{ slideDialogTitle }}</h3>
            <button class="ry-dialog-close" type="button" @click="cancelSlideDialog">✕</button>
          </div>

          <form class="ry-dialog-body ry-dialog-form" @submit.prevent="submitSlideForm">
            <div class="ry-form-row">
              <div class="ry-form-field">
                <label class="ry-field-label">轮播主标题（可选）</label>
                <input
                  v-model.trim="slideForm.title"
                  class="ry-input"
                  placeholder="例如：科技护肤 焕颜新生"
                />
              </div>

              <div class="ry-form-field">
                <label class="ry-field-label">轮播副标题（可选）</label>
                <input
                  v-model.trim="slideForm.subtitle"
                  class="ry-input"
                  placeholder="例如：巧侬花田自然精粹系列"
                />
              </div>
            </div>

            <div class="ry-form-row">
              <div class="ry-form-field">
                <label class="ry-field-label">点击跳转链接</label>
                <input
                  v-model.trim="slideForm.link_url"
                  class="ry-input"
                  placeholder="例如 /products 或 https://..."
                />
              </div>

              <div class="ry-form-field">
                <label class="ry-field-label">排序权重</label>
                <input
                  v-model.number="slideForm.sort_order"
                  type="number"
                  min="0"
                  class="ry-input"
                  placeholder="数字越小越靠前"
                />
              </div>
            </div>

            <div class="ry-form-field full">
              <label class="ry-field-label">状态</label>
              <div class="ry-radio-group">
                <label class="ry-radio-label">
                  <input v-model="slideForm.is_active" type="checkbox" />
                  <span>启用该轮播横幅</span>
                </label>
              </div>
            </div>

            <!-- Uploaders -->
            <div class="ry-form-row">
              <div class="ry-form-field">
                <AdminImageUploader
                  v-model="desktopImageFile"
                  input-id="slide-image"
                  label="电脑桌面端横幅图"
                  hint="建议 1575×590 像素（2.67:1），宽幅高清"
                  aspect-ratio="1575 / 590"
                  :required="!slideForm.id"
                  :current-url="slideForm.image"
                />
              </div>

              <div class="ry-form-field">
                <AdminImageUploader
                  v-model="mobileImageFile"
                  input-id="slide-mobile-image"
                  label="手机端横幅图（可选）"
                  hint="建议 8:5 比例。未上传时使用桌面图兜底"
                  aspect-ratio="8 / 5"
                  :current-url="slideForm.mobile_image"
                />
              </div>
            </div>
          </form>

          <div class="ry-dialog-footer">
            <button class="ry-btn ry-btn-default" type="button" @click="cancelSlideDialog">取 消</button>
            <button class="ry-btn ry-btn-primary" type="button" :disabled="saving" @click="submitSlideForm">
              {{ saving ? '保存中…' : '确 定' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
