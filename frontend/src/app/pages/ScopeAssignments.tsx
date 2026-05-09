import { useState } from "react";
import { Lock, Layers } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface ScopeAssignment {
  id: string;
  user: string;
  role: string;
  tenant: string;
  plant: string;
  area?: string;
  line?: string;
  station?: string;
  assigned_at: string;
}

const mockAssignments: ScopeAssignment[] = [
  {
    id: "SCOPE-001",
    user: "john_doe",
    role: "SUP",
    tenant: "Company A",
    plant: "Plant A",
    area: "Assembly",
    line: "Line 1",
    station: "ST-01",
    assigned_at: "2024-01-15",
  },
  {
    id: "SCOPE-002",
    user: "jane_smith",
    role: "IEP",
    tenant: "Company A",
    plant: "Plant A",
    area: "Assembly",
    assigned_at: "2024-02-20",
  },
  {
    id: "SCOPE-003",
    user: "bob_wilson",
    role: "QC",
    tenant: "Company A",
    plant: "Plant B",
    assigned_at: "2024-03-10",
  },
];

export function ScopeAssignments() {
  const { t } = useI18n();
  const [assignments] = useState(mockAssignments);

  return (
    <GovernancePageShell
      title={t("scopeAssignments.tooltip.scope_assignments")}
      subtitle={t("scopeAssignments.tooltip.user_role_scope_hierarchy_assignments")}
      phase="SHELL"
      bannerNote="Scope assignment is not yet connected to backend. Backend tenant isolation and RBAC system remains source of truth for user scope."
    >
      {/* Info box */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded flex items-start gap-3">
        <Layers className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-blue-700">
          <strong>{t("scopeAssignments.label.scope_hierarchy")}</strong> Tenant → Plant → Area → Line → Station → Equipment
        </div>
      </div>

      {/* Assignments Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full min-w-[800px]">
          <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.user")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.role")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.tenant")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.plant")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.area")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.line")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.station")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("scopeAssignments.label.assigned")}</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((assignment) => (
                <tr key={assignment.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{assignment.user}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{assignment.role}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.tenant}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.plant}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.area || "-"}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.line || "-"}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.station || "-"}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{assignment.assigned_at}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Backend notice */}
      <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded text-sm text-amber-700 flex items-start gap-2">
        <Lock className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <span>{t("scopeAssignments.label.scope_assignments_are_managed_by_backend")}</span>
      </div>
    </GovernancePageShell>
  );
}
