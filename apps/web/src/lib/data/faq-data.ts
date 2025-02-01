import type { FAQData } from '$lib/types/faq';

export const faqData: FAQData = [
  {
    title: 'Getting Started 🚀',
    questions: [
      {
        question: 'How do I start distributing my music with AudioKit?',
        answer:
          "Sign up for an account, verify your email, and head to the dashboard. From there, you can create your first release by clicking 'New Release'. Our AI-powered system will guide you through the process, ensuring your release meets all platform requirements.",
      },
      {
        question: 'What makes AudioKit different from other distributors?',
        answer:
          'We combine traditional distribution with AI-powered tools and developer APIs. Our platform offers smart release timing, automated metadata optimization, and direct API access for building custom integrations - perfect for both artists and developers.',
      },
      {
        question: 'Is there a minimum payout threshold?',
        answer:
          'Yes, the minimum payout threshold is $50. Once your earnings reach this amount, you can request a payout through your dashboard. We support multiple payout methods including PayPal and bank transfer. 💸',
      },
    ],
  },
  {
    title: 'Technical Requirements 🎚️',
    questions: [
      {
        question: 'What audio formats do you accept?',
        answer:
          'We accept WAV files (16 or 24 bit, 44.1kHz or higher). Files must be uncompressed masters with at least -1dB headroom and no clipping.',
      },
      {
        question: 'What artwork specifications do you require?',
        answer:
          'Artwork should be 3000x3000 pixels minimum in JPG or PNG format, RGB color space, with no text within 100 pixels of the edges. Must be original artwork or licensed with proper rights.',
      },
      {
        question: 'Do you support Spatial Audio?',
        answer:
          'Yes! We support Spatial Audio (Dolby Atmos) distribution to Apple Music. This immersive audio format provides listeners with a revolutionary surround sound experience. Submit your Dolby Atmos masters through our platform to reach spatial audio-enabled devices. 🎵',
      },
    ],
  },
  {
    title: 'Distribution & Platforms 🌍',
    questions: [
      {
        question: 'Which platforms do you distribute to?',
        answer:
          'We distribute to all major platforms including Spotify, Apple Music, YouTube Music, Amazon Music, Tidal, Pandora, TikTok, Instagram, and many more. Our distribution network covers over 200 stores and services worldwide, ensuring your music reaches the largest possible audience.',
      },
      {
        question: 'How long does it take for my release to go live?',
        answer:
          'Standard delivery time is 3-5 business days. However, we recommend submitting releases at least 4 weeks in advance to ensure optimal placement and marketing opportunities. Our AI system will suggest the best release timing for maximum impact. ⏰',
      },
      {
        question: 'Can I choose different release dates for different platforms?',
        answer:
          'Yes! Our platform supports platform-specific release scheduling. This feature is particularly useful for coordinating marketing campaigns or taking advantage of platform-specific promotional opportunities. 📅',
      },
    ],
  },
  {
    title: 'API & Developer Features 👩‍💻',
    questions: [
      {
        question: 'How do I get started with the API?',
        answer:
          'Access our API by generating an API key in your dashboard. We provide comprehensive documentation, SDKs for popular languages, and GraphQL support for flexible integration options.',
      },
      {
        question: 'What can I build with the AudioKit API?',
        answer:
          'Our API enables you to create custom release workflows, automate metadata management, track analytics, and integrate with your existing tools. Popular uses include custom dashboards, automated release systems, and royalty tracking applications. 🛠️',
      },
      {
        question: 'Are there rate limits on the API?',
        answer: 'Yes, but they are generous. Contact support if you require assistance. ⚡',
      },
    ],
  },
  {
    title: 'Rights & Royalties 💰',
    questions: [
      {
        question: 'How do royalty payments work?',
        answer:
          'We collect royalties from all platforms and pay out monthly. Our smart royalty splitting system automatically distributes earnings to all rights holders based on your specified percentages. Track everything in real-time through your dashboard.',
      },
      {
        question: 'Do you provide ISRC and UPC codes?',
        answer:
          "Yes! We provide free ISRC codes for all tracks and UPC codes for all releases. Our system automatically generates and assigns these codes, and they're included in your distribution package. 🏷️",
      },
      {
        question: 'How do you handle cover songs and samples?',
        answer:
          "For cover songs, we handle mechanical licensing automatically through our partnerships. For samples, you'll need to clear them beforehand and provide documentation. Our AI system can help identify potential copyright issues before distribution. ⚖️",
      },
    ],
  },
  {
    title: 'Marketing & Promotion 📈',
    questions: [
      {
        question: 'What promotional tools do you offer?',
        answer:
          'We provide pre-save campaigns, smart release timing, social media integration, and AI-powered marketing suggestions. Our platform analyzes your audience data to recommend the best promotion strategies.',
      },
      {
        question: 'Can you help me get on playlists?',
        answer:
          "While we can't guarantee playlist placement, we provide tools to optimize your chances. Our AI system analyzes your music and suggests relevant playlists to pitch to, and we provide direct playlist submission tools for supported platforms. 🎯",
      },
      {
        question: 'Do you offer promotional services?',
        answer:
          'Yes! Weinclude access to our marketing team, press release distribution, and targeted advertising campaigns. We also provide AI-powered audience insights to help optimize your promotion strategy. 🚀',
      },
    ],
  },
];
