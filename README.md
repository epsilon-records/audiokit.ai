# audiokit.ai

The AudioKit website: the landing page and the API docs. The API itself lives in [`epsilon-records/audiokit`](https://github.com/epsilon-records/audiokit).

Plain HTML and one stylesheet. No framework and no build step: Netlify publishes `site/` as it is.

## Layout

```
site/
  index.html        landing page
  docs/index.html   API v1 reference
  thanks.html       shown after the early-access form
  404.html
  styles.css        every page's styles (design tokens at the top)
  favicon.svg
netlify.toml        publish directory and security headers
```

## Develop

```bash
python3 -m http.server 8000 -d site   # then open http://localhost:8000
```

## Keeping the docs right

`site/docs/index.html` restates the API's contract: endpoints, request fields, operations, webhook signing and error codes. When the API changes, update it in the same week, and check the webhook examples still pass the test vector in the API's README. Only list an operation as live once `GET /v1/capabilities` returns it.

## Early-access form

The form on the landing page is a Netlify Form named `access`. Submissions appear under the site's **Forms** tab in Netlify once form detection is enabled there (Forms › Enable form detection, then redeploy). A honeypot field filters simple bots; Netlify's spam filter handles the rest.

## Deploy

Netlify site `audiokit` (https://audiokit.netlify.app). Every push to `main` deploys if the site is linked to this repo; otherwise deploy `site/` from the Netlify UI or CLI.

The previous Svelte app is preserved on the `archive/pre-reset-2026-11-02` branch.
