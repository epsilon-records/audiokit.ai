<script lang="ts">
  import { UserButton, SignedIn, SignedOut, OrganizationSwitcher } from 'svelte-clerk';
  import { Icon, Bars3, XMark } from 'svelte-hero-icons';
  import { slide } from 'svelte/transition';
  import { page } from '$app/stores';
  import { cn } from '$lib/utils';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
  import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';

  let isOpen = $state(false);
  let menuRef = $state<HTMLDivElement | null>(null);
  let buttonRef = $state<HTMLButtonElement | null>(null);

  // Close menu when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (
      isOpen &&
      menuRef &&
      buttonRef &&
      !menuRef.contains(target) &&
      !buttonRef.contains(target)
    ) {
      isOpen = false;
    }
  }

  // Add click outside listener
  $effect(() => {
    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  });

  function toggleMenu() {
    isOpen = !isOpen;
  }

  function closeMenu() {
    isOpen = false;
  }

  function isActive(path: string) {
    return $page.url.pathname.startsWith(path);
  }
</script>

<nav
  class="fixed top-0 w-full z-50 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b border-gray-200 dark:border-gray-700 dark:bg-gray-800/95 h-16"
>
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center py-4">
      <div class="flex items-center gap-4">
        <a href="/" class="flex items-center gap-2">
          <img src="/logo.png" alt="AudioKit Logo" class="h-8 w-8 logo-image" />
          <span
            class="text-indigo-600 dark:text-indigo-400 font-mono font-bold text-xl hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors"
          >
            AudioKit
          </span>
        </a>
        <SignedIn>
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
                organizationSwitcherTrigger:
                  'text-sm hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-gray-500 dark:text-gray-400',
              },
            }}
          />
        </SignedIn>
      </div>

      <!-- Mobile menu button -->
      <div class="pb-4 lg:hidden">
        <button
          bind:this={buttonRef}
          class="menu-button text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors"
          onclick={toggleMenu}
          aria-expanded={isOpen}
          aria-label="Toggle menu"
        >
          <Icon src={isOpen ? XMark : Bars3} class="w-6 h-6" />
        </button>
      </div>

      <!-- Desktop menu -->
      <ul class="hidden lg:flex gap-8 text-lg">
        <SignedIn>
          <li>
            <a
              href="/dashboard"
              class="text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Dashboard
            </a>
          </li>
        </SignedIn>
        <li>
          <a
            href="/docs"
            class="text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            Docs
          </a>
        </li>
        <SignedOut>
          <li>
            <a
              href="/services"
              class={cn(
                'transition-colors',
                isActive('/services')
                  ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              )}
            >
              Services
            </a>
          </li>
          <li>
            <a
              href="/pricing"
              class={cn(
                'transition-colors',
                isActive('/pricing')
                  ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              )}
            >
              Pricing
            </a>
          </li>
          <li>
            <a
              href="/sign-in"
              class="btn btn-sm btn-primary text-lg text-white hover:text-indigo-100 transition-colors"
              >Login</a
            >
          </li>
          <li>
            <a
              href="/sign-up"
              class="btn btn-sm btn-secondary text-lg text-white hover:text-indigo-100 transition-colors"
              >Register</a
            >
          </li>
        </SignedOut>
        <SignedIn>
          <li>
            <ThemeSwitcher />
          </li>
          <li>
            <UserButton
              afterSignOutUrl="/"
              appearance={{
                baseTheme: $mode === 'dark' ? dark : neobrutalism,
                variables: {
                  spacingUnit: '16px',
                  borderRadius: '8px',
                },
              }}
            />
          </li>
        </SignedIn>
      </ul>
    </div>

    <!-- Mobile menu -->
    {#if isOpen}
      <div
        bind:this={menuRef}
        class="mobile-menu lg:hidden fixed top-16 right-0 w-64 h-[calc(100vh-4rem)] bg-white/95 dark:bg-gray-800/95 border-l border-gray-200 dark:border-gray-700 overflow-y-auto"
        transition:slide={{ duration: 200, axis: 'x' }}
      >
        <ul class="container mx-auto px-4 py-4 flex flex-col gap-4">
          <SignedIn>
            <li>
              <a
                href="/dashboard"
                class="block py-2 text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onclick={closeMenu}
              >
                Dashboard
              </a>
            </li>
          </SignedIn>
          <li>
            <a
              href="/docs"
              class="block py-2 text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              onclick={closeMenu}
            >
              Docs
            </a>
          </li>
          <SignedOut>
            <li>
              <a
                href="/services"
                class="block py-2 text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onclick={closeMenu}
              >
                Services
              </a>
            </li>
            <li>
              <a
                href="/pricing"
                class="block py-2 text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onclick={closeMenu}
              >
                Pricing
              </a>
            </li>
            <li>
              <a
                href="/sign-in"
                class="block py-2 btn btn-sm btn-primary text-lg text-white hover:text-indigo-100 transition-colors"
                onclick={closeMenu}
              >
                Login
              </a>
            </li>
            <li>
              <a
                href="/sign-up"
                class="block py-2 btn btn-sm btn-secondary text-lg text-white hover:text-indigo-100 transition-colors"
                onclick={closeMenu}
              >
                Register
              </a>
            </li>
          </SignedOut>
          <SignedIn>
            <li>
              <ThemeSwitcher />
            </li>
            <li class="px-2">
              <UserButton
                afterSignOutUrl="/"
                appearance={{
                  baseTheme: $mode === 'dark' ? dark : neobrutalism,
                  variables: {
                    spacingUnit: '16px',
                    borderRadius: '8px',
                  },
                }}
              />
            </li>
          </SignedIn>
        </ul>
      </div>
    {/if}
  </div>
</nav>

<style>
  @keyframes sway {
    0%,
    100% {
      transform: rotate(-5deg);
    }
    50% {
      transform: rotate(5deg);
    }
  }

  .logo-image {
    transition: transform 0.3s ease;
  }

  .logo-image:hover {
    animation: sway 1s ease-in-out infinite;
  }
</style>
