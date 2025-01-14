<script lang="ts">
  let { href, text = 'Back' } = $props<{
    href: string;
    text?: string;
  }>();
</script>

<a
  {href}
  class="inline-flex items-center gap-2 text-[#00ffff] hover:text-[#ff00ff] transition-colors"
>
  <span class="text-2xl">←</span>
  <span class="uppercase tracking-wider">{text}</span>
</a>
