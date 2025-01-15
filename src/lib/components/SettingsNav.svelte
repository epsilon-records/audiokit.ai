<script lang="ts">
  import { page } from '$app/state';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';

  let { pathname } = $derived(page.url);

  const navigation = [
    { label: 'Profile', href: '/my/settings/profile' },
    { label: 'Account', href: '/my/settings/account' },
    { label: 'Security', href: '/my/settings/security' },
  ];
</script>

<ul class="menu bg-green-100 w-56 p-2 rounded-box">
  <li class="p-2 text-xl">
    <OrganizationSwitcher
      appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
      hidePersonal={true}
      afterCreateOrganizationUrl="/my/settings/profile"
      afterSelectOrganizationUrl="/my/settings/profile"
    />
  </li>
  {#each navigation as item}
    <li class="p-2 text-xl">
      <a href={item.href} class="font-medium {pathname === item.href ? 'active' : ''}">
        {item.label}
      </a>
    </li>
  {/each}
</ul>
