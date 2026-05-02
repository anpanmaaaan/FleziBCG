import { useState } from "react";
import { Plus, Edit, Trash, Lock } from "lucide-react";
import { toast } from "sonner";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface Role {
  id: string;
  code: string;
  name: string;
  description: string;
  persona: string;
  user_count: number;
}

const mockRoles: Role[] = [
  {
    id: "ROLE-001",
    code: "OPR",
    name: "Operator",
    description: "Production line operator with station execution rights",
    persona: "OPR",
    user_count: 45,
  },
  {
    id: "ROLE-002",
    code: "SUP",
    name: "Supervisor",
    description: "Line supervisor with monitoring and override rights",
    persona: "SUP",
    user_count: 12,
  },
  {
    id: "ROLE-003",
    code: "IEP",
    name: "Industrial Engineer",
    description: "Industrial engineer with route and optimization rights",
    persona: "IEP",
    user_count: 8,
  },
  {
    id: "ROLE-004",
    code: "QC",
    name: "Quality Control",
    description: "Quality inspector with quality checkpoint rights",
    persona: "QC",
    user_count: 15,
  },
];

export function RoleManagement() {
  const { t } = useI18n();
  const [roles] = useState(mockRoles);

  return (
    <GovernancePageShell
      title="Role Management"
      subtitle="Manage roles, personas, and action permissions"
      phase="SHELL"
      bannerNote="Role and permission management is not yet connected to backend. Backend IAM system remains source of truth for role definitions and assignments."
      actions={
        <button
          disabled
          onClick={() => toast.info("Role creation requires backend workflow")}
          className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
          title="This action requires backend IAM workflow"
        >
          <Lock className="w-4 h-4" />
          Create Role (Future)
        </button>
      }
    >
      {/* Roles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.map((role) => (
            <div key={role.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{role.name}</h3>
                  <p className="text-xs text-gray-500">Code: {role.code}</p>
                </div>
                <span className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-medium">
                  {role.persona}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{role.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{role.user_count} users assigned</span>
                <div className="flex items-center gap-2">
                  <button
                    disabled
                    aria-label="Edit role (requires backend IAM workflow)"
                    className="p-1.5 text-gray-400 cursor-not-allowed"
                    title="This action requires backend IAM workflow"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    disabled
                    aria-label="Delete role (requires backend IAM workflow)"
                    className="p-1.5 text-gray-400 cursor-not-allowed"
                    title="This action requires backend IAM workflow"
                  >
                    <Trash className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
      </div>
    </GovernancePageShell>
  );
}
