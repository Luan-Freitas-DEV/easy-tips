'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '../../../../components/api'

export default function ShipperServices() {
  const [items, setItems] = useState<any[]>([])
  useEffect(() => {
    const token = localStorage.getItem('token') || ''
    api('/shipper/my-services', 'GET', token).then(r=>r.json()).then(setItems)
  }, [])
  return <main><h3>Meus serviços</h3>{items.map(i=><div key={i.id}><Link href={`/shipper/services/${i.id}`}>{i.title} - {i.status}</Link></div>)}</main>
}
