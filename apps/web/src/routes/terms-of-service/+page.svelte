<script lang="ts">
  import { fly } from 'svelte/transition';
</script>

<svelte:head>
  <title>Terms of Service - AudioKit</title>
  <meta
    name="description"
    content="AudioKit's Terms of Service governing the use of our platform and services."
  />
</svelte:head>

<div class="relative">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="container max-w-4xl mx-auto px-4 py-16 relative z-10">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <div class="bg-white inline-block">
        <h1
          class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
        >
          Terms of Service
        </h1>
      </div>
      <p class="bg-white text-muted-foreground max-w-2xl mx-auto text-lg">
        Effective Date: January 26, 2025
      </p>
    </div>

    <div
      class="prose prose-lg max-w-none bg-white p-8 rounded-lg shadow-sm"
      in:fly={{ y: 20, duration: 600, delay: 200 }}
    >
      <p class="lead">
        Welcome to AudioKit! These Terms of Service ("Terms") govern your use of our website and
        platform (https://audiokit.ai) and all associated services, including any mobile
        applications and software provided by AudioKit. By accessing or using AudioKit, you agree to
        comply with and be bound by these Terms. Please read them carefully.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">1. Acceptance of Terms</h2>
      <p>
        By accessing or using our services, you agree to these Terms of Service and our Privacy
        Policy. If you do not agree, do not use the services.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">2. Services Provided</h2>
      <p>
        AudioKit offers a platform for music creators and industry professionals to access tools for
        music distribution, analytics, and other related services.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">3. User Registration</h2>
      <p>
        To use certain features, you must register for an account. You are responsible for
        maintaining the confidentiality of your account credentials. You agree to notify us
        immediately of any unauthorized use of your account.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">4. User Obligations</h2>
      <p>
        You agree not to use AudioKit for any unlawful purposes or in any manner that could damage,
        disable, overburden, or impair our services. You must not interfere with or disrupt any part
        of the platform.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">5. License</h2>
      <p>
        Subject to your compliance with these Terms, AudioKit grants you a limited, non-exclusive,
        non-transferable license to use our services solely for personal or business purposes.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">6. Content Ownership and Usage</h2>
      <p>
        You retain ownership of any content you upload to the platform. By submitting content, you
        grant AudioKit a non-exclusive, royalty-free license to use, distribute, and display such
        content solely to provide the services.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">7. Termination</h2>
      <p>
        We may suspend or terminate your access to AudioKit if you breach these Terms or if we
        discontinue providing the services. You may also terminate your account at any time.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">8. Disclaimers and Limitation of Liability</h2>
      <p>
        AudioKit provides the services on an "as-is" basis. We disclaim all warranties, express or
        implied, regarding the functionality, performance, or availability of the services. Our
        liability is limited to the maximum extent permitted by law.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">9. Governing Law</h2>
      <p>
        These Terms shall be governed by and construed in accordance with the laws of the United
        States.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">10. Changes to Terms</h2>
      <p>
        We may update these Terms of Service from time to time. When we do, we will post the updated
        version on this page. Please review these Terms periodically for any changes.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">11. Contact Information</h2>
      <p>
        If you have any questions about these Terms, please contact us at <a
          href="mailto:support@audiokit.ai"
          class="text-primary hover:underline">support@audiokit.ai</a
        >.
      </p>
    </div>
  </div>
</div>
