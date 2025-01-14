<script lang="ts">
  import type { PageData } from '../security copy/$types';

  let { data }: { data: PageData } = $props();
</script>

<div class="flex flex-col w-full h-full">
  <form action="?/update" method="POST" class="flex flex-col space-y-2 w-full">
    <h3 class="text-2xl font-medium">Update Profile</h3>
    <div class="form-control w-full max-w-lg">
      <label for="avatar" class="label font-medium pb-1">Profile Picture</label>
    </div>
    <label for="avatar" class="avatar w-32 rounded-full">
      <div class="w-32 rounded-full">
        <img src="https://placeimg.com/80/80/people" alt="user avatar" />
      </div>
    </label>
  </form>
</div>
