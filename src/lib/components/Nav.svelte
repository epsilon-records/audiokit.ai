<script lang="ts">
  import { UserButton, SignedIn, SignedOut } from 'svelte-clerk';
</script>

<nav class="absolute top-0 w-full z-20">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center py-6">
      <a href="/" class="text-yellow-500 font-mono font-bold text-xl">EPSILON</a>
      <ul class="flex gap-8 text-lg">
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
          <!-- <li>
            <a href="/events" class="hover:text-red-400 text-purple-500 transition-colors">Events</a
            >
          </li>
          <li>
            <a href="/shop" class="hover:text-red-400 text-purple-500 transition-colors">Shop</a>
          </li>
          <li>
            <a href="/contact" class="hover:text-red-400 text-purple-500 transition-colors"
              >Contact</a
            >
          </li> -->
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
  </div>
</nav>
