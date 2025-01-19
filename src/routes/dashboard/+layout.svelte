<script lang="ts">
  import { page } from '$app/state';
  import { error } from '@sveltejs/kit';
  import { cn } from '$lib/utils';
  import { toast } from 'svelte-sonner';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { neobrutalism, dark } from '@clerk/themes';
  import { mode } from 'mode-watcher';

  let isMenuOpen = $state(false);

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

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  // Close menu when route changes
  $effect(() => {
    if (page.url.pathname) {
      isMenuOpen = false;
    }
  });
</script>

<!-- Secondary Navigation -->
<nav class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
  <div class="container mx-auto px-4">
    <div class="flex h-8 items-center justify-between">
      <!-- Desktop Navigation -->
      <div class="hidden md:flex items-center gap-3">
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
          href="/dashboard/profile"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/profile')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
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
          href="/dashboard/tools"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/tools')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Tools
        </a>
      </div>
      <div class="hidden md:flex items-center gap-3">
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

      <!-- Mobile Hamburger Button -->
      <button class="md:hidden p-1" onclick={toggleMenu} aria-label="Toggle menu">
        <svg
          class="w-6 h-6 text-gray-500 dark:text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          {#if isMenuOpen}
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          {:else}
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          {/if}
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    {#if isMenuOpen}
      <div class="md:hidden py-2 space-y-1 bg-background border-2 border-black rounded-lg">
        <a
          href="/dashboard"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Overview
        </a>
        <a
          href="/dashboard/profile"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard/profile')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Profile
        </a>
        <a
          href="/dashboard/releases"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard/releases')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Releases
        </a>
        <a
          href="/dashboard/analytics"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard/analytics')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Analytics
        </a>
        <a
          href="/dashboard/create"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard/create')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Create
        </a>
        <a
          href="/dashboard/tools"
          class={cn(
            'block px-3 py-2 rounded-md text-base font-medium transition-colors',
            isActive('/dashboard/tools')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Tools
        </a>
        <div class="px-3 py-2">
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
    {/if}
  </div>
</nav>

<div class="bg-gray-50 dark:bg-gray-900">
  <slot />
</div>
