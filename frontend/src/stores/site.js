import { reactive } from 'vue'

import { api } from '../api'


export const siteState = reactive({
  ready: false,
  settings: { site_name: '巧侬' },
  categories: [],
})

let loadingPromise

export function loadSite() {
  if (loadingPromise) return loadingPromise
  loadingPromise = Promise.all([
    api('/api/content/site/'),
    api('/api/catalog/categories/'),
  ]).then(([settings, categories]) => {
    siteState.settings = settings
    siteState.categories = categories
    siteState.ready = true
  }).catch(() => {
    siteState.ready = true
  })
  return loadingPromise
}
