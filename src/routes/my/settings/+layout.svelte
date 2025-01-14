<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { LayoutData } from './$types';
  import { page } from '$app/state';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();

  const navigation = [
    { label: 'Profile', href: '/my/settings/profile' },
    { label: 'Account', href: '/my/settings/account' },
    { label: 'Security', href: '/my/settings/security' },
  ];
</script>

<div class="w-full h-full px-2">
  <h3 class="text-2xl font-medium">Settings</h3>
  <div class="divider"></div>
  <div class="flex w-full h-full space-x-4">
    <ul class="menu bg-bass-100 w-56 p-2 rounded-box">
      {#each navigation as item}
        <li>
          <a
            href={item.href}
            class="found-medium {page.url.pathname === item.href ? 'active' : ''}"
          >
            {item.label}
          </a>
        </li>
      {/each}
    </ul>
  </div>
  <div class="w-full">
    {@render children()}
  </div>
</div>
