import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

type ColorVariant = "blue" | "green" | "purple" | "orange" | "yellow" | "red" | "gray" | "cyan";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  color?: ColorVariant;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export function StatsCard({ title, value, icon: Icon, color = "blue", subtitle, trend }: StatsCardProps) {
  const colorClasses = {
    blue: {
      bg: "from-blue-50 to-blue-100",
      border: "border-blue-200",
      text: "text-blue-600",
      valueText: "text-blue-800",
      iconBg: "bg-blue-500",
    },
    green: {
      bg: "from-green-50 to-green-100",
      border: "border-green-200",
      text: "text-green-600",
      valueText: "text-green-800",
      iconBg: "bg-green-500",
    },
    purple: {
      bg: "from-purple-50 to-purple-100",
      border: "border-purple-200",
      text: "text-purple-600",
      valueText: "text-purple-800",
      iconBg: "bg-purple-500",
    },
    orange: {
      bg: "from-orange-50 to-orange-100",
      border: "border-orange-200",
      text: "text-orange-600",
      valueText: "text-orange-800",
      iconBg: "bg-orange-500",
    },
    yellow: {
      bg: "from-yellow-50 to-yellow-100",
      border: "border-yellow-200",
      text: "text-yellow-700",
      valueText: "text-yellow-800",
      iconBg: "bg-yellow-500",
    },
    red: {
      bg: "from-red-50 to-red-100",
      border: "border-red-200",
      text: "text-red-600",
      valueText: "text-red-800",
      iconBg: "bg-red-500",
    },
    gray: {
      bg: "from-gray-50 to-gray-100",
      border: "border-gray-200",
      text: "text-gray-600",
      valueText: "text-gray-800",
      iconBg: "bg-gray-500",
    },
    cyan: {
      bg: "from-blue-50 to-blue-100",
      border: "border-blue-200",
      text: "text-blue-600",
      valueText: "text-blue-800",
      iconBg: "bg-blue-500",
    },
  };

  const classes = colorClasses[color];

  return (
    <div className={`bg-gradient-to-br ${classes.bg} p-4 rounded-lg border ${classes.border}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className={`text-sm font-medium ${classes.text}`}>{title}</div>
          <div className={`text-2xl font-bold ${classes.valueText} mt-1`}>{value}</div>
          {subtitle && (
            <div className="text-xs text-gray-600 mt-1">{subtitle}</div>
          )}
          {trend && (
            <div className={`text-xs mt-1 ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </div>
          )}
        </div>
        {Icon && (
          <Icon className={`w-8 h-8 ${classes.text}`} />
        )}
      </div>
    </div>
  );
}