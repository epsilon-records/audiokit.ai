<script lang="ts">
  import type { PageData } from '../security copy/$types';
  import { Icon, Pencil } from 'svelte-hero-icons';

  let { data }: { data: PageData } = $props();
</script>

<div class="flex flex-col w-full h-full">
  <form action="?/update" method="POST" class="flex flex-col space-y-2 w-full">
    <h3 class="text-2xl font-medium">Update Profile</h3>
    <div class="form-control w-full max-w-lg">
      <label for="avatar" class="label font-medium pb-1">
        <span class="label-text">Profile Picture</span>
      </label>
      <label for="avatar" class="avatar w-32 rounded-full hover:cursor-pointer">
        <label for="avatar" class="absolute -bottom-0.5 -right-0.5 hover:cursor-pointer">
          <Icon src={Pencil} class="w-4 h-4" />
        </label>
        <div class="w-32 rounded-full">
          <img src="https://placeimg.com/80/80/people" alt="user avatar" />
        </div>
      </label>
      <input type="file" name="avatar" id="avatar" value="" accept="image/*" hidden />
    </div>
  </form>
</div>
