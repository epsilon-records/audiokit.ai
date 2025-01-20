<script lang="ts">
  import '../app.css';
  import { ClerkProvider } from 'svelte-clerk';
  import Nav from '$lib/components/Nav.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { Toaster } from 'svelte-sonner';
  import type { Snippet } from 'svelte';
  import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';

  let { children } = $props<{ children: Snippet }>();
</script>

<svelte:head>
  {#if !import.meta.env.PROD}
    <script
      data-recording-token="YlK6PCQzlht5rZutE1qns77yPUiS5FNPT6QBMXM0"
      data-is-production-environment="false"
      src="https://snippet.meticulous.ai/v1/meticulous.js"
    ></script>
    <script>
      (function () {
        var dbpr = 100;
        if (Math.random() * 100 > 100 - dbpr) {
          var d = 'dbbRum',
            w = window,
            o = document,
            a = addEventListener,
            scr = o.createElement('script');
          scr.async = !0;
          w[d] = w[d] || [];
          w[d].push(['presampling', dbpr]);
          ['error', 'unhandledrejection'].forEach(function (t) {
            a(t, function (e) {
              w[d].push([t, e]);
            });
          });
          scr.src = 'https://cdn.debugbear.com/5GOULW9zQSMv.js';
          o.head.appendChild(scr);
        }
      })();
    </script>
  {/if}
</svelte:head>

<ClerkProvider publishableKey={PUBLIC_CLERK_PUBLISHABLE_KEY}>
  <div class="min-h-screen flex flex-col">
    <Nav />
    <main class="flex-1 pt-16">
      {@render children()}
    </main>
    <Footer />
  </div>
  <Toaster richColors />
</ClerkProvider>
