/**
 * OEE Deep Dive - Mock Data Generation
 * 
 * This file contains all mock data generators for the OEE Deep Dive dashboard.
 * Replace these with real API calls when integrating with backend.
 */

import { format, subDays } from 'date-fns';

export interface OEETrendData {
  id?: string;
  date: string;
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  target: number;
}

export interface SixBigLoss {
  id?: string;
  name: string;
  minutes: number;
  impact: number;
  category: 'availability' | 'performance' | 'quality';
  trend: number;
}

export interface DowntimeData {
  id?: string;
  cause: string;
  minutes: number;
  cumulative: number;
  oeeImpact?: number;
}

export interface LineData {
  id?: string;
  line: string;
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  status: 'running' | 'reduced' | 'setup' | 'downtime' | 'offline';
  bottleneck?: boolean;
}

export interface OEEMetrics {
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  trends: {
    oee: number;
    availability: number;
    performance: number;
    quality: number;
  };
}

/**
 * Generate OEE trend data for the specified number of days
 */
export function generateOEETrendData(days: number = 30): OEETrendData[] {
  const today = new Date();
  const data: OEETrendData[] = [];
  
  for (let i = days - 1; i >= 0; i--) {
    const date = subDays(today, i);
    data.push({
      id: `trend-${i}`,
      date: format(date, 'MMM dd'),
      oee: 75 + Math.random() * 20,
      availability: 80 + Math.random() * 15,
      performance: 85 + Math.random() * 12,
      quality: 95 + Math.random() * 5,
      target: 95
    });
  }
  
  return data;
}

/**
 * Get Six Big Losses data
 * Sorted by impact (descending)
 */
export function getSixBigLossesData(): SixBigLoss[] {
  const losses: SixBigLoss[] = [
    { 
      id: 'loss-1',
      name: 'Equipment Failures', 
      minutes: 48, 
      impact: 5.2, 
      category: 'availability', 
      trend: 15 
    },
    { 
      id: 'loss-2',
      name: 'Setup & Adjustments', 
      minutes: 32, 
      impact: 3.5, 
      category: 'availability', 
      trend: -8 
    },
    { 
      id: 'loss-3',
      name: 'Reduced Speed', 
      minutes: 42, 
      impact: 4.6, 
      category: 'performance', 
      trend: -12 
    },
    { 
      id: 'loss-4',
      name: 'Small Stops & Idling', 
      minutes: 18, 
      impact: 2.0, 
      category: 'performance', 
      trend: 5 
    },
    { 
      id: 'loss-5',
      name: 'Startup Rejects', 
      minutes: 12, 
      impact: 0.8, 
      category: 'quality', 
      trend: 3 
    },
    { 
      id: 'loss-6',
      name: 'Production Rejects', 
      minutes: 8, 
      impact: 0.5, 
      category: 'quality', 
      trend: -2 
    }
  ];

  return losses.sort((a, b) => b.impact - a.impact);
}

/**
 * Get Downtime Pareto data
 * Includes cumulative percentage
 */
export function getDowntimeData(): DowntimeData[] {
  return [
    { id: 'dt-1', cause: 'Machine Breakdown', minutes: 180, cumulative: 36, oeeImpact: 5.2 },
    { id: 'dt-2', cause: 'Setup Time', minutes: 150, cumulative: 66, oeeImpact: 4.3 },
    { id: 'dt-3', cause: 'Changeover', minutes: 80, cumulative: 82, oeeImpact: 2.3 },
    { id: 'dt-4', cause: 'Tool Failure', minutes: 45, cumulative: 91, oeeImpact: 1.3 },
    { id: 'dt-5', cause: 'Maintenance', minutes: 25, cumulative: 96, oeeImpact: 0.7 },
    { id: 'dt-6', cause: 'Other', minutes: 20, cumulative: 100, oeeImpact: 0.6 }
  ];
}

/**
 * Get Line-by-Line comparison data
 */
export function getLineComparisonData(): LineData[] {
  return [
    { 
      id: 'line-1',
      line: 'Line 1', 
      oee: 87, 
      availability: 92, 
      performance: 95, 
      quality: 100, 
      status: 'running' 
    },
    { 
      id: 'line-2',
      line: 'Line 2', 
      oee: 92, 
      availability: 96, 
      performance: 96, 
      quality: 100, 
      status: 'running' 
    },
    { 
      id: 'line-3',
      line: 'Line 3', 
      oee: 45, 
      availability: 50, 
      performance: 90, 
      quality: 100, 
      status: 'downtime', 
      bottleneck: true 
    },
    { 
      id: 'line-4',
      line: 'Line 4', 
      oee: 78, 
      availability: 85, 
      performance: 92, 
      quality: 99, 
      status: 'reduced' 
    },
    { 
      id: 'line-5',
      line: 'Line 5', 
      oee: 85, 
      availability: 89, 
      performance: 96, 
      quality: 99, 
      status: 'running' 
    }
  ];
}

/**
 * Get current OEE metrics with trends
 */
export function getCurrentOEEMetrics(): OEEMetrics {
  return {
    oee: 85.2,
    availability: 90.5,
    performance: 94.8,
    quality: 99.3,
    trends: {
      oee: 3.2,
      availability: -2.1,
      performance: 5.8,
      quality: 0.5
    }
  };
}

/**
 * AI Insight: Top Loss Detection
 */
export function getTopLossInsight() {
  return {
    lossType: 'Equipment Failure',
    minutes: 48,
    impact: 5.2,
    confidence: 'High' as const,
    suggestedFocus: 'Line 3',
    reasons: [
      'Highest downtime contributor',
      'Recurring issue on Line 3',
      'Historical pattern detected'
    ]
  };
}

/**
 * AI Prediction: Next Shift Risk
 */
export function getNextShiftRiskPrediction() {
  return {
    risk: 'Medium' as 'Low' | 'Medium' | 'High',
    nextShiftTime: '2:00 PM - 10:00 PM',
    reasons: [
      'High downtime frequency',
      'Slow recovery after stops'
    ],
    recommendations: [
      'Pre-position maintenance team',
      'Check spare parts availability',
      'Review preventive maintenance schedule'
    ],
    confidence: 0.75
  };
}

/**
 * AI What-If: Improvement Estimation
 */
export function getWhatIfEstimation(lossType: string, reductionPercent: number) {
  const currentOEE = 85.2;
  const estimatedGain = (reductionPercent / 10) * 0.34; // Simplified calculation
  
  return {
    suggestion: `Reduce ${lossType} by ${reductionPercent}%`,
    projectedGain: estimatedGain.toFixed(1),
    newOEE: (currentOEE + estimatedGain).toFixed(1),
    confidence: 0.8
  };
}

/**
 * Calculate OEE from components
 */
export function calculateOEE(availability: number, performance: number, quality: number): number {
  return (availability / 100) * (performance / 100) * (quality / 100) * 100;
}

/**
 * Get OEE benchmark category
 */
export function getOEEBenchmark(oee: number): {
  category: string;
  color: string;
  description: string;
} {
  if (oee >= 85) {
    return {
      category: 'High Performance',
      color: 'green',
      description: 'Excellent performance, maintain current practices'
    };
  }
  if (oee >= 70) {
    return {
      category: 'Standard',
      color: 'blue',
      description: 'Meeting standard benchmarks, focus on incremental improvements'
    };
  }
  if (oee >= 60) {
    return {
      category: 'Below Standard',
      color: 'yellow',
      description: 'Performance below standard, identify top losses'
    };
  }
  if (oee >= 40) {
    return {
      category: 'Low Performance',
      color: 'orange',
      description: 'Action required, implement improvement projects'
    };
  }
  return {
    category: 'Critical',
    color: 'red',
    description: 'Urgent action needed, major issues present'
  };
}