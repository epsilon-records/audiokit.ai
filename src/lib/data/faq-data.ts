import type { FAQData } from '$lib/types/faq';

export const faqData: FAQData = [
  {
    title: "Distribution Basics",
    questions: [
      {
        question: "What digital platforms do you distribute to?",
        answer: "We distribute to all major platforms including Spotify, Apple Music, Beatport, Bandcamp, Amazon Music, YouTube Music, TIDAL, Traxsource, and 150+ other stores and streaming services worldwide."
      },
      {
        question: "How much does it cost to distribute through Epsilon Records?",
        answer: "We offer a simple pricing structure: $99 per year for unlimited digital releases. This includes unlimited tracks, worldwide distribution, custom release scheduling, ISRC code generation, content protection, and access to our analytics dashboard. Additional services like professional mastering ($49/track), promotional support ($199/release), and physical distribution (pricing varies) are available as optional add-ons. There are no hidden fees, and you can cancel your subscription at any time while your existing releases remain live."
      }
    ]
  },
  {
    title: "Royalties & Payments",
    questions: [
      {
        question: "How and when do I get paid?",
        answer: "Royalties are paid monthly when your balance reaches $50. Payments are made via bank transfer or PayPal, and you'll receive detailed analytics and earnings reports through your dashboard."
      },
      {
        question: "Do you take any commission from my royalties?",
        answer: "Yes, we take a 50% share of both royalties and publishing rights. This industry-standard split helps us invest in marketing, promotion, and label operations while ensuring our artists' success."
      }
    ]
  },
  {
    title: "Technical Requirements",
    questions: [
      {
        question: "What audio formats do you accept?",
        answer: "We accept WAV files (16 or 24 bit, 44.1kHz or higher). Files must be uncompressed masters with at least -1dB headroom and no clipping."
      },
      {
        question: "What artwork specifications do you require?",
        answer: "Artwork should be 3000x3000 pixels minimum in JPG or PNG format, RGB color space, with no text within 100 pixels of the edges. Must be original artwork or licensed with proper rights."
      }
    ]
  }
]; 