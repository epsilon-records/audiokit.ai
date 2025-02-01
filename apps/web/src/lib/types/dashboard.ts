export interface DashboardStats {
  instagramFollowers: number;
  weeklyGrowth: number;
  engagementRate: number;
}

export interface WidgetProps {
  title: string;
  value: number;
  change?: number;
  icon?: any;
}
