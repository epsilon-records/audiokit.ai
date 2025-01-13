<script lang="ts">
import { 
  Twitter, 
  Instagram, 
  Youtube, 
  Facebook,
  Globe,
  Music
} from 'lucide-svelte';

// Define a proper interface for the social links
interface SocialLinks {
  platform: string;
  url: string;
}

// Update props to expect an array of SocialLinks
let { links } = $props<{ links: SocialLinks[] }>();

const platformIcons = {
  twitter: Twitter,
  instagram: Instagram,
  youtube: Youtube,
  facebook: Facebook,
  soundcloud: Music,
  website: Globe,
};

type PlatformKey = keyof typeof platformIcons;

function getPlatformIcon(platform: string) {
  const normalized = platform.toLowerCase().replace(/[\s-]+/g, '');
  
  const key = Object.keys(platformIcons).find(k => 
    k.toLowerCase().replace(/[\s-]+/g, '') === normalized
  ) as PlatformKey;
  
  return platformIcons[key] || Globe;
}
</script>

{#if links && links.length > 0}
  <div>
    <h2 class="text-sm text-[#00ffff] uppercase mb-2">Follow</h2>
    <div class="flex gap-4">
      {#each links as { platform, url }}
        <a 
          href={url} 
          target="_blank" 
          rel="noopener noreferrer"
          class="flex items-center gap-2 text-[#ff00ff] hover:text-[#00ffff] transition-colors group"
        >
          <svelte:component 
            this={getPlatformIcon(platform)} 
            class="w-5 h-5 transition-transform group-hover:scale-110" 
          />
          <span class="text-sm">{platform}</span>
        </a>
      {/each}
    </div>
  </div>
{/if} 