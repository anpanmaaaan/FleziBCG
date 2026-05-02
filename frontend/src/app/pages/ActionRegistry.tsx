import { useState } from "react";
import { Lock, Search } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface Action {
  id: string;
  code: string;
  domain: string;
  description: string;
  persona_group: string;
}

const mockActions: Action[] = [
  {
    id: "ACT-001",
    code: "station.execute.start",
    domain: "Station Execution",
    description: "Start operation at production station",
    persona_group: "OPR, SUP",
  },
  {
    id: "ACT-002",
    code: "station.execute.pause",
    domain: "Station Execution",
    description: "Pause active operation",
    persona_group: "OPR, SUP",
  },
  {
    id: "ACT-003",
    code: "station.execute.complete",
    domain: "Station Execution",
    description: "Mark operation as complete",
    persona_group: "OPR, SUP",
  },
  {
    id: "ACT-004",
    code: "quality.checkpoint.create",
    domain: "Quality Management",
    description: "Create quality checkpoint record",
    persona_group: "QC, SUP",
  },
  {
    id: "ACT-005",
    code: "quality.checkpoint.approve",
    domain: "Quality Management",
    description: "Approve quality checkpoint",
    persona_group: "QC",
  },
  {
    id: "ACT-006",
    code: "route.create",
    domain: "Master Data",
    description: "Create production route",
    persona_group: "IEP, PMG",
  },
];

export function ActionRegistry() {
  const { t } = useI18n();
  const [actions] = useState(mockActions);
  const [searchValue, setSearchValue] = useState("");

  const filteredActions = actions.filter(
    (a) =>
      a.code.toLowerCase().includes(searchValue.toLowerCase()) ||
      a.domain.toLowerCase().includes(searchValue.toLowerCase()) ||
      a.description.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <GovernancePageShell
      title="Action / Permission Registry"
      subtitle="System actions and their allowed personas"
      phase="SHELL"
      bannerNote="Action and permission registry is read-only visualization. Backend authorization system remains source of truth for allowed actions."
    >
      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search actions..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full"
          />
        </div>
      </div>

      {/* Actions Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full min-w-[560px]">
          <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Action Code</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Domain</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Description</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Allowed Personas</th>
              </tr>
            </thead>
            <tbody>
              {filteredActions.map((action) => (
                <tr key={action.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-mono text-gray-900">{action.code}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{action.domain}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{action.description}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className="inline-flex px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                      {action.persona_group}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      {/* Note */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
        <Lock className="inline w-4 h-4 mr-2" />
        This is a read-only registry. Backend IAM system defines actual action availability.
      </div>
    </GovernancePageShell>
  );
}
