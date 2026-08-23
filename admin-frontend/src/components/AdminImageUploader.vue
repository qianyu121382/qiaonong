<script setup>
import { computed, ref } from 'vue'
import AdminIcon from './AdminIcon.vue'

const props = defineProps({
  modelValue: {
    type: [File, Object, null],
    default: null,
  },
  currentUrl: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '上传图片',
  },
  hint: {
    type: String,
    default: '支持 JPG、PNG、WebP 格式',
  },
  inputId: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
  aspectRatio: {
    type: String,
    default: '1 / 1',
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'clear'])

const fileInputRef = ref(null)
const localPreview = ref('')

const displayUrl = computed(() => {
  if (localPreview.value) return localPreview.value
  if (props.currentUrl) return props.currentUrl
  return ''
})

function triggerSelect() {
  fileInputRef.value?.click()
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  emit('update:modelValue', file)
  emit('change', file)

  const reader = new FileReader()
  reader.onload = (e) => {
    localPreview.value = e.target?.result || ''
  }
  reader.readAsDataURL(file)
}

function handleClear() {
  localPreview.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  emit('update:modelValue', null)
  emit('clear')
}
</script>

<template>
  <div class="uploader-component">
    <div class="form-label">
      <span>
        {{ label }}
        <span v-if="required" class="required-dot">*</span>
      </span>
      <span v-if="displayUrl && !localPreview" class="hint-inline">
        <a :href="displayUrl" target="_blank" class="preview-link">
          <AdminIcon name="external" :size="12" /> 查看原图
        </a>
      </span>
    </div>

    <input
      :id="inputId"
      ref="fileInputRef"
      type="file"
      class="uploader-file-input"
      accept="image/jpeg,image/png,image/webp"
      @change="handleFileChange"
    />

    <div
      class="uploader-box"
      :class="{ 'has-image': Boolean(displayUrl) }"
      @click="triggerSelect"
    >
      <div v-if="displayUrl" class="uploader-preview-row">
        <div class="preview-wrapper" :style="{ aspectRatio }">
          <img :src="displayUrl" alt="预览图" class="preview-img" />
          <div v-if="localPreview" class="new-tag">待上传</div>
        </div>
        <div class="preview-meta">
          <div class="meta-title">{{ localPreview ? '已选择新文件' : '当前线上图片' }}</div>
          <div class="meta-hint">{{ hint }}</div>
          <div class="meta-actions" @click.stop>
            <button class="btn btn-sm btn-outline" type="button" @click="triggerSelect">
              <AdminIcon name="upload" :size="14" />
              更换图片
            </button>
            <button
              v-if="localPreview"
              class="btn btn-sm btn-danger-outline"
              type="button"
              @click="handleClear"
            >
              <AdminIcon name="close" :size="14" />
              取消选择
            </button>
          </div>
        </div>
      </div>

      <div v-else class="uploader-empty-state">
        <div class="upload-icon-circle">
          <AdminIcon name="upload" :size="20" />
        </div>
        <div class="upload-text">
          <strong>点击上传图片</strong>
          <span>{{ hint }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.uploader-component {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-link {
  color: var(--color-primary, #174233);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
}

.preview-link:hover {
  text-decoration: underline;
}

.uploader-box {
  cursor: pointer;
  border: 1.5px dashed var(--color-border, #e2e8e4);
  border-radius: var(--radius-md, 10px);
  padding: 14px 16px;
  background: var(--color-surface-subtle, #f8faf9);
  transition: all 0.2s ease;
}

.uploader-box:hover {
  border-color: var(--color-primary, #174233);
  background: var(--color-primary-subtle, #f2f7f4);
}

.uploader-empty-state {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 0;
}

.upload-icon-circle {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-full, 9999px);
  background: #ffffff;
  border: 1px solid var(--color-border, #e2e8e4);
  color: var(--color-primary, #174233);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-xs, 0 1px 2px rgba(0,0,0,0.04));
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.upload-text strong {
  font-size: 13.5px;
  color: var(--color-text-main, #192a24);
}

.upload-text span {
  font-size: 12px;
  color: var(--color-text-muted, #82948c);
}

.uploader-preview-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-wrapper {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-sm, 6px);
  overflow: hidden;
  position: relative;
  background: #ffffff;
  border: 1px solid var(--color-border, #e2e8e4);
  flex-shrink: 0;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.new-tag {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(23, 66, 51, 0.85);
  color: #ffffff;
  font-size: 10px;
  text-align: center;
  padding: 2px 0;
  font-weight: 600;
}

.preview-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.meta-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-text-main, #192a24);
}

.meta-hint {
  font-size: 12px;
  color: var(--color-text-muted, #82948c);
}

.meta-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
</style>
