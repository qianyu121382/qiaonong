<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { api } from '../api'
import AdminIcon from '../components/AdminIcon.vue'
import AdminImageUploader from '../components/AdminImageUploader.vue'
import { showToast } from '../stores/toast'

// 1. 数据状态
const categories = ref([])
const loading = ref(true)
const saving = ref(false)

// 视图模式：'tree'（树形折叠表格） | 'card'（系列分组卡片）
const viewMode = ref('tree')
const showSearch = ref(true)

// 搜索/筛选参数
const queryParams = reactive({
  keyword: '',
  level: '',
  isActive: '',
})

// 折叠展开映射：{ [categoryId]: boolean } (true 为折叠收起，默认 false 展开)
const collapsedMap = reactive({})

// 弹窗与表单状态
const dialogOpen = ref(false)
const dialogTitle = ref('新增产品分类')
const formLevel = ref(1) // 1: 一级分类, 2: 二级分类
const bannerFile = ref(null)
const categoryForm = reactive(emptyCategory())

// 大图预览 Lightbox
const previewImageUrl = ref('')
const previewImageTitle = ref('')

function emptyCategory() {
  return {
    id: null,
    name: '',
    slug: '',
    parent: '',
    description: '',
    banner: '',
    sort_order: 0,
    is_active: true,
  }
}

function replaceForm(source) {
  Object.assign(categoryForm, emptyCategory(), source)
  categoryForm.parent = source?.parent ?? ''
  formLevel.value = categoryForm.parent ? 2 : 1
}

// 2. 树形数据构建
const rootCategories = computed(() =>
  categories.value
    .filter((item) => !item.parent)
    .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
)

const categoryTree = computed(() => {
  return rootCategories.value.map((root) => {
    const children = categories.value
      .filter((item) => item.parent === root.id)
      .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
      .map((child) => ({
        ...child,
        level: 2,
        parentName: root.name,
      }))

    return {
      ...root,
      level: 1,
      children,
      childCount: children.length,
      activeChildCount: children.filter((c) => c.is_active).length,
    }
  })
})

// 筛选后的树形数据
const filteredTree = computed(() => {
  const kw = queryParams.keyword.trim().toLowerCase()
  const lvl = queryParams.level
  const act = queryParams.isActive

  return categoryTree.value
    .map((root) => {
      // 检查一级分类自身是否匹配
      const rootNameMatch = !kw || root.name.toLowerCase().includes(kw) || (root.slug && root.slug.toLowerCase().includes(kw))
      const rootLevelMatch = !lvl || lvl === '1'
      const rootActiveMatch = !act || (act === 'true' && root.is_active) || (act === 'false' && !root.is_active)
      const rootSelfMatch = rootNameMatch && rootLevelMatch && rootActiveMatch

      // 筛选二级分类
      const matchingChildren = root.children.filter((child) => {
        const childNameMatch = !kw || child.name.toLowerCase().includes(kw) || (child.slug && child.slug.toLowerCase().includes(kw))
        const childLevelMatch = !lvl || lvl === '2'
        const childActiveMatch = !act || (act === 'true' && child.is_active) || (act === 'false' && !child.is_active)
        return childNameMatch && childLevelMatch && childActiveMatch
      })

      // 如果用户明确筛选“仅看二级”，且有匹配子类，则只展示子类
      if (lvl === '2') {
        if (matchingChildren.length > 0) {
          return {
            ...root,
            isGhostRoot: true,
            filteredChildren: matchingChildren,
          }
        }
        return null
      }

      // 如果用户明确筛选“仅看一级”
      if (lvl === '1') {
        return rootSelfMatch ? { ...root, filteredChildren: [] } : null
      }

      // 常规搜索：自身匹配或者子项有匹配
      if (rootSelfMatch || matchingChildren.length > 0) {
        return {
          ...root,
          isGhostRoot: !rootSelfMatch,
          filteredChildren: (kw || act) ? matchingChildren : root.children,
        }
      }

      return null
    })
    .filter(Boolean)
})

// 扁平统计筛选后的数量
const totalFilteredCount = computed(() => {
  let count = 0
  for (const root of filteredTree.value) {
    if (!root.isGhostRoot && queryParams.level !== '2') count++
    count += root.filteredChildren?.length || 0
  }
  return count
})

// 上级分类下拉选项（排除自身）
const parentOptions = computed(() =>
  rootCategories.value.filter((item) => item.id !== categoryForm.id)
)

// 编辑中的分类是否包含下级分类（如果有下级分类，禁止变更为二级分类）
const editingHasChildren = computed(() =>
  Boolean(categoryForm.id && categories.value.some((item) => item.parent === categoryForm.id))
)

const selectedParent = computed(() =>
  categories.value.find((item) => item.id === categoryForm.parent) || null
)

function parentIsInactive(item) {
  if (!item.parent) return false
  const parent = categories.value.find((category) => category.id === item.parent)
  return Boolean(parent && !parent.is_active)
}

// 是否全部折叠
const isAllCollapsed = computed(() => {
  if (rootCategories.value.length === 0) return false
  return rootCategories.value.every((root) => collapsedMap[root.id] === true)
})

// 3. API 数据交互
async function loadData() {
  loading.value = true
  try {
    categories.value = (await api('/api/admin/catalog/categories/')) || []
  } catch (error) {
    showToast(error.message || '加载分类失败', 'error')
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  queryParams.keyword = ''
  queryParams.level = ''
  queryParams.isActive = ''
}

// 折叠展开控制
function toggleCollapse(rootId) {
  collapsedMap[rootId] = !collapsedMap[rootId]
}

function toggleAllCollapse() {
  const targetState = !isAllCollapsed.value
  rootCategories.value.forEach((root) => {
    collapsedMap[root.id] = targetState
  })
}

// 4. 新增/修改/删除对话框控制
function handleAddRoot() {
  replaceForm(emptyCategory())
  formLevel.value = 1
  categoryForm.parent = ''
  bannerFile.value = null
  dialogTitle.value = '新增一级分类（系列）'
  dialogOpen.value = true
}

function handleAddChild(parentCategory) {
  replaceForm(emptyCategory())
  formLevel.value = 2
  categoryForm.parent = parentCategory.id
  bannerFile.value = null
  dialogTitle.value = '添加【' + parentCategory.name + '】的二级分类'
  dialogOpen.value = true
}

function handleUpdate(item) {
  replaceForm(item)
  bannerFile.value = null
  dialogTitle.value = item.parent
    ? ('修改二级分类 - ' + item.name)
    : ('修改一级分类 - ' + item.name)
  dialogOpen.value = true
}

function cancelDialog() {
  dialogOpen.value = false
  bannerFile.value = null
}

function buildPayload() {
  const form = new FormData()
  form.append('name', categoryForm.name.trim())
  form.append('parent', formLevel.value === 1 ? '' : (categoryForm.parent || ''))
  form.append('description', categoryForm.description ? categoryForm.description.trim() : '')
  form.append('sort_order', Number(categoryForm.sort_order) || 0)
  form.append('is_active', categoryForm.is_active)
  if (formLevel.value === 1 && bannerFile.value) {
    form.append('banner', bannerFile.value)
  }
  return form
}

async function submitForm() {
  if (!categoryForm.name.trim()) {
    showToast('请输入分类名称', 'error')
    return
  }
  if (formLevel.value === 2 && !categoryForm.parent) {
    showToast('二级分类必须选择所属的一级分类', 'error')
    return
  }

  saving.value = true
  try {
    const path = categoryForm.id
      ? ('/api/admin/catalog/categories/' + categoryForm.id + '/')
      : '/api/admin/catalog/categories/'
    await api(path, {
      method: categoryForm.id ? 'PATCH' : 'POST',
      body: buildPayload(),
    })
    showToast(
      categoryForm.id
        ? '分类修改成功，前台官网导航将自动同步'
        : '分类新增成功，前台官网导航将自动同步',
      'success'
    )
    cancelDialog()
    await loadData()
  } catch (error) {
    showToast(error.message || '保存分类失败', 'error')
  } finally {
    saving.value = false
  }
}

// 快速切换启用/停用状态
async function handleQuickToggleActive(item) {
  const nextActive = !item.is_active
  const actionText = nextActive ? '启用' : '停用'
  try {
    await api('/api/admin/catalog/categories/' + item.id + '/', {
      method: 'PATCH',
      body: { is_active: nextActive },
    })
    item.is_active = nextActive
    const inheritedHidden = nextActive && parentIsInactive(item)
    showToast(
      inheritedHidden
        ? '已启用分类“' + item.name + '”，但所属一级分类已停用，前台仍会隐藏'
        : '已' + actionText + '分类“' + item.name + '”，前台将同步联动',
      'success'
    )
  } catch (error) {
    showToast(error.message || (actionText + '分类失败'), 'error')
  }
}

async function handleDelete(item) {
  const isParent = !item.parent
  const tip = isParent
    ? ('确定删除一级分类“' + item.name + '”吗？\n如果该分类下存在二级分类或已关联产品，系统会拒绝删除。')
    : ('确定删除二级分类“' + item.name + '”吗？\n如果该分类已关联产品，系统会拒绝删除。')

  if (!window.confirm(tip)) return

  try {
    await api('/api/admin/catalog/categories/' + item.id + '/', { method: 'DELETE' })
    showToast('分类“' + item.name + '”已成功删除', 'success')
    await loadData()
  } catch (error) {
    showToast(error.message || '删除分类失败', 'error')
  }
}

// 大图预览
function openPreview(url, title) {
  if (!url) return
  previewImageUrl.value = url
  previewImageTitle.value = title || '分类栏目图预览'
}

function closePreview() {
  previewImageUrl.value = ''
  previewImageTitle.value = ''
}

// 监听表单层级切换
watch(formLevel, (lvl) => {
  if (lvl === 1) {
    categoryForm.parent = ''
  } else if (!categoryForm.parent && parentOptions.value.length > 0) {
    categoryForm.parent = parentOptions.value[0].id
  }
})

onMounted(loadData)
</script>

<template>
  <div class="ry-page-container category-page">
    <!-- 顶部业务说明提示条 -->
    <div class="category-notice-bar">
      <div class="notice-left">
        <div class="notice-icon-box">
          <AdminIcon name="info" :size="16" />
        </div>
        <div class="notice-text">
          <strong>产品分类联动说明：</strong>
          一级与二级分类将实时联动前台官网顶部导航、下拉菜单、首页系列与产品列表；停用后相关分类及产品将从官网前台自动隐藏。
        </div>
      </div>
      <div class="notice-actions">
        <a href="/" target="_blank" class="notice-link">
          <AdminIcon name="external" :size="13" />
          <span>查看官网前台效果</span>
        </a>
      </div>
    </div>

    <!-- 筛选搜索卡片 -->
    <div v-show="showSearch" class="ry-query-card category-query-card">
      <form class="ry-form-inline" @submit.prevent>
        <div class="ry-form-item">
          <span class="ry-form-label">搜索分类：</span>
          <div class="query-input-wrap">
            <AdminIcon name="search" :size="14" class="query-input-icon" />
            <input
              v-model.trim="queryParams.keyword"
              class="ry-input with-icon"
              style="width: 220px;"
              placeholder="输入分类名称或标识 slug"
            />
          </div>
        </div>

        <div class="ry-form-item">
          <span class="ry-form-label">分类层级：</span>
          <select v-model="queryParams.level" class="ry-select" style="width: 130px;">
            <option value="">全部层级</option>
            <option value="1">一级分类 (系列)</option>
            <option value="2">二级分类 (子类)</option>
          </select>
        </div>

        <div class="ry-form-item">
          <span class="ry-form-label">启用状态：</span>
          <select v-model="queryParams.isActive" class="ry-select" style="width: 120px;">
            <option value="">全部状态</option>
            <option value="true">已启用</option>
            <option value="false">已停用</option>
          </select>
        </div>

        <div class="ry-form-item" style="margin-left: auto;">
          <button class="ry-btn ry-btn-default" type="button" @click="resetQuery">
            <AdminIcon name="refresh" :size="13" />
            <span>重置筛选</span>
          </button>
        </div>
      </form>
    </div>

    <!-- 分类主体内容卡片 -->
    <div class="ry-table-card category-main-card">
      <!-- 顶部综合工具栏 -->
      <div class="ry-toolbar-row">
        <div class="ry-toolbar-left">
          <button class="ry-btn ry-btn-primary" type="button" @click="handleAddRoot">
            <AdminIcon name="plus" :size="14" />
            <span>新增一级分类</span>
          </button>

          <button
            v-if="viewMode === 'tree'"
            class="ry-btn ry-btn-default"
            type="button"
            :title="isAllCollapsed ? '展开所有一级分类的子项' : '收起所有一级分类的子项'"
            @click="toggleAllCollapse"
          >
            <AdminIcon :name="isAllCollapsed ? 'chevron-down' : 'chevron-right'" :size="13" />
            <span>{{ isAllCollapsed ? '全部展开' : '全部折叠' }}</span>
          </button>

          <button class="ry-btn ry-btn-success-plain" type="button" @click="loadData">
            <AdminIcon name="refresh" :size="13" />
            <span>刷新数据</span>
          </button>
        </div>

        <div class="ry-toolbar-right">
          <!-- 视图模式切换器 -->
          <div class="view-mode-toggle" title="切换视图模式">
            <button
              class="mode-btn"
              :class="{ active: viewMode === 'tree' }"
              type="button"
              @click="viewMode = 'tree'"
            >
              <AdminIcon name="list" :size="14" />
              <span>树形表格</span>
            </button>
            <button
              class="mode-btn"
              :class="{ active: viewMode === 'card' }"
              type="button"
              @click="viewMode = 'card'"
            >
              <AdminIcon name="grid" :size="14" />
              <span>系列卡片</span>
            </button>
          </div>

          <span class="ry-tag ry-tag-info">共 {{ totalFilteredCount }} 个分类</span>

          <button
            class="ry-tool-btn"
            type="button"
            :title="showSearch ? '隐藏搜索' : '显示搜索'"
            @click="showSearch = !showSearch"
          >
            <AdminIcon name="search" :size="14" />
          </button>
        </div>
      </div>

      <!-- 视图 1：【树形折叠层级表格 (Tree Table)】 -->
      <div v-if="viewMode === 'tree'" class="ry-table-wrap category-tree-table-wrap">
        <table class="ry-table category-tree-table">
          <thead>
            <tr>
              <th style="min-width: 260px;">分类结构与名称</th>
              <th style="width: 140px; text-align: center;">栏目图 (横幅)</th>
              <th style="width: 100px; text-align: center;">层级</th>
              <th style="width: 90px; text-align: center;">排序值</th>
              <th style="width: 100px; text-align: center;">启停状态</th>
              <th style="min-width: 200px; text-align: center;">快捷管理操作</th>
            </tr>
          </thead>

          <tbody v-if="loading">
            <tr>
              <td colspan="6" class="category-empty">
                <div class="empty-state">
                  <AdminIcon name="refresh" :size="24" class="spinning" />
                  <span>正在加载产品分类数据…</span>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody v-else-if="filteredTree.length === 0">
            <tr>
              <td colspan="6" class="category-empty">
                <div class="empty-state">
                  <AdminIcon name="categories" :size="32" style="color: #c0c4cc;" />
                  <span>未找到符合条件的分类数据</span>
                  <button class="ry-btn ry-btn-default ry-btn-sm" type="button" @click="resetQuery">
                    清除筛选条件
                  </button>
                </div>
              </td>
            </tr>
          </tbody>

          <!-- 树形数据渲染 -->
          <template v-for="root in filteredTree" :key="'root-' + root.id">
            <!-- 一级分类行 (Parent Row) -->
            <tr
              v-if="!root.isGhostRoot && queryParams.level !== '2'"
              class="root-row"
              :class="{ collapsed: collapsedMap[root.id] }"
            >
              <td>
                <div class="cell-root-name">
                  <!-- 展开折叠三角按钮 -->
                  <button
                    v-if="root.children.length > 0"
                    class="collapse-trigger-btn"
                    :class="{ rotated: !collapsedMap[root.id] }"
                    type="button"
                    :title="collapsedMap[root.id] ? '展开子分类' : '收起子分类'"
                    @click="toggleCollapse(root.id)"
                  >
                    <AdminIcon name="chevron-right" :size="13" />
                  </button>
                  <span v-else class="collapse-trigger-placeholder"></span>

                  <!-- 一级分类徽标与名称 -->
                  <div class="root-icon-badge">
                    <AdminIcon name="folder" :size="15" />
                  </div>

                  <div class="root-name-info">
                    <div class="name-main">
                      <strong class="root-title">{{ root.name }}</strong>
                      <code class="root-slug" :title="'URL 标识: ' + root.slug">{{ root.slug }}</code>
                    </div>
                    <div v-if="root.description" class="root-desc-brief" :title="root.description">
                      {{ root.description }}
                    </div>
                  </div>

                  <!-- 子分类数量胶囊 -->
                  <span
                    v-if="root.children.length > 0"
                    class="child-count-pill"
                    :title="'包含 ' + root.children.length + ' 个二级子分类'"
                  >
                    {{ root.children.length }} 个子类
                  </span>
                  <span v-else class="child-count-pill empty">暂无子类</span>
                </div>
              </td>

              <!-- 一级栏目图 -->
              <td style="text-align: center;">
                <div v-if="root.banner" class="banner-preview-box" @click="openPreview(root.banner, root.name + ' - 栏目图')">
                  <img :src="root.banner" :alt="root.name" class="banner-thumb-img" />
                  <div class="banner-preview-overlay">
                    <AdminIcon name="eye" :size="12" />
                  </div>
                </div>
                <span v-else class="banner-placeholder">待配置</span>
              </td>

              <!-- 层级 Tag -->
              <td style="text-align: center;">
                <span class="ry-tag ry-tag-primary">一级系列</span>
              </td>

              <!-- 排序 -->
              <td style="text-align: center;">
                <span class="order-badge">{{ root.sort_order }}</span>
              </td>

              <!-- 状态切换 -->
              <td style="text-align: center;">
                <button
                  class="status-toggle-pill"
                  :class="root.is_active ? 'active' : 'inactive'"
                  type="button"
                  :title="root.is_active ? '点击停用该一级分类（将同时隐藏下属分类和产品）' : '点击启用该一级分类'"
                  @click="handleQuickToggleActive(root)"
                >
                  <span class="status-dot"></span>
                  <span>{{ root.is_active ? '已启用' : '已停用' }}</span>
                </button>
              </td>

              <!-- 操作 -->
              <td style="text-align: center;">
                <div class="category-row-actions">
                  <button class="ry-btn ry-btn-primary-plain ry-btn-sm" type="button" @click="handleAddChild(root)">
                    <AdminIcon name="plus" :size="12" />
                    <span>加子类</span>
                  </button>
                  <button class="ry-link-btn" type="button" @click="handleUpdate(root)">
                    <AdminIcon name="edit" :size="13" />修改
                  </button>
                  <button class="ry-link-btn danger" type="button" @click="handleDelete(root)">
                    <AdminIcon name="trash" :size="13" />删除
                  </button>
                </div>
              </td>
            </tr>

            <!-- 二级分类行 (Child Rows) -->
            <template v-if="!collapsedMap[root.id] || queryParams.keyword || queryParams.level === '2'">
              <tr
                v-for="(child, cIdx) in (root.filteredChildren || [])"
                :key="'child-' + child.id"
                class="child-row"
              >
                <td>
                  <div class="cell-child-name">
                    <!-- 树形分支引线 -->
                    <div class="tree-branch-line">
                      <span class="branch-elbow">{{ cIdx === (root.filteredChildren.length - 1) ? '└─' : '├─' }}</span>
                    </div>

                    <div class="child-tag-dot"></div>

                    <div class="child-name-info">
                      <strong class="child-title">{{ child.name }}</strong>
                      <code class="child-slug" :title="'URL 标识: ' + child.slug">{{ child.slug }}</code>
                    </div>

                    <span v-if="child.description" class="child-desc-tip" :title="child.description">
                      {{ child.description }}
                    </span>
                  </div>
                </td>

                <!-- 二级分类栏目图展示：不维护栏目图，显示 — -->
                <td style="text-align: center;">
                  <span class="category-muted">—</span>
                </td>

                <!-- 层级 Tag -->
                <td style="text-align: center;">
                  <span class="ry-tag ry-tag-info">二级子类</span>
                </td>

                <!-- 排序 -->
                <td style="text-align: center;">
                  <span class="order-badge order-badge-child">{{ child.sort_order }}</span>
                </td>

                <!-- 状态切换 -->
                <td style="text-align: center;">
                  <button
                    class="status-toggle-pill"
                    :class="child.is_active && !parentIsInactive(child) ? 'active' : 'inactive'"
                    type="button"
                    :title="parentIsInactive(child) && child.is_active ? '所属一级分类已停用，前台当前不会展示；点击可同时停用该二级分类' : (child.is_active ? '点击停用该二级分类' : '点击启用该二级分类')"
                    @click="handleQuickToggleActive(child)"
                  >
                    <span class="status-dot"></span>
                    <span>{{ parentIsInactive(child) && child.is_active ? '上级停用' : (child.is_active ? '已启用' : '已停用') }}</span>
                  </button>
                </td>

                <!-- 操作 -->
                <td style="text-align: center;">
                  <div class="category-row-actions">
                    <button class="ry-link-btn" type="button" @click="handleUpdate(child)">
                      <AdminIcon name="edit" :size="13" />修改
                    </button>
                    <button class="ry-link-btn danger" type="button" @click="handleDelete(child)">
                      <AdminIcon name="trash" :size="13" />删除
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </template>
        </table>
      </div>

      <!-- 视图 2：【系列分组卡片展厅 (Grouped Grid Cards)】 -->
      <div v-else class="category-cards-grid">
        <div
          v-for="root in filteredTree"
          :key="'card-' + root.id"
          class="category-group-card"
          :class="{ inactive: !root.is_active }"
        >
          <!-- 卡片头部 Banner 与操作 -->
          <div class="group-card-header">
            <div class="group-banner-wrapper">
              <img
                v-if="root.banner"
                :src="root.banner"
                :alt="root.name"
                class="group-banner-img"
                @click="openPreview(root.banner, root.name + ' - 系列横幅图')"
              />
              <div v-else class="group-banner-empty">
                <AdminIcon name="image" :size="24" />
                <span>未设置系列横幅图</span>
              </div>
              <div class="group-banner-badge-row">
                <span class="card-order-tag">排序: {{ root.sort_order }}</span>
                <span :class="['ry-tag', root.is_active ? 'ry-tag-success' : 'ry-tag-danger']">
                  {{ root.is_active ? '已启用' : '已停用' }}
                </span>
              </div>
            </div>

            <div class="group-header-info">
              <div class="group-title-row">
                <div class="group-title-left">
                  <h4 class="group-title">{{ root.name }}</h4>
                  <code class="group-slug">{{ root.slug }}</code>
                </div>
                <div class="group-header-actions">
                  <button class="ry-btn ry-btn-default ry-btn-sm" type="button" title="编辑一级分类" @click="handleUpdate(root)">
                    <AdminIcon name="edit" :size="12" />
                    <span>编辑</span>
                  </button>
                  <button class="ry-btn ry-btn-danger-plain ry-btn-sm" type="button" title="删除一级分类" @click="handleDelete(root)">
                    <AdminIcon name="trash" :size="12" />
                  </button>
                </div>
              </div>
              <p v-if="root.description" class="group-desc">{{ root.description }}</p>
            </div>
          </div>

          <!-- 卡片主体：二级分类列表 -->
          <div class="group-card-body">
            <div class="children-header">
              <span class="children-title">
                下级子分类
                <span class="children-count">({{ (root.filteredChildren || []).length }})</span>
              </span>
              <button class="ry-btn ry-btn-primary-plain ry-btn-sm" type="button" @click="handleAddChild(root)">
                <AdminIcon name="plus" :size="12" />
                <span>添加子类</span>
              </button>
            </div>

            <div v-if="(root.filteredChildren || []).length === 0" class="children-empty">
              <span>暂无二级子分类，点击上方按钮新增</span>
            </div>

            <ul v-else class="children-list">
              <li
                v-for="child in root.filteredChildren"
                :key="'card-child-' + child.id"
                class="child-item"
                :class="{ inactive: !child.is_active || parentIsInactive(child) }"
              >
                <div class="child-item-left">
                  <span class="child-item-dot"></span>
                  <div class="child-item-meta">
                    <strong class="child-item-name">{{ child.name }}</strong>
                    <span class="child-item-order">#{{ child.sort_order }}</span>
                  </div>
                  <span v-if="!child.is_active" class="child-item-inactive-tag">已停用</span>
                  <span v-else-if="parentIsInactive(child)" class="child-item-inactive-tag">上级停用</span>
                </div>

                <div class="child-item-actions">
                  <button class="icon-action-btn" type="button" title="修改" @click="handleUpdate(child)">
                    <AdminIcon name="edit" :size="12" />
                  </button>
                  <button class="icon-action-btn danger" type="button" title="删除" @click="handleDelete(child)">
                    <AdminIcon name="trash" :size="12" />
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增 / 编辑 分类对话框 (Modal Dialog) -->
    <div v-if="dialogOpen" class="ry-dialog-backdrop" @click.self="cancelDialog">
      <div class="ry-dialog category-dialog">
        <div class="ry-dialog-header">
          <div class="dialog-header-title-box">
            <div class="dialog-header-icon">
              <AdminIcon name="categories" :size="18" />
            </div>
            <h3 class="ry-dialog-title">{{ dialogTitle }}</h3>
          </div>
          <button class="ry-dialog-close" type="button" @click="cancelDialog">✕</button>
        </div>

        <form class="ry-dialog-body ry-dialog-form" @submit.prevent="submitForm">
          <!-- 分类层级选择分段控件 -->
          <div class="ry-form-field full">
            <label class="ry-field-label">分类层级设定</label>
            <div class="level-segment-control">
              <button
                class="segment-option"
                :class="{ active: formLevel === 1 }"
                type="button"
                :disabled="editingHasChildren && formLevel === 1"
                @click="formLevel = 1"
              >
                <AdminIcon name="layers" :size="14" />
                <span>一级分类 (作为前台系列主栏目)</span>
              </button>
              <button
                class="segment-option"
                :class="{ active: formLevel === 2 }"
                type="button"
                :disabled="editingHasChildren"
                @click="formLevel = 2"
              >
                <AdminIcon name="products" :size="14" />
                <span>二级分类 (作为系列下属子分类)</span>
              </button>
            </div>
            <small v-if="editingHasChildren" class="category-help text-warning">
              该一级分类已有下属二级子分类，不支持变更为二级分类。
            </small>
          </div>

          <!-- 所属一级分类下拉 (仅二级分类展示) -->
          <div v-if="formLevel === 2" class="ry-form-field full">
            <label class="ry-field-label"><span class="required">*</span>所属一级分类 (系列)</label>
            <select v-model="categoryForm.parent" class="ry-select" required :disabled="editingHasChildren">
              <option value="" disabled>请选择所属一级系列</option>
              <option v-for="item in parentOptions" :key="item.id" :value="item.id">
                {{ item.name }} (排序: {{ item.sort_order }})
              </option>
            </select>
            <small class="category-help">二级分类将归属于所选一级分类，并在官网前台导航下拉与系列列表中呈现。</small>
          </div>

          <!-- 分类名称与排序 -->
          <div class="ry-form-row">
            <div class="ry-form-field">
              <label class="ry-field-label"><span class="required">*</span>分类名称</label>
              <input
                v-model.trim="categoryForm.name"
                class="ry-input"
                maxlength="100"
                required
                placeholder="例如：护肤系列、保湿洁面"
              />
            </div>
            <div class="ry-form-field">
              <label class="ry-field-label">显示排序值 (数值越小越靠前)</label>
              <input
                v-model.number="categoryForm.sort_order"
                class="ry-input"
                type="number"
                min="0"
                placeholder="0"
              />
            </div>
          </div>

          <!-- 启用状态开关 -->
          <div class="ry-form-field full">
            <label class="ry-field-label">公开发布状态</label>
            <div class="active-switch-panel">
              <label class="ry-radio-label">
                <input v-model="categoryForm.is_active" type="checkbox" />
                <strong>在官网公开展示并参与导航与首页系列联动</strong>
              </label>
              <span class="active-switch-desc">
                {{ formLevel === 2 && categoryForm.is_active && selectedParent && !selectedParent.is_active
                  ? '所属一级分类已停用；即使当前二级分类启用，前台仍会隐藏。'
                  : (categoryForm.is_active ? '当前状态：已启用，前台访客可正常浏览。' : '当前状态：已停用，前台所有页面将隐藏此分类。') }}
              </span>
            </div>
          </div>

          <!-- 分类简介 (适用于一级分类或二级分类) -->
          <div class="ry-form-field full">
            <label class="ry-field-label">分类简介描述 (选填)</label>
            <textarea
              v-model.trim="categoryForm.description"
              class="ry-textarea"
              rows="3"
              placeholder="可填写该分类在官网对应产品页面顶部展示的品牌系列描述文案…"
            ></textarea>
          </div>

          <!-- 栏目图上传区 (一级分类维护，二级分类显示继承提示) -->
          <div v-if="formLevel === 1" class="ry-form-field full">
            <AdminImageUploader
              v-model="bannerFile"
              input-id="category-banner"
              label="一级系列栏目图 (横幅 Banner)"
              hint="支持 JPG、PNG、WebP，建议比例 16:5（约 1600×500 像素）；用于前台官网该系列产品页横幅及下属二级分类的继承显示"
              aspect-ratio="16 / 5"
              :current-url="categoryForm.banner"
            />
          </div>

          <div v-else class="category-banner-inherit-card">
            <AdminIcon name="info" :size="15" class="inherit-info-icon" />
            <span class="inherit-text-simple">二级分类不维护栏目图；前台对应产品页面将显示所属一级分类的栏目图。</span>
          </div>
        </form>

        <div class="ry-dialog-footer">
          <button class="ry-btn ry-btn-default" type="button" @click="cancelDialog">取消</button>
          <button class="ry-btn ry-btn-primary" type="button" :disabled="saving" @click="submitForm">
            {{ saving ? '正在保存…' : '确定保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 高清大图预览模态框 (Image Lightbox) -->
    <div v-if="previewImageUrl" class="ry-dialog-backdrop lightbox-backdrop" @click.self="closePreview">
      <div class="lightbox-dialog">
        <div class="lightbox-header">
          <span class="lightbox-title">{{ previewImageTitle }}</span>
          <button class="lightbox-close" type="button" @click="closePreview">✕</button>
        </div>
        <div class="lightbox-body">
          <img :src="previewImageUrl" :alt="previewImageTitle" class="lightbox-img" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 顶部业务说明条 */
.category-notice-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e6f7df 100%);
  border: 1px solid #c2e7b0;
  border-radius: var(--ry-radius);
  color: #3f7e26;
  font-size: 13.5px;
}

.notice-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notice-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #67c23a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notice-text strong {
  color: #276014;
}

.notice-actions {
  flex-shrink: 0;
}

.notice-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #ffffff;
  border: 1px solid #c2e7b0;
  border-radius: var(--ry-radius);
  color: #2f6f58;
  font-size: 12.5px;
  font-weight: 500;
  transition: all 0.15s;
}

.notice-link:hover {
  background: #67c23a;
  color: #ffffff;
  border-color: #67c23a;
}

/* 筛选搜索卡片 */
.category-query-card {
  padding: 14px 18px 2px;
}

.query-input-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.query-input-icon {
  position: absolute;
  left: 10px;
  color: var(--ry-text-placeholder);
  pointer-events: none;
}

.ry-input.with-icon {
  padding-left: 30px;
}

/* 主内容卡片 */
.category-main-card {
  margin-bottom: 20px;
}

/* 视图模式切换按钮组 */
.view-mode-toggle {
  display: inline-flex;
  align-items: center;
  background: #f0f2f5;
  padding: 2px;
  border-radius: var(--ry-radius);
  border: 1px solid var(--ry-border-base);
}

.mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 26px;
  padding: 0 10px;
  font-size: 12px;
  color: var(--ry-text-regular);
  background: transparent;
  border: none;
  border-radius: 2px;
  transition: all 0.15s;
}

.mode-btn.active {
  background: #ffffff;
  color: var(--ry-primary);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 树形表格样式 */
.category-tree-table {
  border-collapse: collapse;
}

.root-row td {
  background-color: #fafbfc !important;
  font-weight: 500;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.root-row:hover td {
  background-color: #f2f6fc !important;
}

.cell-root-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collapse-trigger-btn {
  width: 22px;
  height: 22px;
  border-radius: 3px;
  border: 1px solid var(--ry-border-base);
  background: #ffffff;
  color: var(--ry-text-regular);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.collapse-trigger-btn:hover {
  border-color: var(--ry-primary);
  color: var(--ry-primary);
}

.collapse-trigger-btn.rotated {
  transform: rotate(90deg);
  background: var(--ry-primary);
  border-color: var(--ry-primary);
  color: #ffffff;
}

.collapse-trigger-placeholder {
  width: 22px;
  display: inline-block;
}

.root-icon-badge {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  background: #ecf5ff;
  color: var(--ry-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.root-name-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.name-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.root-title {
  font-size: 14.5px;
  color: var(--ry-text-primary);
}

.root-slug {
  font-size: 11px;
  color: var(--ry-text-placeholder);
  background: #f0f2f5;
  padding: 1px 5px;
  border-radius: 3px;
}

.root-desc-brief {
  font-size: 11.5px;
  color: var(--ry-text-secondary);
  max-width: 320px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.child-count-pill {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 10px;
  background: #e1f3d8;
  color: #529b2e;
  border: 1px solid #c2e7b0;
  white-space: nowrap;
}

.child-count-pill.empty {
  background: #f4f4f5;
  color: #909399;
  border-color: #e9e9eb;
}

/* 栏目图预览小图 */
.banner-preview-box {
  position: relative;
  width: 80px;
  height: 30px;
  border-radius: 3px;
  overflow: hidden;
  margin: 0 auto;
  border: 1px solid var(--ry-border-base);
  cursor: pointer;
}

.banner-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.banner-preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s;
}

.banner-preview-box:hover .banner-preview-overlay {
  opacity: 1;
}

.banner-placeholder,
.category-muted {
  font-size: 13px;
  color: var(--ry-text-placeholder);
}

/* 排序数值 Badge */
.order-badge {
  display: inline-block;
  min-width: 24px;
  padding: 1px 6px;
  font-size: 12px;
  font-weight: 600;
  background: #f0f2f5;
  color: var(--ry-text-regular);
  border-radius: 3px;
}

.order-badge-child {
  background: #ffffff;
  border: 1px solid var(--ry-border-lighter);
}

/* 状态切换按钮胶囊 */
.status-toggle-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
  background: transparent;
}

.status-toggle-pill.active {
  background: #f0f9eb;
  border-color: #e1f3d8;
  color: #67c23a;
}

.status-toggle-pill.active:hover {
  background: #e1f3d8;
}

.status-toggle-pill.inactive {
  background: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
}

.status-toggle-pill.inactive:hover {
  background: #fde2e2;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* 操作区按钮 */
.category-row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 二级分类行 (Child Row) */
.child-row td {
  background-color: #ffffff;
}

.child-row:hover td {
  background-color: #f5f7fa !important;
}

.cell-child-name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 28px;
}

.tree-branch-line {
  color: var(--ry-border-base);
  font-family: monospace;
  font-size: 14px;
  user-select: none;
}

.child-tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409eff;
  flex-shrink: 0;
}

.child-name-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.child-title {
  font-size: 13.5px;
  color: var(--ry-text-regular);
}

.child-slug {
  font-size: 11px;
  color: var(--ry-text-placeholder);
}

.child-desc-tip {
  font-size: 11px;
  color: var(--ry-text-placeholder);
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 空状态 */
.category-empty {
  padding: 40px !important;
  text-align: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--ry-text-secondary);
  font-size: 13.5px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 视图 2：【系列分组卡片展厅 (Cards Grid)】 */
.category-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 4px 0;
}

.category-group-card {
  background: #ffffff;
  border: 1px solid var(--ry-border-lighter);
  border-radius: var(--ry-radius);
  box-shadow: var(--ry-shadow-card);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.2s;
}

.category-group-card:hover {
  transform: translateY(-2px);
  border-color: #b3d8ff;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.category-group-card.inactive {
  opacity: 0.75;
  filter: grayscale(0.2);
}

/* 卡片顶部横幅 */
.group-banner-wrapper {
  position: relative;
  width: 100%;
  height: 110px;
  background: #2d3a4b;
  overflow: hidden;
}

.group-banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s;
}

.group-banner-img:hover {
  transform: scale(1.04);
}

.group-banner-empty {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #304156 0%, #1f2d3d 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #8c9eb5;
  font-size: 12px;
}

.group-banner-badge-row {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-order-tag {
  background: rgba(0, 0, 0, 0.6);
  color: #ffffff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  backdrop-filter: blur(4px);
}

.group-header-info {
  padding: 14px 16px 12px;
  border-bottom: 1px solid var(--ry-border-lighter);
  background: #ffffff;
}

.group-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.group-title-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.group-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--ry-text-primary);
}

.group-slug {
  font-size: 11px;
  color: var(--ry-text-placeholder);
}

.group-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.group-desc {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--ry-text-secondary);
  line-height: 1.4;
}

/* 卡片子项主体 */
.group-card-body {
  padding: 14px 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fbfbfc;
}

.children-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.children-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ry-text-regular);
}

.children-count {
  font-weight: normal;
  color: var(--ry-text-secondary);
}

.children-empty {
  padding: 20px 10px;
  text-align: center;
  color: var(--ry-text-placeholder);
  font-size: 12px;
  background: #ffffff;
  border: 1px dashed var(--ry-border-base);
  border-radius: var(--ry-radius);
}

.children-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.child-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: #ffffff;
  border: 1px solid var(--ry-border-lighter);
  border-radius: var(--ry-radius);
  transition: all 0.15s;
}

.child-item:hover {
  border-color: var(--ry-primary-border);
  background: #f9fbff;
}

.child-item.inactive {
  opacity: 0.6;
}

.child-item-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.child-item-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ry-primary);
}

.child-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.child-item-name {
  font-size: 13px;
  color: var(--ry-text-regular);
}

.child-item-order {
  font-size: 11px;
  color: var(--ry-text-placeholder);
}

.child-item-inactive-tag {
  font-size: 10px;
  background: #fef0f0;
  color: #f56c6c;
  padding: 1px 4px;
  border-radius: 2px;
}

.child-item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-action-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 3px;
  color: var(--ry-text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}

.icon-action-btn:hover {
  background: #ecf5ff;
  color: var(--ry-primary);
}

.icon-action-btn.danger:hover {
  background: #fef0f0;
  color: var(--ry-danger);
}

/* 对话框专用定制 */
.category-dialog {
  width: min(680px, 95vw);
}

.dialog-header-title-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-header-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--ry-radius);
  background: #ecf5ff;
  color: var(--ry-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 分段层级选择器 */
.level-segment-control {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.segment-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 38px;
  border: 1px solid var(--ry-border-base);
  border-radius: var(--ry-radius);
  background: #fafafa;
  color: var(--ry-text-regular);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.segment-option:hover:not(:disabled) {
  border-color: var(--ry-primary);
  color: var(--ry-primary);
}

.segment-option.active {
  border-color: var(--ry-primary);
  background: var(--ry-primary-light);
  color: var(--ry-primary);
  font-weight: 600;
}

.segment-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.active-switch-panel {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 14px;
  background: #fbfbfb;
  border: 1px solid var(--ry-border-lighter);
  border-radius: var(--ry-radius);
}

.active-switch-desc {
  font-size: 12px;
  color: var(--ry-text-secondary);
  padding-left: 20px;
}

.category-banner-inherit-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  background: #f8f9fa;
  border: 1px dashed var(--ry-border-base);
  border-radius: var(--ry-radius);
}

.inherit-info-icon {
  color: #909399;
  flex-shrink: 0;
}

.inherit-text-simple {
  font-size: 12.5px;
  color: var(--ry-text-secondary);
  line-height: 1.5;
}

/* 高清大图预览 Lightbox */
.lightbox-backdrop {
  z-index: 3000;
  background: rgba(0, 0, 0, 0.75);
}

.lightbox-dialog {
  max-width: 90vw;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.lightbox-header {
  padding: 12px 18px;
  background: #1f2d3d;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.lightbox-title {
  font-size: 14px;
  font-weight: 500;
}

.lightbox-close {
  background: transparent;
  border: none;
  color: #bfcbd9;
  font-size: 16px;
  cursor: pointer;
}

.lightbox-close:hover {
  color: #ffffff;
}

.lightbox-body {
  padding: 16px;
  background: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-img {
  max-width: 80vw;
  max-height: 75vh;
  object-fit: contain;
  border-radius: 2px;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .category-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 720px) {
  .category-cards-grid {
    grid-template-columns: 1fr;
  }

  .category-notice-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .root-slug,
  .child-slug {
    display: none;
  }

  .level-segment-control {
    grid-template-columns: 1fr;
  }
}
</style>
