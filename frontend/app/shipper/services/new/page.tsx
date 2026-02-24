'use client'
import { useState } from 'react'
import { api } from '../../../../../components/api'

const initial = {
  title: '', description: '', service_type: 'LOTACAO', origin_address: '', origin_lat: -23.55, origin_lng: -46.63,
  dest_address: '', dest_lat: -22.9, dest_lng: -47.06, offered_price: 1000
}

export default function NewService() {
  const [f, setF] = useState(initial)
  const [msg, setMsg] = useState('')
  async function submit(e: React.FormEvent) {
    e.preventDefault()
    const now = new Date().toISOString()
    const token = localStorage.getItem('token') || ''
    const payload = { ...f, pickup_window_start: now, pickup_window_end: now, delivery_window_start: now, delivery_window_end: now }
    const res = await api('/services', 'POST', token, payload)
    setMsg(res.ok ? 'Criado!' : 'Erro')
  }
  return <form onSubmit={submit}><h3>Novo Serviço</h3><input placeholder='Título' value={f.title} onChange={e=>setF({...f,title:e.target.value})}/><input placeholder='Descrição' value={f.description} onChange={e=>setF({...f,description:e.target.value})}/><input placeholder='Origem' value={f.origin_address} onChange={e=>setF({...f,origin_address:e.target.value})}/><input placeholder='Destino' value={f.dest_address} onChange={e=>setF({...f,dest_address:e.target.value})}/><input type='number' value={f.offered_price} onChange={e=>setF({...f,offered_price:Number(e.target.value)})}/><button>Publicar</button><p>{msg}</p></form>
}
