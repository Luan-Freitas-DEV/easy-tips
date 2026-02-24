import Link from 'next/link'

export default function Dash() {
  return <main><h2>Dashboard</h2><ul><li><Link href='/shipper/services/new'>Novo frete</Link></li><li><Link href='/shipper/services'>Meus fretes</Link></li><li><Link href='/driver/feed'>Feed motorista</Link></li><li><Link href='/driver/intent'>Intenção de retorno</Link></li><li><Link href='/driver/assignment'>Minha viagem</Link></li></ul></main>
}
