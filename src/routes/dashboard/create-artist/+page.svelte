<script lang="ts">
  import { CreateOrganization } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';

  // Define a complete appearance configuration
  const clerkAppearance = {
    baseTheme: $mode === 'dark' ? dark : neobrutalism,
    variables: {
      // Spacing
      spacingUnit: '16px',

      // Colors
      colorPrimary: '#0E4FFF',
      colorBackground: '#ffffff',
      colorText: '#1F1F1F',
      colorDanger: '#FF4E4E',
      colorSuccess: '#22C55E',
      colorWarning: '#F59E0B',
      colorInputText: '#1F1F1F',
      colorInputBackground: '#F3F4F6',
      colorInputBorder: '#E5E7EB',

      // Typography
      fontFamily: 'ui-sans-serif, system-ui, sans-serif',
      fontSize: '16px',
      fontWeight: {
        normal: '400',
        medium: '500',
        bold: '600',
      },

      // Borders
      borderRadius: '8px',

      // Shadows
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    },
    elements: {
      // Form elements
      formButtonPrimary: {
        backgroundColor: '#0E4FFF',
        '&:hover': {
          backgroundColor: '#0036D9',
        },
      },
      formFieldInput: {
        borderColor: '#E5E7EB',
        '&:focus': {
          borderColor: '#0E4FFF',
          boxShadow: '0 0 0 3px rgba(14,79,255,0.1)',
        },
      },
      // Card styling
      card: {
        border: '1px solid #E5E7EB',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
        borderRadius: '12px',
      },
      // Header styling
      headerTitle: {
        fontSize: '24px',
        fontWeight: '600',
        color: '#1F1F1F',
      },
      headerSubtitle: {
        fontSize: '16px',
        color: '#6B7280',
      },
      // Footer styling
      footer: {
        fontSize: '14px',
        color: '#6B7280',
      },
      // Alternative action links
      footerActionLink: {
        color: '#0E4FFF',
        '&:hover': {
          textDecoration: 'underline',
        },
      },
      // Alert/Message styling
      alert: {
        backgroundColor: '#FEF3C7',
        borderColor: '#F59E0B',
        color: '#92400E',
      },
    },
  };
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Manage New Artist</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Create an organization to manage your artist profile, team members, and releases.
    </p>
  </div>

  <div class="flex justify-center">
    <div class="rounded-lg p-2 mt-4 mb-8">
      <CreateOrganization appearance={clerkAppearance} />
    </div>
  </div>
</div>
