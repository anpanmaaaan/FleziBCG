import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router";
import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  showBackButton?: boolean;
  onBackClick?: () => void;
  actions?: ReactNode;
  breadcrumb?: ReactNode;
}

export function PageHeader({ 
  title, 
  subtitle,
  showBackButton = false, 
  onBackClick,
  actions,
  breadcrumb
}: PageHeaderProps) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBackClick) {
      onBackClick();
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      {/* Breadcrumb if provided */}
      {breadcrumb && (
        <div className="mb-2 text-sm text-gray-500">
          {breadcrumb}
        </div>
      )}

      {/* Main header content */}
      <div className="flex items-center justify-between">
        {/* Left: Title section */}
        <div className="flex items-center gap-4">
          {showBackButton && (
            <button
              onClick={handleBack}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-medium">Back</span>
            </button>
          )}
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        {actions && (
          <div className="flex items-center gap-3">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
