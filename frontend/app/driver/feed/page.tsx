'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '../../../../components/api'

export default function Feed() {
  const [items, setItems] = useState<any[]>([])
  useEffect(() => { api('/services?status=PUBLICADO').then(r=>r.json()).then(setItems) }, [])
  return <main><h3>Feed</h3>{items.map(i=><div key={i.id}><Link href={`/driver/services/${i.id}`}>{i.title} - R$ {i.offered_price}</Link></div>)}</main>
}
