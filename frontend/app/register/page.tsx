'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '../../../components/api'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('BOTH')
  const router = useRouter()

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const res = await api('/auth/register', 'POST', undefined, { name, email, password, role })
    if (res.ok) router.push('/login')
  }

  return <form onSubmit={submit}><h2>Cadastro</h2><input placeholder='nome' value={name} onChange={e=>setName(e.target.value)}/><input placeholder='email' value={email} onChange={e=>setEmail(e.target.value)}/><input type='password' placeholder='senha' value={password} onChange={e=>setPassword(e.target.value)}/><select value={role} onChange={e=>setRole(e.target.value)}><option>SHIPPER</option><option>DRIVER</option><option>BOTH</option></select><button>Cadastrar</button></form>
}
