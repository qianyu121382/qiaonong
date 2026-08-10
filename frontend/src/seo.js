const SITE_URL = 'https://zgqnht.com'
const DEFAULT_DESCRIPTION = '巧侬花田官方网站，展示品牌介绍、护肤产品、院护系列、医美产品及联系方式。'

function ensureMeta(selector, attributes) {
  let element = document.head.querySelector(selector)
  if (!element) {
    element = document.createElement('meta')
    Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value))
    document.head.appendChild(element)
  }
  return element
}

export function setPageSeo({ title, description = DEFAULT_DESCRIPTION, path = window.location.pathname, noindex = false }) {
  document.title = title
  ensureMeta('meta[name="description"]', { name: 'description' }).setAttribute('content', description)
  ensureMeta('meta[name="robots"]', { name: 'robots' }).setAttribute('content', noindex ? 'noindex,follow' : 'index,follow')

  let canonical = document.head.querySelector('link[rel="canonical"]')
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.setAttribute('rel', 'canonical')
    document.head.appendChild(canonical)
  }
  canonical.setAttribute('href', `${SITE_URL}${path === '/' ? '/' : path.replace(/\/$/, '')}`)
}

export { DEFAULT_DESCRIPTION }
