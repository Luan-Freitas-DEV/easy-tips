'use client'
import { useState } from 'react'
import { api } from '../../../../components/api'

export default function IntentPage() {
  const [address, setAddress] = useState('São Paulo')
  async function submit() {
    const now = new Date().toISOString()
    const token = localStorage.getItem('token') || ''
    const res = await api('/drivers/intent', 'POST', token, { intended_dest_lat: -23.55, intended_dest_lng: -46.63, intended_dest_address: address, available_from: now, available_to: now })
    alert(res.ok ? 'Salvo' : 'Erro')
  }
  return <main><h3>Destino final pretendido</h3><input value={address} onChange={e=>setAddress(e.target.value)}/><button onClick={submit}>Salvar</button></main>
}
