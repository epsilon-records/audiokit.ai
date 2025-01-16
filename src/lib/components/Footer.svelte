<script lang="ts">
  const currentYear = $derived(new Date().getFullYear());
</script>

<footer class="border-t">
  <div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
      <!-- About -->
      <div>
        <h3 class="font-bold mb-4">Epsilon Records</h3>
        <p class="text-muted-foreground text-sm">
          Underground acid techno label pushing boundaries since 2023.
        </p>
      </div>

      <!-- Quick Links -->
      <div>
        <h3 class="font-bold mb-4">Quick Links</h3>
        <ul class="space-y-2 text-sm">
          <li><a href="/artists" class="hover:underline">Artists</a></li>
          <li><a href="/releases" class="hover:underline">Releases</a></li>
          <li><a href="/events" class="hover:underline">Events</a></li>
          <li><a href="/shop" class="hover:underline">Shop</a></li>
          <li><a href="/faq" class="hover:underline">FAQ</a></li>
        </ul>
      </div>

      <!-- Connect -->
      <div>
        <h3 class="font-bold mb-4">Connect</h3>
        <ul class="space-y-2 text-sm">
          <li><a href="/contact" class="hover:underline">Contact</a></li>
          <li><a href="/demos" class="hover:underline">Demo Submission</a></li>
          <li><a href="/newsletter" class="hover:underline">Newsletter</a></li>
        </ul>
      </div>

      <!-- Social -->
      <div>
        <h3 class="font-bold mb-4">Follow Us</h3>
        <div class="flex space-x-4">
          <a href="https://instagram.com" class="hover:text-primary">Instagram</a>
          <a href="https://soundcloud.com" class="hover:text-primary">SoundCloud</a>
          <a href="https://bandcamp.com" class="hover:text-primary">Bandcamp</a>
        </div>
      </div>
    </div>

    <div class="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
      <p>© {currentYear} Epsilon Records. All rights reserved.</p>
    </div>
  </div>
</footer>
