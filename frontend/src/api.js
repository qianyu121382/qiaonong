export async function api(path) {
  const response = await fetch(path, { headers: { Accept: 'application/json' } })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const error = new Error(data?.detail || `内容加载失败（${response.status}）`)
    error.status = response.status
    throw error
  }
  return data
}
