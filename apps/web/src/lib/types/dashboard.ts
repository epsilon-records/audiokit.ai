/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

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
