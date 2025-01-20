<script lang="ts">
  import { page } from '$app/state';
  import { error } from '@sveltejs/kit';
  import { cn } from '$lib/utils';
  import { toast } from 'svelte-sonner';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { slide } from 'svelte/transition';
  import { createClerkNavAppearance } from '$lib/config/clerk';

  let isMenuOpen = $state(false);
  let navAppearance = $state(createClerkNavAppearance($mode === 'dark' ? 'dark' : 'light'));

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
      toast.error('An error occurred', {
        description: 'Please try again or contact support',
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

  // Update appearance when mode changes
  $effect(() => {
    navAppearance = createClerkNavAppearance($mode === 'dark' ? 'dark' : 'light');
  });
</script>

<!-- Secondary Navigation -->
<nav class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
  <div class="container mx-auto px-4">
    <div class="flex h-8 items-center justify-between">
      <!-- Desktop Navigation -->
      <div class="hidden md:flex items-center gap-3">
        <OrganizationSwitcher
          appearance={navAppearance}
          hidePersonal={true}
          afterCreateOrganizationUrl="/dashboard/redirect"
          afterSelectOrganizationUrl="/dashboard/redirect"
          afterLeaveOrganizationUrl="/dashboard/redirect"
        />
        <div class="h-4 w-px bg-gray-200 dark:bg-gray-700" />
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
      </div>
      <div class="hidden md:flex items-center gap-3">
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
              href="/join"
              class="ml-2 inline-flex items-center rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
            >
              Enable Services
            </a>
          {/if}
        </span>
      </div>

      <!-- Mobile Navigation -->
      <div class="md:hidden flex items-center justify-between w-full">
        <!-- Mobile Hamburger Button and Organization Switcher -->
        <div class="flex items-center gap-2">
          <button class="p-1" onclick={toggleMenu} aria-label="Toggle menu">
            <svg
              class="w-6 h-6 text-black dark:text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {#if isMenuOpen}
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M9 9l6 6m0-6l-6 6m12-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              {:else}
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
                />
              {/if}
            </svg>
          </button>
          <OrganizationSwitcher
            appearance={navAppearance}
            hidePersonal={true}
            afterCreateOrganizationUrl="/dashboard/redirect"
            afterSelectOrganizationUrl="/dashboard/redirect"
            afterLeaveOrganizationUrl="/dashboard/redirect"
          />
        </div>

        <!-- Status Indicator (visible on all screens) -->
        <span class="text-sm text-gray-600 dark:text-gray-400 flex items-center">
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
              href="/join"
              class="ml-2 inline-flex items-center rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
            >
              Enable Services
            </a>
          {/if}
        </span>
      </div>
    </div>

    <!-- Mobile Menu Panel -->
    {#if isMenuOpen}
      <div class="md:hidden py-2 space-y-1" transition:slide={{ duration: 200 }}>
        <a
          href="/dashboard"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
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
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
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
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/releases')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Releases
        </a>
        <a
          href="/dashboard/tools"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/tools')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Tools
        </a>
        <a
          href="/dashboard/analytics"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/analytics')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Analytics
        </a>
        <a
          href="/dashboard/team"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/team')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Team
        </a>
        <a
          href="/dashboard/create"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/create')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Create
        </a>
        <button
          onclick={handleManageSubscription}
          class={cn(
            'block w-full text-left px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/billing')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Billing
        </button>
        <a
          href="/dashboard/account"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/account')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Account
        </a>
      </div>
    {/if}
  </div>
</nav>

<div class="bg-gray-50 dark:bg-gray-900">
  <slot />
</div>
