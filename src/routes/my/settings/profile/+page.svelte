<script lang="ts">
  import { enhance } from '$app/forms';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import { Card, CardHeader, CardContent, CardFooter } from '$lib/components/ui/card';
  import { Label } from '$lib/components/ui/label';
  import { Button } from '$lib/components/ui/button';
  import { Textarea } from '$lib/components/ui/textarea';
  import ImageHandler from '$lib/components/ImageHandler.svelte';

  export let data;
  let loading = false;
</script>

<PageContainer title="Profile Settings">
  <Card>
    <form
      method="POST"
      action="?/updateProfile"
      enctype="multipart/form-data"
      use:enhance={() => {
        loading = true;
        return async ({ result }) => {
          loading = false;
          if (result.type === 'success') {
            // Handle success
          }
        };
      }}
    >
      <CardHeader>
        <h3 class="text-lg font-semibold">Profile Information</h3>
        <p class="text-sm text-muted-foreground">Update your profile information and avatar.</p>
      </CardHeader>

      <CardContent class="space-y-6">
        <div class="space-y-2">
          <Label for="avatar">Profile Picture</Label>
          <div class="flex items-center gap-4">
            <ImageHandler
              src={data.user?.avatar}
              alt={data.user?.name || 'Profile picture'}
              class="w-24 h-24 rounded-full"
            />
            <input
              type="file"
              id="avatar"
              name="avatar"
              accept="image/*"
              class="text-sm text-muted-foreground"
            />
          </div>
        </div>

        <div class="space-y-2">
          <Label for="name">Display Name</Label>
          <input
            type="text"
            id="name"
            name="name"
            value={data.user?.name || ''}
            class="w-full p-2 border rounded-md"
          />
        </div>

        <div class="space-y-2">
          <Label for="bio">Bio</Label>
          <Textarea
            id="bio"
            name="bio"
            value={data.user?.bio || ''}
            placeholder="Tell us about yourself"
            rows={4}
          />
        </div>
      </CardContent>

      <CardFooter>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save Changes'}
        </Button>
      </CardFooter>
    </form>
  </Card>
</PageContainer>
