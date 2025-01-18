<script lang="ts">
  import { page } from '$app/state';
  import { error } from '@sveltejs/kit';
  import { cn } from '$lib/utils';
  import { toast } from 'svelte-sonner';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { neobrutalism, dark } from '@clerk/themes';
  import { mode } from 'mode-watcher';

  async function handleManageSubscription() {
    try {
      const response = await fetch('/api/create-portal-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw error(response.status, response.statusText);
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (err) {
      console.error(err);
      toast.error('Failed to open billing portal', {
        description:
          'There was an issue accessing your billing settings. Please try again or contact support.',
      });
    }
  }

  function isActive(path: string) {
    return page.url.pathname === path;
  }
</script>

<!-- Secondary Navigation -->
<nav class="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
  <div class="container mx-auto px-4">
    <div class="flex h-16 items-center justify-between">
      <div class="flex items-center gap-4">
        <OrganizationSwitcher
          hidePersonal={true}
          afterCreateOrganizationUrl="/dashboard/team"
          afterSelectOrganizationUrl="/dashboard"
          afterLeaveOrganizationUrl="/dashboard"
          appearance={{
            baseTheme: $mode === 'dark' ? dark : neobrutalism,
            variables: {
              spacingUnit: '16px',
              borderRadius: '8px',
            },
            elements: {
              rootBox: 'flex',
              organizationSwitcherTrigger:
                'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-gray-500 dark:text-gray-400',
            },
          }}
        />
        <a
          href="/dashboard"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Overview
        </a>
        <a
          href="/dashboard/create"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/create')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Create
        </a>
        <a
          href="/dashboard/profile"
          class={cn(
            'text-sm hover:text-primary dark:hover:text-primary transition-colors',
            isActive('/dashboard/profile')
              ? 'text-primary font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Profile
        </a>
        <a
          href="/dashboard/releases"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/releases')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Releases
        </a>
        <a
          href="/dashboard/analytics"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/analytics')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Analytics
        </a>
      </div>
      <div class="flex items-center gap-4">
        <a
          href="/dashboard/team"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/team')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Team
        </a>
        <a
          href="/dashboard/account"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/account')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Account
        </a>
        <button
          onclick={handleManageSubscription}
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/billing')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Billing
        </button>
        <div class="h-4 w-px bg-gray-200 dark:bg-gray-700" />
        <span class="text-sm text-gray-600 dark:text-gray-400">
          Status:
          {#if page.data.hasActiveSubscription}
            <span
              class="ml-1 inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400"
            >
              Active
            </span>
          {:else}
            <span
              class="ml-1 inline-flex items-center rounded-full bg-red-50 px-2 py-1 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400"
            >
              Inactive
            </span>
            <a
              href="/subscribe"
              class="ml-2 inline-flex items-center rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
            >
              Enable Services
            </a>
          {/if}
        </span>
      </div>
    </div>
  </div>
</nav>

<div class="bg-gray-50 dark:bg-gray-900">
  <slot />
</div>
