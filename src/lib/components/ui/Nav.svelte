<script lang="ts">
  import UserButton from 'clerk-sveltekit/client/UserButton.svelte';
  import SignedIn from 'clerk-sveltekit/client/SignedIn.svelte';
  import SignedOut from 'clerk-sveltekit/client/SignedOut.svelte';
</script>

<nav class="absolute top-0 w-full z-20">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center py-6">
      <a href="/" class="text-white font-mono font-bold text-xl">EPSILON</a>
      <ul class="flex gap-8">
        <li>
          <a href="/releases" class="hover:text-red-400 text-white transition-colors">Releases</a>
        </li>
        <li>
          <a href="/artists" class="hover:text-red-400 text-white transition-colors">Artists</a>
        </li>
        <li>
          <a href="/events" class="hover:text-red-400 text-white transition-colors">Events</a>
        </li>
        <li><a href="/shop" class="hover:text-red-400 text-white transition-colors">Shop</a></li>
        <li>
          <a href="/contact" class="hover:text-red-400 text-white transition-colors">Contact</a>
        </li>
        <SignedIn>
          <div class="pb-1">
            <UserButton afterSignOutUrl="/" />
          </div>
        </SignedIn>
        <SignedOut>
          <li>
            <a href="/sign-in" class="hover:text-red-400 text-white transition-colors">Login</a>
          </li>
        </SignedOut>
      </ul>
    </div>
  </div>
</nav>
