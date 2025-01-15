<script lang="ts">
  import { page } from '$app/state';
  import { UserProfile } from 'svelte-clerk';

  let { pathname } = $derived(page.url);

  const navigation = [
    { label: 'Profile', href: '/my/settings/profile' },
    { label: 'Account', href: '/my/settings/account' },
    { label: 'Security', href: '/my/settings/security' },
  ];
</script>

<ul class="menu bg-green-100 w-56 p-2 rounded-box">
  {#each navigation as item}
    <li class="p-2 text-xl">
      <a href={item.href} class="font-medium {pathname === item.href ? 'active' : ''}">
        {item.label}
      </a>
    </li>
  {/each}
  <li class="p-2 text-xl">
    <UserProfile routing="path" path="/my/settings/account" />
  </li>
</ul>
