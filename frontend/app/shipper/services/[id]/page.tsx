'use client'
import { useEffect, useState } from 'react'
import { api } from '../../../../../components/api'

export default function ShipperDetail({ params }: { params: { id: string } }) {
  const [offers, setOffers] = useState<any[]>([])
  useEffect(() => {
    const token = localStorage.getItem('token') || ''
    api(`/services/${params.id}/offers`, 'GET', token).then(r=>r.json()).then(setOffers)
  }, [params.id])

  async function accept(offerId: number) {
    const token = localStorage.getItem('token') || ''
    await api(`/offers/${offerId}/accept`, 'POST', token)
    alert('Aceita')
  }
  return <main><h3>Ofertas</h3>{offers.map(o=><div key={o.id}>{o.kind} R$ {o.price} <button onClick={()=>accept(o.id)}>Aceitar contraproposta</button></div>)}</main>
}
