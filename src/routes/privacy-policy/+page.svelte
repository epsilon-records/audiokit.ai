<script lang="ts">
  import { fly, fade } from 'svelte/transition';
</script>

<svelte:head>
  <title>Privacy Policy - AudioKit</title>
  <meta
    name="description"
    content="AudioKit's privacy policy explaining how we collect, use, and protect your personal information."
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
          Privacy Policy
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
        At AudioKit, we are committed to protecting your privacy. This Privacy Policy explains how
        we collect, use, and safeguard your personal data when you use our services.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">1. Information We Collect</h2>
      <p>We may collect the following types of information:</p>
      <ul class="list-disc pl-6">
        <li>
          <strong>Personal Information:</strong> Name, email address, billing information, and other
          details you provide during registration.
        </li>
        <li>
          <strong>Usage Data:</strong> Information about how you interact with our platform, including
          device data, IP addresses, and browsing activity.
        </li>
      </ul>

      <h2 class="text-2xl font-bold mt-8 mb-4">2. How We Use Your Information</h2>
      <p>We use the information we collect for the following purposes:</p>
      <ul class="list-disc pl-6">
        <li>To provide, maintain, and improve our services.</li>
        <li>To communicate with you regarding your account, updates, and promotional offers.</li>
        <li>To analyze usage trends and improve the user experience.</li>
        <li>To comply with legal obligations.</li>
      </ul>

      <h2 class="text-2xl font-bold mt-8 mb-4">3. Data Sharing</h2>
      <p>
        We do not sell your personal data. However, we may share your information in the following
        circumstances:
      </p>
      <ul class="list-disc pl-6">
        <li>
          <strong>Service Providers:</strong> We may share information with third-party service providers
          who assist in operating our platform.
        </li>
        <li>
          <strong>Legal Compliance:</strong> We may disclose information if required by law or in response
          to legal requests.
        </li>
      </ul>

      <h2 class="text-2xl font-bold mt-8 mb-4">4. Data Security</h2>
      <p>
        We take reasonable steps to protect your information. However, no method of transmission
        over the internet or electronic storage is 100% secure, and we cannot guarantee absolute
        security.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">5. Your Data Rights</h2>
      <p>You have the right to:</p>
      <ul class="list-disc pl-6">
        <li>Access the personal data we hold about you.</li>
        <li>Correct or update your information.</li>
        <li>Request the deletion of your data, subject to certain limitations.</li>
        <li>Opt-out of receiving marketing communications.</li>
      </ul>
      <p>
        To exercise your rights, contact us at <a
          href="mailto:support@audiokit.ai"
          class="text-primary hover:underline">support@audiokit.ai</a
        >.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">6. Cookies and Tracking Technologies</h2>
      <p>
        We use cookies and similar technologies to track activity on our platform and enhance user
        experience. You can control cookie settings through your browser.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">7. International Data Transfers</h2>
      <p>
        If you are located outside of the United States, your personal data may be transferred to
        and processed in the United States. By using our services, you consent to such transfers.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">8. Children's Privacy</h2>
      <p>
        Our services are not intended for individuals under the age of 13, and we do not knowingly
        collect personal information from children. If you believe we have inadvertently collected
        such information, please contact us immediately.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">9. Changes to This Privacy Policy</h2>
      <p>
        We may update this Privacy Policy from time to time. Any changes will be posted on this page
        with an updated effective date. Please review this Privacy Policy periodically.
      </p>

      <h2 class="text-2xl font-bold mt-8 mb-4">10. Contact Us</h2>
      <p>
        If you have any questions or concerns about this Privacy Policy, please contact us at <a
          href="mailto:support@audiokit.ai"
          class="text-primary hover:underline">support@audiokit.ai</a
        >.
      </p>
    </div>
  </div>
</div>
