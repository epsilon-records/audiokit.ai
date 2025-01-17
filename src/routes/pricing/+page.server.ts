import type { PageServerLoad } from './$types';

interface PricingTier {
  name: string;
  price: number;
  interval: 'month' | 'year';
  features: string[];
  highlighted?: boolean;
}

export const load: PageServerLoad = async () => {
  // In a real app, you might fetch this from a CMS or database
  const pricingTiers: PricingTier[] = [
    {
      name: 'Starter',
      price: 0,
      interval: 'month',
      features: [
        'Up to 1,000 API calls/month',
        'Basic support',
        'Core features',
        'Community access',
      ],
    },
    {
      name: 'Pro',
      price: 49,
      interval: 'month',
      highlighted: true,
      features: [
        'Up to 50,000 API calls/month',
        'Priority support',
        'Advanced features',
        'Team collaboration',
        'Custom integrations',
      ],
    },
    {
      name: 'Enterprise',
      price: 199,
      interval: 'month',
      features: [
        'Unlimited API calls',
        '24/7 dedicated support',
        'All features',
        'Custom solutions',
        'SLA guarantee',
        'Dedicated account manager',
      ],
    },
  ];

  return {
    pricingTiers,
  };
};
