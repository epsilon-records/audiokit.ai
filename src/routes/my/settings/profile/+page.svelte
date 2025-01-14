<script lang="ts">
  import type { PageData } from '../security copy/$types';

  let { data }: { data: PageData } = $props();
</script>

<div class="flex flex-col w-full h-full">
  <form action="?/update" method="POST" class="flex flex-col space-y-2 w-full">
    <h3 class="text-2xl font-medium">Update Profile</h3>
  </form>
</div>
