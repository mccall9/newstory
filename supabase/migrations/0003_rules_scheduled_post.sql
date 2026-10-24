-- Regra de comente-e-ganhe presa a um post agendado: o publicador preenche
-- ig_media_id quando o post vai ao ar.
alter table public.keyword_rules
  add column scheduled_post_id uuid references public.scheduled_posts (id) on delete set null;
create index keyword_rules_scheduled_post_idx on public.keyword_rules (scheduled_post_id);

-- A view usa r.*: recriar para incluir a nova coluna.
drop view public.keyword_rules_stats;
create view public.keyword_rules_stats with (security_invoker = true) as
select r.*,
  count(l.comment_id) filter (where l.status = 'sent') as dms_sent,
  count(l.comment_id) filter (where l.status = 'failed') as dms_failed
from public.keyword_rules r
left join public.leads l on l.rule_id = r.id
group by r.id;
