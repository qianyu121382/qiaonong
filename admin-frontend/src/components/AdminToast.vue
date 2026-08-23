<script setup>
import { removeToast, toastState } from '../stores/toast'
import AdminIcon from './AdminIcon.vue'
</script>

<template>
  <teleport to="body">
    <div class="toast-container" aria-live="polite">
      <transition-group name="toast-anim">
        <div
          v-for="toast in toastState.toasts"
          :key="toast.id"
          class="toast-item"
          :class="`toast-${toast.type}`"
        >
          <div class="toast-icon">
            <AdminIcon
              v-if="toast.type === 'success'"
              name="check-circle"
              :size="18"
            />
            <AdminIcon
              v-else-if="toast.type === 'error'"
              name="alert-circle"
              :size="18"
            />
            <AdminIcon
              v-else
              name="info"
              :size="18"
            />
          </div>
          <div class="toast-content">
            {{ toast.message }}
          </div>
          <button
            class="toast-close"
            type="button"
            aria-label="关闭"
            @click="removeToast(toast.id)"
          >
            <AdminIcon name="close" :size="14" />
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 380px;
  width: calc(100vw - 32px);
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md, 10px);
  background: #ffffff;
  box-shadow: 0 10px 30px -5px rgba(23, 58, 48, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  color: var(--color-text, #1e2f28);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.toast-success {
  border-left: 4px solid var(--color-success, #16a34a);
}
.toast-success .toast-icon {
  color: var(--color-success, #16a34a);
}

.toast-error {
  border-left: 4px solid var(--color-danger, #e03131);
}
.toast-error .toast-icon {
  color: var(--color-danger, #e03131);
}

.toast-info {
  border-left: 4px solid var(--color-primary, #1b493b);
}
.toast-info .toast-icon {
  color: var(--color-primary, #1b493b);
}

.toast-content {
  flex: 1;
  word-break: break-word;
}

.toast-close {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #8c9d96);
  border-radius: 4px;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}

.toast-close:hover {
  color: var(--color-text, #1e2f28);
  background: #f0f3f1;
}

/* Animations */
.toast-anim-enter-active,
.toast-anim-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-anim-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}

.toast-anim-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

@media (max-width: 640px) {
  .toast-container {
    top: 16px;
    right: 16px;
    left: 16px;
    width: auto;
  }
}
</style>
