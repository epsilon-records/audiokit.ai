<script lang="ts">
  import { UserButton, SignedIn, SignedOut } from 'svelte-clerk';
  import { Icon, Bars4, XMark } from 'svelte-hero-icons';
  import { slide } from 'svelte/transition';
  import { page } from '$app/state';
  import { cn } from '$lib/utils';
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
    return page.url.pathname.startsWith(path);
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
      </div>

      <!-- Mobile menu button -->
      <div class="lg:hidden">
        <button
          bind:this={buttonRef}
          class="menu-button text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors"
          onclick={toggleMenu}
          aria-expanded={isOpen}
          aria-label="Toggle menu"
        >
          <Icon src={isOpen ? XMark : Bars4} class="w-6 h-6" />
        </button>
      </div>

      <!-- Desktop menu -->
      <ul class="hidden lg:flex gap-8 text-lg">
        <SignedIn>
          <li class="pt-1">
            <a
              href="/dashboard"
              class="text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Dashboard
            </a>
          </li>
        </SignedIn>
        <SignedOut>
          <li class="pt-1">
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
          <li class="pt-1">
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
        </SignedOut>
        <li class="pt-1">
          <a
            href="/docs"
            class={cn(
              'transition-colors',
              isActive('/docs')
                ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
            )}
          >
            Docs
          </a>
        </li>
        <SignedIn>
          <li class="pt-1">
            <a
              href="/support"
              class={cn(
                'transition-colors',
                isActive('/support')
                  ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              )}
            >
              Support
            </a>
          </li>
        </SignedIn>
        <SignedOut>
          <li class="pt-1">
            <a
              href="/contact"
              class={cn(
                'transition-colors',
                isActive('/contact')
                  ? 'text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              )}
            >
              Contact
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
          <li class="pt-1">
            <ThemeSwitcher />
          </li>
          <li>
            <UserButton afterSignOutUrl="/" />
          </li>
        </SignedIn>
      </ul>
    </div>

    <!-- Mobile menu -->
    {#if isOpen}
      <div
        bind:this={menuRef}
        class="mobile-menu lg:hidden fixed top-16 left-4 right-4 bg-background border-2 border-black dark:border-gray-700 rounded-lg shadow-lg max-w-[1400px] mx-auto"
        transition:slide
      >
        <div class="py-2 space-y-1">
          <SignedIn>
            <a
              href="/dashboard"
              class={cn(
                'block px-6 py-2 text-base font-medium rounded-md transition-colors',
                isActive('/dashboard')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              onclick={closeMenu}
            >
              Dashboard
            </a>
          </SignedIn>
          <SignedOut>
            <a
              href="/services"
              class={cn(
                'block px-6 py-2 text-base font-medium rounded-md transition-colors',
                isActive('/services')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              onclick={closeMenu}
            >
              Services
            </a>
            <a
              href="/pricing"
              class={cn(
                'block px-6 py-2 text-base font-medium rounded-md transition-colors',
                isActive('/pricing')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              onclick={closeMenu}
            >
              Pricing
            </a>
          </SignedOut>
          <a
            href="/docs"
            class={cn(
              'block px-6 py-2 text-base font-medium rounded-md transition-colors',
              isActive('/docs')
                ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
            )}
            onclick={closeMenu}
          >
            Docs
          </a>
          <SignedIn>
            <a
              href="/support"
              class={cn(
                'block px-6 py-2 text-base font-medium rounded-md transition-colors',
                isActive('/support')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              onclick={closeMenu}
            >
              Support
            </a>
          </SignedIn>
          <SignedOut>
            <a
              href="/contact"
              class={cn(
                'block px-6 py-2 text-base font-medium rounded-md transition-colors',
                isActive('/contact')
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/50 dark:text-indigo-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              onclick={closeMenu}
            >
              Contact
            </a>
            <div class="px-4 py-2 space-y-1">
              <a
                href="/sign-in"
                class="w-full inline-flex justify-center items-center px-3 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors text-base font-medium"
                onclick={closeMenu}
              >
                Login
              </a>
              <a
                href="/sign-up"
                class="w-full inline-flex justify-center items-center px-3 py-2 rounded-md bg-gray-200 text-gray-900 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 transition-colors text-base font-medium"
                onclick={closeMenu}
              >
                Register
              </a>
            </div>
          </SignedOut>
          <SignedIn>
            <div class="px-4 py-2 space-y-1">
              <ThemeSwitcher />
              <div class="mt-2 px-2">
                <UserButton afterSignOutUrl="/" />
              </div>
            </div>
          </SignedIn>
        </div>
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
