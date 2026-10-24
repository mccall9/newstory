-- Publicador de posts agendados: pg_cron chama /api/cron/publish a cada minuto.
-- A URL e o segredo ficam no Vault (fora do código). Enquanto não existirem, não faz nada:
--   select vault.create_secret('<CRON_SECRET>', 'instagram_cron_secret');
--   select vault.create_secret('https://<seu-deploy>/api/cron/publish', 'instagram_publish_url');
create extension if not exists pg_cron;
create extension if not exists pg_net;

create or replace function public.trigger_instagram_publish()
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  publish_url text;
  secret text;
begin
  select decrypted_secret into publish_url from vault.decrypted_secrets where name = 'instagram_publish_url';
  select decrypted_secret into secret from vault.decrypted_secrets where name = 'instagram_cron_secret';
  if publish_url is null or secret is null then
    return;
  end if;
  perform net.http_post(
    url := publish_url,
    headers := jsonb_build_object('Authorization', 'Bearer ' || secret, 'Content-Type', 'application/json'),
    body := '{}'::jsonb,
    timeout_milliseconds := 55000
  );
end;
$$;

revoke all on function public.trigger_instagram_publish() from public, anon, authenticated;

select cron.schedule('instagram-publish-due', '* * * * *', 'select public.trigger_instagram_publish()');
