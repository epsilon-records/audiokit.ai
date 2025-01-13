<script lang="ts">
import { pb } from '$lib/pocketbase';

let { artist } = $props<{ artist: any }>();

const imageUrl = $derived(
  Array.isArray(artist.artist_photo) && artist.artist_photo.length > 0 
    ? pb.files.getURL(artist, artist.artist_photo[0])
    : '/default-artist.jpg'
);
</script>

<div class="relative aspect-square overflow-hidden border border-[#00ff00]">
  <img 
    src={imageUrl} 
    alt={artist.stage_name}
    class="w-full h-full object-cover"
  />
</div> 