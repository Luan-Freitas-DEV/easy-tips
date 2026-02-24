'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '../../../components/api'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')
  const router = useRouter()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const res = await api('/auth/login', 'POST', undefined, { email, password })
    const data = await res.json()
    if (!res.ok) return setMsg(data.detail || 'erro')
    localStorage.setItem('token', data.access_token)
    router.push('/dashboard')
  }

  return <form onSubmit={submit}><h2>Login</h2><input placeholder='email' value={email} onChange={e=>setEmail(e.target.value)}/><input placeholder='senha' type='password' value={password} onChange={e=>setPassword(e.target.value)}/><button>Entrar</button><p>{msg}</p></form>
}
