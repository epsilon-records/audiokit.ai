<script lang="ts">
  import { page } from '$app/state';

  let { pathname } = $derived(page.url);

  const navigation = [
    { label: 'Create Artist', href: '/my/settings/create/' },
    { label: 'Artist Profile', href: '/my/settings/profile/' },
    { label: 'Team Settings', href: '/my/settings/team/' },
    { label: 'Account Settings', href: '/my/settings/account/' },
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
</ul>
