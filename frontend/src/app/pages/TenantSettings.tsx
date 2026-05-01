import { useState } from "react";
import { Lock, Building2 } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
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
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="Tenant settings and configuration are managed by backend system. Frontend settings panel is visualization only."
      />
      <div className="flex-1 flex flex-col p-6">
        {/* Page header */}
        <div className="flex items-center gap-3 mb-6">
          <h1 className="text-2xl font-bold">Tenant Settings</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>

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
                <label className="block text-sm font-medium text-gray-700 mb-2">Tenant Name</label>
                <input
                  disabled
                  type="text"
                  value={mockTenant.name}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tenant Code</label>
                <input
                  disabled
                  type="text"
                  value={mockTenant.code}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email</label>
                <input
                  disabled
                  type="email"
                  value={mockTenant.contact_email}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Administrator</label>
                <input
                  disabled
                  type="text"
                  value={mockTenant.admin_user}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Created</label>
                <input
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
                title="Backend system manages tenant settings"
              >
                <Lock className="w-4 h-4" />
                Save Changes (Future)
              </button>
              <p className="text-sm text-gray-500">All changes must be made through backend tenant management.</p>
            </div>
          </div>
        </div>

        {/* Integration Info */}
        <div className="max-w-2xl p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Tenant Integrations</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• ERP System: SAP (not yet connected)</li>
            <li>• Message Queue: RabbitMQ (not yet configured)</li>
            <li>• Data Warehouse: PostgreSQL (not yet connected)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
