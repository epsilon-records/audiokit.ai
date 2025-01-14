<script lang="ts">
  import { page } from '$app/state';

  const navigation = [
    { label: 'Profile', href: '/my/settings/profile' },
    { label: 'Account', href: '/my/settings/account' },
    { label: 'Security', href: '/my/settings/security' },
  ];
</script>

<ul class="menu bg-bass-100 w-56 p-2 rounded-box">
  {#each navigation as item}
    <li>
      <a href={item.href} class="found-medium {$page.url.pathname === item.href ? 'active' : ''}">
        {item.label}
      </a>
    </li>
  {/each}
</ul>
