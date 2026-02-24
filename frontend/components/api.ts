export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function api(path: string, method = 'GET', token?: string, body?: unknown) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: body ? JSON.stringify(body) : undefined,
    cache: 'no-store'
  })
  return res
}
