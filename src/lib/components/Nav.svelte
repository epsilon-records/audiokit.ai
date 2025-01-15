<script lang="ts">
  import { UserButton, SignedIn, SignedOut } from 'svelte-clerk';
  import { Menu, X } from 'svelte-hero-icons';
  import { fade, slide } from 'svelte/transition';

  let isOpen = $state(false);

  const toggleMenu = () => {
    isOpen = !isOpen;
  };

  // Close menu when clicking outside
  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (!target.closest('.mobile-menu') && !target.closest('.menu-button')) {
      isOpen = false;
    }
  };

  $effect(() => {
    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
    } else {
      document.removeEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<nav class="absolute top-0 w-full z-20">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center py-6">
      <a href="/" class="text-yellow-500 font-mono font-bold text-xl">EPSILON</a>

      <!-- Mobile menu button -->
      <button
        class="menu-button lg:hidden text-purple-500 hover:text-red-400 transition-colors"
        on:click={toggleMenu}
      >
        {#if isOpen}
          <X class="w-6 h-6" />
        {:else}
          <Menu class="w-6 h-6" />
        {/if}
      </button>

      <!-- Desktop menu -->
      <ul class="hidden lg:flex gap-8 text-lg">
        <li>
          <a href="/distribution" class="hover:text-red-400 text-purple-500 transition-colors"
            >Distribution</a
          >
        </li>
        <li>
          <a href="/releases" class="hover:text-red-400 text-purple-500 transition-colors"
            >Releases</a
          >
        </li>
        <li>
          <a href="/artists" class="hover:text-red-400 text-purple-500 transition-colors">Artists</a
          >
        </li>
        <SignedOut>
          <li>
            <a
              href="/sign-in"
              class="btn btn-sm btn-primary text-lg hover:text-red-400 text-white transition-colors"
              >Login</a
            >
          </li>
          <li>
            <a
              href="/sign-up"
              class="btn btn-sm btn-secondary text-lg hover:text-green-300 text-white transition-colors"
              >Register</a
            >
          </li>
        </SignedOut>
        <SignedIn>
          <li>
            <a href="/dashboard" class="hover:text-red-400 text-purple-500 transition-colors"
              >Dashboard</a
            >
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
        class="mobile-menu lg:hidden absolute top-20 left-0 right-0 bg-black/95 border-t border-purple-500"
        transition:slide={{ duration: 200 }}
      >
        <ul class="container mx-auto px-4 py-4 flex flex-col gap-4">
          <li>
            <a
              href="/distribution"
              class="block py-2 hover:text-red-400 text-purple-500 transition-colors"
              on:click={() => (isOpen = false)}>Distribution</a
            >
          </li>
          <li>
            <a
              href="/releases"
              class="block py-2 hover:text-red-400 text-purple-500 transition-colors"
              on:click={() => (isOpen = false)}>Releases</a
            >
          </li>
          <li>
            <a
              href="/artists"
              class="block py-2 hover:text-red-400 text-purple-500 transition-colors"
              on:click={() => (isOpen = false)}>Artists</a
            >
          </li>
          <SignedOut>
            <li>
              <a
                href="/sign-in"
                class="block py-2 btn btn-sm btn-primary text-lg hover:text-red-400 text-white transition-colors"
                on:click={() => (isOpen = false)}>Login</a
              >
            </li>
            <li>
              <a
                href="/sign-up"
                class="block py-2 btn btn-sm btn-secondary text-lg hover:text-green-300 text-white transition-colors"
                on:click={() => (isOpen = false)}>Register</a
              >
            </li>
          </SignedOut>
          <SignedIn>
            <li>
              <a
                href="/dashboard"
                class="block py-2 hover:text-red-400 text-purple-500 transition-colors"
                on:click={() => (isOpen = false)}>Dashboard</a
              >
            </li>
            <li class="py-2">
              <UserButton afterSignOutUrl="/" />
            </li>
          </SignedIn>
        </ul>
      </div>
    {/if}
  </div>
</nav>
