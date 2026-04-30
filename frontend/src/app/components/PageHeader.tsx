import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router";
import { ReactNode } from "react";
import { useI18n } from "@/app/i18n";

interface PageHeaderProps {
  title: React.ReactNode;
  subtitle?: string;
  showBackButton?: boolean;
  onBackClick?: () => void;
  actions?: ReactNode;
  breadcrumb?: ReactNode;
  children?: ReactNode;
}

export function PageHeader({ 
  title, 
  subtitle,
  showBackButton = false, 
  onBackClick,
  actions,
  breadcrumb,
  children
}: PageHeaderProps) {
  const navigate = useNavigate();
  const { t } = useI18n();

  const handleBack = () => {
    if (onBackClick) {
      onBackClick();
    } else {
      navigate(-1);
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      {breadcrumb && (
        <div className="mb-3 text-sm text-gray-500">
          {breadcrumb}
        </div>
      )}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex min-w-0 items-start gap-3 sm:gap-4">
          {showBackButton && (
            <button
              type="button"
              onClick={handleBack}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-50 hover:text-gray-900"
              aria-label={t("common.action.back")}
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="font-medium">{t("common.action.back")}</span>
            </button>
          )}

          <div className="min-w-0">
            <h1 className="text-2xl font-bold leading-tight text-gray-900">{title}</h1>
            {subtitle && (
              <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
            )}
          </div>
        </div>

        {(actions || children) && (
          <div className="flex items-center gap-2 self-start sm:self-auto">
            {actions}
            {children}
          </div>
        )}
      </div>
    </div>
  );
}
