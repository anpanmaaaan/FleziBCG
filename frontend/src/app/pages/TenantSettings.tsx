import { useState } from "react";
import { Lock, Building2 } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface TenantInfo {
  id: string;
  name: string;
  code: string;
  contact_email: string;
  admin_user: string;
  status: string;
  created_at: string;
}

const mockTenant: TenantInfo = {
  id: "TEN-001",
  name: "Company A Manufacturing",
  code: "COMP-A",
  contact_email: "admin@company-a.com",
  admin_user: "admin_user",
  status: "active",
  created_at: "2024-01-01",
};

export function TenantSettings() {
  const { t } = useI18n();

  return (
    <GovernancePageShell
      title={t("tenantSettings.tooltip.tenant_settings")}
      subtitle={t("tenantSettings.tooltip.tenant_configuration_and_organization_me")}
      phase="SHELL"
      bannerNote="Tenant settings and configuration are managed by backend system. Frontend settings panel is visualization only."
    >

      {/* Tenant Profile Card */}
      <div className="max-w-2xl mb-6">
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{mockTenant.name}</h2>
                  <p className="text-sm text-gray-500">{mockTenant.code}</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium">
                {mockTenant.status}
              </span>
            </div>

            {/* Settings Fields */}
            <div className="space-y-4">
              <div>
                <label htmlFor="tenant-name" className="block text-sm font-medium text-gray-700 mb-2">{t("tenantSettings.label.tenant_name")}</label>
                <input
                  id="tenant-name"
                  disabled
                  type="text"
                  value={mockTenant.name}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label htmlFor="tenant-code" className="block text-sm font-medium text-gray-700 mb-2">{t("tenantSettings.label.tenant_code")}</label>
                <input
                  id="tenant-code"
                  disabled
                  type="text"
                  value={mockTenant.code}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label htmlFor="tenant-email" className="block text-sm font-medium text-gray-700 mb-2">{t("tenantSettings.label.contact_email")}</label>
                <input
                  id="tenant-email"
                  disabled
                  type="email"
                  value={mockTenant.contact_email}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label htmlFor="tenant-admin" className="block text-sm font-medium text-gray-700 mb-2">{t("tenantSettings.label.administrator")}</label>
                <input
                  id="tenant-admin"
                  disabled
                  type="text"
                  value={mockTenant.admin_user}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label htmlFor="tenant-created" className="block text-sm font-medium text-gray-700 mb-2">{t("tenantSettings.label.created")}</label>
                <input
                  id="tenant-created"
                  disabled
                  type="text"
                  value={mockTenant.created_at}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>
            </div>

            {/* Action buttons */}
            <div className="mt-6 flex items-center gap-3">
              <button
                disabled
                className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
                title={t("common.notice.tenantLocked")}
              >
                <Lock className="w-4 h-4" />
                Save Changes (Future)
              </button>
              <p className="text-sm text-gray-500">{t("tenantSettings.label.all_changes_must_be_made_through_backend")}</p>
            </div>
          </div>
        </div>

      {/* Integration Info */}
      <div className="max-w-2xl p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">{t("tenantSettings.label.tenant_integrations")}</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>{t("tenantSettings.label._erp_system_sap_not_yet_connected")}</li>
          <li>{t("tenantSettings.label._message_queue_rabbitmq_not_yet_configur")}</li>
          <li>{t("tenantSettings.label._data_warehouse_postgresql_not_yet_conne")}</li>
        </ul>
      </div>
    </GovernancePageShell>
  );
}
