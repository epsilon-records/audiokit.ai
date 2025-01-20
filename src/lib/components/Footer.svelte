<script lang="ts">
  import {
    siInstagram,
    siSoundcloud,
    siBandcamp,
    siYoutube,
    siTwitch,
    siTiktok,
    siMixcloud,
    siBeatport,
  } from 'simple-icons';
  const currentYear = $derived(new Date().getFullYear());

  // Define brand colors from Simple Icons
  const BRAND_COLORS = {
    beatport: '#01FF95',
    instagram: '#E4405F',
    soundcloud: '#FF6B35',
    bandcamp: '#408294',
    youtube: '#FF1E1E',
    twitch: '#9146FF',
    tiktok: '#FF00FF',
    mixcloud: '#9245FF',
  } as const;
</script>

<footer class="border-t">
  <div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
      <!-- About -->
      <div>
        <h3 class="font-bold mb-4">AudioKit</h3>
        <p class="text-muted-foreground text-sm">
          Specialized music distribution platform providing API access and AI-powered tools for
          artists and developers.
        </p>
      </div>

      <!-- Quick Links -->
      <div>
        <h3 class="font-bold mb-4">Quick Links</h3>
        <ul class="space-y-2 text-sm">
          <li><a href="/artists" class="hover:underline">Artists</a></li>
          <li><a href="/releases" class="hover:underline">Releases</a></li>
          <li><a href="/events" class="hover:underline">Events</a></li>
          <li><a href="/docs" class="hover:underline">Docs</a></li>
          <li><a href="/faq" class="hover:underline">FAQ</a></li>
        </ul>
      </div>

      <!-- Connect -->
      <div>
        <h3 class="font-bold mb-4">Connect</h3>
        <ul class="space-y-2 text-sm">
          <li><a href="/contact" class="hover:underline">Contact</a></li>
          <li><a href="/newsletter" class="hover:underline">Newsletter</a></li>
          <li>
            <a
              href="/demos"
              class="hover:underline inline-flex items-center gap-1"
              target="_blank"
              rel="noopener noreferrer"
            >
              Demo Submission
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="relative top-[1px]"
              >
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          </li>
        </ul>
      </div>

      <!-- Social -->
      <div>
        <h3 class="font-bold mb-4">Follow Us</h3>
        <div class="grid grid-cols-4 gap-4">
          <a
            href="https://beatport.com/label/epsilon-records/112442"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on Beatport"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.beatport}>
              <path d={siBeatport.path} />
            </svg>
          </a>
          <a
            href="https://instagram.com/epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on Instagram"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.instagram}>
              <path d={siInstagram.path} />
            </svg>
          </a>
          <a
            href="https://youtube.com/epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on YouTube"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.youtube}>
              <path d={siYoutube.path} />
            </svg>
          </a>
          <a
            href="https://twitch.tv/epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on Twitch"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.twitch}>
              <path d={siTwitch.path} />
            </svg>
          </a>
          <a
            href="https://tiktok.com/@epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on TikTok"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.tiktok}>
              <path d={siTiktok.path} />
            </svg>
          </a>
          <a
            href="https://mixcloud.com/epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on Mixcloud"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.mixcloud}>
              <path d={siMixcloud.path} />
            </svg>
          </a>
          <a
            href="https://soundcloud.com/epsilonrecords"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on SoundCloud"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.soundcloud}>
              <path d={siSoundcloud.path} />
            </svg>
          </a>
          <a
            href="http://epsilonrecords.bandcamp.com"
            class="hover:opacity-80 transition-opacity"
            aria-label="Follow us on Bandcamp"
          >
            <svg role="img" viewBox="0 0 24 24" class="w-6 h-6" fill={BRAND_COLORS.bandcamp}>
              <path d={siBandcamp.path} />
            </svg>
          </a>
        </div>
      </div>
    </div>

    <div class="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
      <p>© {currentYear} AudioKit. All rights reserved.</p>
    </div>
  </div>
</footer>
