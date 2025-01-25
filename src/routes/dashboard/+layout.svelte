<script lang="ts">
  import { page } from '$app/state';
  import { error } from '@sveltejs/kit';
  import { cn } from '$lib/utils';
  import { toast } from 'svelte-sonner';
  import { OrganizationSwitcher, useClerkContext } from 'svelte-clerk';
  import { slide } from 'svelte/transition';

  let { children } = $props();
  let isMenuOpen = $state(false);
  const { isLoaded } = $derived(useClerkContext());

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
</script>

<!-- Secondary Navigation -->
<nav class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
  <div class="container mx-auto px-4">
    <div class="flex h-8 items-center justify-between">
      <!-- Desktop Navigation -->
      <div class="hidden md:flex items-center gap-3">
        {#if !isLoaded}
          <div class="h-7 w-[180px] bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        {:else}
          <OrganizationSwitcher
            hidePersonal={true}
            createOrganizationUrl="/dashboard/create-artist"
            organizationProfileUrl="/dashboard/team"
            afterCreateOrganizationUrl="/dashboard/reload"
            afterSelectOrganizationUrl="/dashboard/reload"
            afterLeaveOrganizationUrl="/dashboard/reload"
          />
        {/if}
        <div class="h-4 w-px bg-gray-200 dark:bg-gray-700"></div>
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
        <a
          href="/dashboard/tracks"
          class={cn(
            'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors',
            isActive('/dashboard/tracks')
              ? 'text-indigo-600 dark:text-indigo-400 font-medium'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          Tracks
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
        {#if page.data.hasActiveSubscription}
          <span
            class="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400"
          >
            Active
          </span>
        {:else}
          <a
            href="/upgrade"
            class={cn(
              'text-sm transition-colors group',
              isActive('/upgrade')
                ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                : 'text-gray-500 dark:text-gray-400'
            )}
          >
            <div class="flex items-center gap-1 hover:text-indigo-600 dark:hover:text-indigo-400">
              Settings
              <svg
                class="w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
          </a>
        {/if}
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
          {#if !isLoaded}
            <div class="h-7 w-[180px] bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          {:else}
            <OrganizationSwitcher
              hidePersonal={true}
              createOrganizationUrl="/dashboard/create-artist"
              organizationProfileUrl="/dashboard/team"
              afterCreateOrganizationUrl="/dashboard/reload"
              afterSelectOrganizationUrl="/dashboard/reload"
              afterLeaveOrganizationUrl="/dashboard/reload"
            />
          {/if}
        </div>

        <!-- Status Indicator (visible on all screens) -->
        <div class="flex items-center gap-3">
          {#if page.data.hasActiveSubscription}
            <span
              class="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400"
            >
              Active
            </span>
          {:else}
            <a
              href="/upgrade"
              class={cn(
                'text-sm transition-colors group',
                isActive('/upgrade')
                  ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400'
              )}
            >
              <div class="flex items-center gap-1 hover:text-indigo-600 dark:hover:text-indigo-400">
                Settings
                <svg
                  class="w-4 h-4 text-gray-500 dark:text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
            </a>
          {/if}
        </div>
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
          href="/dashboard/tracks"
          class={cn(
            'block px-3 py-2 text-base font-medium rounded-md transition-colors',
            isActive('/dashboard/tracks')
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
              : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          Tracks
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
        {#if !page.data.hasActiveSubscription}
          <a
            href="/upgrade"
            class={cn(
              'block px-3 py-2 text-base font-medium rounded-md transition-colors',
              isActive('/upgrade')
                ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
            )}
          >
            <div class="flex items-center gap-1">
              Settings
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
          </a>
        {/if}
      </div>
    {/if}
  </div>
</nav>

<div class="bg-gray-50 dark:bg-gray-900">
  {@render children()}
</div>
