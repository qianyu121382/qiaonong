import { reactive } from 'vue'

export const tagsViewState = reactive({
  visitedViews: [
    { name: 'dashboard', path: '/', title: '工作台', affix: true },
  ],
})

const routeTitleMap = {
  dashboard: '工作台',
  products: '产品管理',
  carousel: '首页轮播',
  company: '公司信息',
}

export function addView(route) {
  if (!route.name || route.name === 'login') return
  const title = routeTitleMap[route.name] || route.meta?.title || '未命名'
  const exists = tagsViewState.visitedViews.some((v) => v.path === route.path)
  if (!exists) {
    tagsViewState.visitedViews.push({
      name: route.name,
      path: route.path,
      title,
      affix: route.path === '/',
    })
  }
}

export function closeView(path) {
  const index = tagsViewState.visitedViews.findIndex((v) => v.path === path)
  if (index > -1) {
    const view = tagsViewState.visitedViews[index]
    if (view.affix) return null // Affixed tabs cannot be closed
    tagsViewState.visitedViews.splice(index, 1)
    return tagsViewState.visitedViews[Math.max(0, index - 1)] || null
  }
  return null
}

export function closeOtherViews(currentPath) {
  tagsViewState.visitedViews = tagsViewState.visitedViews.filter(
    (v) => v.affix || v.path === currentPath
  )
}
