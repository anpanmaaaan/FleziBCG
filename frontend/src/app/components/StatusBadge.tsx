import { ReactNode } from "react";

interface StatusBadgeProps {
  children?: ReactNode;
  variant?: "success" | "warning" | "error" | "info" | "neutral" | "purple" | "cyan";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function StatusBadge({ children, variant = "neutral", size = "md", className = "" }: StatusBadgeProps) {
  const variants = {
    success: "bg-green-100 text-green-800 border-green-200",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    error: "bg-red-100 text-red-800 border-red-200",
    info: "bg-blue-100 text-blue-800 border-blue-200",
    neutral: "bg-gray-100 text-gray-800 border-gray-200",
    purple: "bg-purple-100 text-purple-800 border-purple-200",
    cyan: "bg-cyan-100 text-cyan-800 border-cyan-200",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <span className={`inline-flex items-center font-medium rounded border ${variants[variant]} ${sizes[size]} ${className}`}>
      {children}
    </span>
  );
}