-- Rode DEPOIS do deploy na Vercel, trocando <URL_DO_DEPLOY> e <CRON_SECRET>.
-- Chama o publicador de posts agendados a cada minuto.
create extension if not exists pg_cron;
create extension if not exists pg_net;

select cron.schedule(
  'instagram-publish-due',
  '* * * * *',
  $$
  select net.http_post(
    url := 'https://<URL_DO_DEPLOY>/api/cron/publish',
    headers := jsonb_build_object('Authorization', 'Bearer <CRON_SECRET>')
  );
  $$
);
