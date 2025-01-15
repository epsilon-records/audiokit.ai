<script lang="ts">
  import { page } from '$app/state';

  let pathname = $derived(
    page.url.pathname.endsWith('/') ? page.url.pathname : `${page.url.pathname}/`,
  );

  const navigation = [
    { label: 'Select', href: '/my/settings/select' },
    { label: 'Create', href: '/my/settings/create' },
    { label: 'Profile', href: '/my/settings/profile' },
    { label: 'Releases', href: '/my/settings/releases' },
    { label: 'Team', href: '/my/settings/team' },
    { label: 'Account', href: '/my/settings/account' },
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
