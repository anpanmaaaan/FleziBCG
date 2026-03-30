import { Link } from "react-router";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-2 text-sm text-gray-600 mb-4">
      <Link to="/dashboard" className="flex items-center gap-1 hover:text-blue-600 transition-colors">
        <Home className="w-4 h-4" />
        <span>Dashboard</span>
      </Link>
      
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          <ChevronRight className="w-4 h-4 text-gray-400" />
          {item.path && index !== items.length - 1 ? (
            <Link to={item.path} className="hover:text-blue-600 transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className={index === items.length - 1 ? "font-semibold text-gray-900" : ""}>
              {item.label}
            </span>
          )}
        </div>
      ))}
    </nav>
  );
}
