# Conteúdo

Gerador de carrosséis no modelo Pattiners e das páginas-guia do comente-e-ganhe.

1. Escreva os posts em um JSON (veja `posts-dia.json`).
2. `python3 gen.py posts.json` gera `carrosseis/CARROSSEL-<slug>.html` e `public/<slug>.html`.
3. `node shot.js ../public/<slug>.html carrosseis/phone-<slug>.png` tira o print do guia para o último slide.
4. Dentro de `carrosseis/`: `node ../render.js CARROSSEL-<slug>.html <prefixo>` exporta os slides em JPEG 1080×1350.
5. `python3 schedule.py plan.json <SUPABASE_SERVICE_ROLE_KEY>` sobe os slides, agenda os posts e cria as regras. Ele lê o `MCP_AUTH_TOKEN` de um arquivo `vercel-env.txt` na pasta acima de `carrosseis/`.
