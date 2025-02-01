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
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-WN04JQMELT"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {
      dataLayer.push(arguments);
    }
    gtag('js', new Date());

    gtag('config', 'G-WN04JQMELT');
  </script>

  <!-- For old IEs -->
  <link rel="shortcut icon" href="favicon.ico" />

  <!-- For new browsers - multisize ico  -->
  <link rel="icon" type="image/x-icon" sizes="16x16 32x32" href="favicon.ico" />

  <!-- For iPad with high-resolution Retina display running iOS ≥ 7: -->
  <link rel="apple-touch-icon" sizes="152x152" href="favicon-152-precomposed.png" />

  <!-- For iPad with high-resolution Retina display running iOS ≤ 6: -->
  <link rel="apple-touch-icon" sizes="144x144" href="favicon-144-precomposed.png" />

  <!-- For iPhone with high-resolution Retina display running iOS ≥ 7: -->
  <link rel="apple-touch-icon" sizes="120x120" href="favicon-120-precomposed.png" />

  <!-- For iPhone with high-resolution Retina display running iOS ≤ 6: -->
  <link rel="apple-touch-icon" sizes="114x114" href="favicon-114-precomposed.png" />

  <!-- For iPhone 6+ -->
  <link rel="apple-touch-icon" sizes="180x180" href="favicon-180-precomposed.png" />

  <!-- For first- and second-generation iPad: -->
  <link rel="apple-touch-icon" sizes="72x72" href="favicon-72-precomposed.png" />

  <!-- For non-Retina iPhone, iPod Touch, and Android 2.1+ devices: -->
  <link rel="apple-touch-icon" sizes="57x57" href="favicon-57.png" />

  <!-- For Old Chrome -->
  <link rel="icon" sizes="32x32" href="favicon-32.png" />

  <!-- For IE10 Metro -->
  <meta name="msapplication-TileColor" content="#FFFFFF" />
  <meta name="msapplication-TileImage" content="favicon-144.png" />
  <meta name="theme-color" content="#ffffff" />

  <!-- Chrome for Android -->
  <link rel="manifest" href="manifest.json" />
  <link rel="icon" sizes="192x192" href="favicon-192.png" />

  <!-- TikTok Pixel Code Start -->
  <script>
    !(function (w, d, t) {
      w.TiktokAnalyticsObject = t;
      var ttq = (w[t] = w[t] || []);
      (ttq.methods = [
        'page',
        'track',
        'identify',
        'instances',
        'debug',
        'on',
        'off',
        'once',
        'ready',
        'alias',
        'group',
        'enableCookie',
        'disableCookie',
        'holdConsent',
        'revokeConsent',
        'grantConsent',
      ]),
        (ttq.setAndDefer = function (t, e) {
          t[e] = function () {
            t.push([e].concat(Array.prototype.slice.call(arguments, 0)));
          };
        });
      for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]);
      (ttq.instance = function (t) {
        for (var e = ttq._i[t] || [], n = 0; n < ttq.methods.length; n++)
          ttq.setAndDefer(e, ttq.methods[n]);
        return e;
      }),
        (ttq.load = function (e, n) {
          var r = 'https://analytics.tiktok.com/i18n/pixel/events.js',
            o = n && n.partner;
          (ttq._i = ttq._i || {}),
            (ttq._i[e] = []),
            (ttq._i[e]._u = r),
            (ttq._t = ttq._t || {}),
            (ttq._t[e] = +new Date()),
            (ttq._o = ttq._o || {}),
            (ttq._o[e] = n || {});
          n = document.createElement('script');
          (n.type = 'text/javascript'), (n.async = !0), (n.src = r + '?sdkid=' + e + '&lib=' + t);
          e = document.getElementsByTagName('script')[0];
          e.parentNode.insertBefore(n, e);
        });

      ttq.load('CUAKG4JC77UE0Q4QB7MG');
      ttq.page();
    })(window, document, 'ttq');
  </script>
  <!-- TikTok Pixel Code End -->

  <!-- Start of HubSpot Embed Code -->
  <script
    type="text/javascript"
    id="hs-script-loader"
    async
    defer
    src="//js-eu1.hs-scripts.com/143610477.js"
  ></script>
  <!-- End of HubSpot Embed Code -->
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
