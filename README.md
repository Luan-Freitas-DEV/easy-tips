# Easy Tips - MVP "iFood de Caminhoneiros"

Marketplace de fretes para o Brasil inteiro com dois perfis (Embarcador e Caminhoneiro), negociação por oferta/contraproposta e sugestões de carga de retorno (backhaul).

## Stack

- **Frontend**: Next.js 14 (App Router, TypeScript)
- **Backend**: FastAPI + SQLAlchemy + Alembic + JWT
- **Banco**: PostgreSQL 15 com PostGIS
- **Orquestração local**: Docker Compose
- **Testes**: Pytest (API)

## Estrutura

- `backend/` API REST, regras de negócio, migrações e testes.
- `frontend/` UI web responsiva (mobile-first) com páginas mínimas do MVP.
- `docker-compose.yml` sobe banco, backend e frontend.

## Requisitos

- Docker + Docker Compose

## Variáveis de ambiente

Backend (`backend/.env`):

```env
DATABASE_URL=postgresql+psycopg://app:app@db:5432/easytips
JWT_SECRET=super-secret-change-me
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000
```

Frontend (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Como rodar

```bash
docker compose up --build -d
```

### Migrações

As migrações rodam automaticamente na inicialização do backend (`alembic upgrade head`).

Para rodar manualmente:

```bash
docker compose exec backend alembic upgrade head
```

## API e documentação

- Swagger: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Fluxo principal do MVP

1. Registrar usuário com role `SHIPPER`, `DRIVER` ou `BOTH`.
2. Embarcador cria `Service` (frete).
3. Caminhoneiro aceita ou contrapropõe (`Offer`).
4. Embarcador aceita contraproposta.
5. Sistema cria `Assignment` e muda `Service` para `ACEITO`.
6. Motorista do assignment avança para `COLETADO` e `ENTREGUE`.
7. Motorista informa intenção de destino final e recebe sugestões de backhaul.

## Endpoints implementados

### Auth
- `POST /auth/register`
- `POST /auth/login`

### Perfil
- `GET /me`

### Services
- `POST /services`
- `GET /services`
- `GET /services/{id}`
- `PATCH /services/{id}`

### Offers / Negociação
- `POST /services/{id}/offers`
- `GET /services/{id}/offers`
- `POST /offers/{id}/accept`

### Assignment / Status
- `POST /assignments/{service_id}/collect`
- `POST /assignments/{service_id}/deliver`

### Backhaul
- `POST /drivers/intent`
- `GET /drivers/{driver_id}/backhaul_suggestions`

## Testes

Rodar testes da API:

```bash
docker compose exec backend pytest -q
```

## Lint/format

Backend:

```bash
docker compose exec backend ruff check .
docker compose exec backend ruff format --check .
```

Frontend:

```bash
docker compose exec frontend npm run lint
```

## Seed opcional

O projeto inclui somente estruturas e fluxo principal. Pode-se cadastrar usuários e criar dados manualmente pela UI/API.

## Observações do MVP

- Cálculo de proximidade/backhaul usa fórmula de Haversine (fallback sem função geoespacial dedicada no SQL).
- Estrutura preparada para evoluir para consultas espaciais PostGIS puras em produção.
