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
const selectedFileName = ref('')

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

  selectedFileName.value = file.name
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
  selectedFileName.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
  emit('update:modelValue', null)
  emit('clear')
}
</script>

<template>
  <div class="ry-uploader-wrap">
    <!-- Header Label -->
    <div class="ry-uploader-label-row">
      <span class="ry-field-label">
        <span v-if="required" class="required">*</span>
        {{ label }}
      </span>
      <span v-if="hint" class="ry-uploader-hint-inline">{{ hint }}</span>
    </div>

    <!-- Hidden Native File Input -->
    <input
      :id="inputId"
      ref="fileInputRef"
      type="file"
      class="ry-hidden-file-input"
      accept="image/jpeg,image/png,image/webp"
      @change="handleFileChange"
    />

    <!-- RuoYi / Element Plus Upload Card -->
    <div class="ry-upload-card" :class="{ 'has-file': Boolean(displayUrl) }">
      <!-- When an image exists (online or selected) -->
      <div v-if="displayUrl" class="ry-upload-preview-row">
        <div class="ry-upload-thumb-box" :style="{ aspectRatio }">
          <img :src="displayUrl" alt="预览图" class="ry-upload-thumb-img" />
          <div v-if="localPreview" class="ry-upload-new-badge">新选择</div>
        </div>

        <div class="ry-upload-meta-box">
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span v-if="localPreview" class="ry-tag ry-tag-success">
              已选文件：{{ selectedFileName || '待上传' }}
            </span>
            <span v-else class="ry-tag ry-tag-info">
              当前线上图片
            </span>
          </div>

          <div class="ry-upload-btn-group">
            <button
              class="ry-btn ry-btn-primary-plain ry-btn-sm"
              type="button"
              @click="triggerSelect"
            >
              <AdminIcon name="upload" :size="13" />
              <span>更换文件</span>
            </button>

            <a
              v-if="displayUrl && !localPreview"
              :href="displayUrl"
              target="_blank"
              class="ry-btn ry-btn-default ry-btn-sm"
            >
              <AdminIcon name="external" :size="13" />
              <span>查看大图</span>
            </a>

            <button
              v-if="localPreview"
              class="ry-btn ry-btn-danger-plain ry-btn-sm"
              type="button"
              @click="handleClear"
            >
              <AdminIcon name="close" :size="13" />
              <span>取消更改</span>
            </button>
          </div>
        </div>
      </div>

      <!-- When empty / no image selected -->
      <div v-else class="ry-upload-empty-box" @click="triggerSelect">
        <div class="ry-upload-icon-circle">
          <AdminIcon name="upload" :size="18" />
        </div>
        <div class="ry-upload-empty-text">
          <button class="ry-btn ry-btn-primary-plain ry-btn-sm" type="button" @click.stop="triggerSelect">
            <AdminIcon name="upload" :size="13" />
            <span>选择文件</span>
          </button>
          <span class="ry-upload-empty-hint">点击选择本地图片上传</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ry-uploader-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ry-uploader-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.ry-uploader-hint-inline {
  font-size: 12px;
  color: var(--ry-text-secondary, #909399);
}

.ry-hidden-file-input {
  display: none;
}

.ry-upload-card {
  border: 1px dashed var(--ry-border-base, #dcdfe6);
  border-radius: var(--ry-radius, 4px);
  background-color: #fbfdff;
  padding: 12px 14px;
  transition: border-color 0.2s, background-color 0.2s;
}

.ry-upload-card:hover {
  border-color: var(--ry-primary, #409eff);
  background-color: #f5f9ff;
}

.ry-upload-card.has-file {
  background-color: #ffffff;
  border-style: solid;
  border-color: var(--ry-border-lighter, #ebeef5);
}

.ry-upload-empty-box {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 4px 0;
}

.ry-upload-icon-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--ry-primary-light, #ecf5ff);
  color: var(--ry-primary, #409eff);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ry-upload-empty-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ry-upload-empty-hint {
  font-size: 12.5px;
  color: var(--ry-text-secondary, #909399);
}

.ry-upload-preview-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.ry-upload-thumb-box {
  width: 64px;
  height: 64px;
  border-radius: 3px;
  overflow: hidden;
  position: relative;
  background-color: #f4f4f5;
  border: 1px solid var(--ry-border-light, #e4e7ed);
  flex-shrink: 0;
}

.ry-upload-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.ry-upload-new-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(64, 158, 255, 0.9);
  color: #ffffff;
  font-size: 10px;
  text-align: center;
  line-height: 16px;
  font-weight: 500;
}

.ry-upload-meta-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.ry-upload-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
