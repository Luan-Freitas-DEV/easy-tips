'use client'
import { useState } from 'react'
import { api } from '../../../../../components/api'

export default function DriverService({ params }: { params: { id: string } }) {
  const [price, setPrice] = useState(0)
  const [message, setMessage] = useState('')

  async function send(kind: 'ACCEPT'|'COUNTER') {
    const token = localStorage.getItem('token') || ''
    const res = await api(`/services/${params.id}/offers`, 'POST', token, { kind, price, message })
    alert(res.ok ? 'Enviado' : 'Erro')
  }

  return <main><h3>Negociar serviço</h3><input type='number' value={price} onChange={e=>setPrice(Number(e.target.value))}/><input placeholder='mensagem' value={message} onChange={e=>setMessage(e.target.value)}/><button onClick={()=>send('ACCEPT')}>Aceitar</button><button onClick={()=>send('COUNTER')}>Contrapropor</button></main>
}
