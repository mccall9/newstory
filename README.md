# Instagram MCP

Servidor MCP próprio para operar uma conta do Instagram pelo Claude: publicar, agendar, ver posts e métricas, responder comentários e rodar o fluxo **"comente e ganhe o link"** (DM automática para quem comenta a palavra-chave).

Usa só a API oficial da Meta, sem scraping.

## Arquitetura

```
Claude ──► /api/mcp ──────────► Instagram API (graph.instagram.com)
                │
                ▼
            Supabase  ◄── /api/webhook ◄── Meta (comentário novo)
  (agenda, regras, leads,  ◄── /api/cron/publish ◄── pg_cron (a cada minuto)
   token, mídias)          ◄── /api/cron/refresh-token ◄── Vercel Cron (diário)
```

| Endpoint | Função |
|---|---|
| `api/mcp.ts` | Servidor MCP (Streamable HTTP), protegido por `MCP_AUTH_TOKEN` |
| `api/webhook.ts` | Recebe comentários, confere a palavra-chave e manda a DM (private reply) |
| `api/cron/publish.ts` | Publica os posts agendados que já passaram do horário |
| `api/cron/refresh-token.ts` | Renova o token de longa duração (~60 dias) |

A API do Instagram não tem agendamento nativo. O post fica no banco e o cron publica na hora.

## Ferramentas (24)

| Grupo | Ferramentas |
|---|---|
| Conta | `ig_get_profile`, `ig_get_account_insights` |
| Meus posts | `ig_list_media`, `ig_get_media`, `ig_get_media_insights`, `ig_delete_media` |
| Publicar | `ig_upload_media`, `ig_publish_now`, `ig_publish_container`, `ig_publishing_limit` |
| Agendar | `ig_schedule_post`, `ig_list_scheduled`, `ig_update_scheduled`, `ig_cancel_scheduled` |
| Comentários | `ig_get_comments`, `ig_reply_comment`, `ig_hide_comment`, `ig_delete_comment` |
| Comente e ganhe | `ig_create_keyword_rule`, `ig_list_rules`, `ig_update_rule`, `ig_list_leads` |
| Pesquisa | `ig_business_discovery`, `ig_hashtag_media` |

As ferramentas de pesquisa usam a API com **Facebook Login** (`graph.facebook.com`). Elas só funcionam com `FB_PAGE_ACCESS_TOKEN` e `FB_IG_USER_ID` configurados. O resto usa **Business Login for Instagram**.

## Configuração

### 1. Conta e app na Meta

1. Crie a conta do Instagram e mude para **conta profissional** (Business ou Creator).
2. Em [developers.facebook.com](https://developers.facebook.com), crie um app do tipo **Business** e adicione o produto **Instagram → API setup with Instagram login**.
3. Em "Generate access tokens", adicione sua conta e gere o token. Ele já vem com longa duração (~60 dias).
4. Anote o **IG User ID**, o **token** e o **App Secret** (em App settings → Basic).
5. Permissões: `instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_comments`, `instagram_business_manage_messages` e `instagram_business_manage_insights`.

Em modo de desenvolvimento, tudo funciona na sua própria conta. A revisão da Meta só é necessária para outras contas.

### 2. Supabase

1. Aplique as migrations de `supabase/migrations/`. Elas criam as tabelas, o bucket público `media` e o cron que publica os agendados.
2. Guarde no Vault o `CRON_SECRET` e, depois do deploy, a URL do publicador (os comandos estão no topo de `0002_publish_cron.sql`). Sem a URL, o cron não faz nada.

### 3. Vercel

Configure as variáveis de `.env.example` no projeto e faça o deploy. Gere os segredos assim:

```bash
openssl rand -hex 32   # MCP_AUTH_TOKEN, CRON_SECRET, META_WEBHOOK_VERIFY_TOKEN
```

### 4. Webhook (comente e ganhe)

No app da Meta, em Instagram → Webhooks:

- Callback URL: `https://<seu-deploy>/api/webhook`
- Verify token: o valor de `META_WEBHOOK_VERIFY_TOKEN`
- Assine o campo **comments**

### 5. Conectar ao Claude

- **Claude Code:** `claude mcp add --transport http instagram https://<seu-deploy>/api/mcp --header "Authorization: Bearer <MCP_AUTH_TOKEN>"`
- **Clientes que não enviam headers:** use `https://<seu-deploy>/api/mcp?key=<MCP_AUTH_TOKEN>`

## Limites da Meta

- Private reply: 1 por comentário, até 7 dias depois dele. Mensagens seguintes só depois que a pessoa responder, dentro de 24h.
- Publicação: cota diária por conta. Consulte com `ig_publishing_limit`.
- Hashtags: 30 hashtags diferentes a cada 7 dias.
- Mídias precisam estar em URL pública. Use `ig_upload_media`.

## Desenvolvimento

```bash
npm install
npm run typecheck
npm test
```
