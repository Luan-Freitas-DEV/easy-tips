'use client'
import { useEffect, useState } from 'react'
import { api } from '../../../../components/api'

export default function AssignmentPage() {
  const [service, setService] = useState<any>(null)
  const [suggestions, setSuggestions] = useState<any[]>([])

  useEffect(() => {
    const token = localStorage.getItem('token') || ''
    api('/driver/my-assignment', 'GET', token).then(r=>r.json()).then((data)=>{
      setService(data)
      if (data?.dest_lat) {
        api('/drivers/1/backhaul_suggestions?from_lat='+data.dest_lat+'&from_lng='+data.dest_lng+'&intended_dest_lat=-23.55&intended_dest_lng=-46.63&radius_km=300').then(r=>r.json()).then(setSuggestions)
      }
    })
  }, [])

  async function doAction(action: 'collect'|'deliver') {
    const token = localStorage.getItem('token') || ''
    await api(`/assignments/${service.id}/${action}`, 'POST', token)
    alert('ok')
  }

  if (!service) return <p>Sem assignment.</p>
  return <main><h3>Serviço atual: {service.title}</h3><button onClick={()=>doAction('collect')}>COLETADO</button><button onClick={()=>doAction('deliver')}>ENTREGUE</button><h4>Sugestões de retorno</h4>{suggestions.map(s=><div key={s.service_id}>{s.title} score {s.score}</div>)}</main>
}
