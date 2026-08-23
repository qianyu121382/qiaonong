import { reactive } from 'vue'

export const toastState = reactive({
  toasts: [],
})

let toastId = 0

export function showToast(message, type = 'success', duration = 3200) {
  const id = ++toastId
  toastState.toasts.push({ id, message, type })
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
}

export function removeToast(id) {
  const index = toastState.toasts.findIndex((t) => t.id === id)
  if (index !== -1) {
    toastState.toasts.splice(index, 1)
  }
}
