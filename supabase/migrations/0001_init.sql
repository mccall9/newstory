-- Instagram MCP: agendamentos, regras comente-e-ganhe, leads e token.
-- Todas as tabelas têm RLS ligado e nenhuma policy: só a service role (servidor) acessa.

create table public.scheduled_posts (
  id uuid primary key default gen_random_uuid(),
  post_type text not null check (post_type in ('photo', 'carousel', 'reel', 'story')),
  caption text,
  media_urls text[] not null check (cardinality(media_urls) between 1 and 10),
  publish_at timestamptz not null,
  status text not null default 'scheduled'
    check (status in ('scheduled', 'publishing', 'published', 'failed', 'cancelled')),
  container_id text,
  ig_media_id text,
  error text,
  published_at timestamptz,
  created_at timestamptz not null default now()
);
create index scheduled_posts_due_idx on public.scheduled_posts (publish_at) where status = 'scheduled';

create table public.keyword_rules (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  ig_media_id text, -- null = vale para todos os posts
  keywords text[] not null check (cardinality(keywords) > 0),
  dm_message text not null,
  link text,
  public_reply text,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.leads (
  comment_id text primary key, -- garante uma DM por comentário
  rule_id uuid references public.keyword_rules (id) on delete set null,
  ig_media_id text not null,
  ig_user_id text not null,
  username text,
  comment_text text,
  status text not null default 'pending' check (status in ('pending', 'sent', 'failed')),
  error text,
  sent_at timestamptz,
  created_at timestamptz not null default now()
);
create index leads_rule_idx on public.leads (rule_id);
create index leads_created_idx on public.leads (created_at desc);

create table public.ig_tokens (
  id text primary key,
  access_token text not null,
  expires_at timestamptz,
  updated_at timestamptz not null default now()
);

create view public.keyword_rules_stats with (security_invoker = true) as
select r.*,
  count(l.comment_id) filter (where l.status = 'sent') as dms_sent,
  count(l.comment_id) filter (where l.status = 'failed') as dms_failed
from public.keyword_rules r
left join public.leads l on l.rule_id = r.id
group by r.id;

alter table public.scheduled_posts enable row level security;
alter table public.keyword_rules enable row level security;
alter table public.leads enable row level security;
alter table public.ig_tokens enable row level security;

-- Bucket público para as mídias (a API do Instagram baixa a mídia por URL pública).
insert into storage.buckets (id, name, public)
values ('media', 'media', true)
on conflict (id) do nothing;
