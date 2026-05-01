import { useState } from "react";
import { Lock, Plus, Layers } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface HierarchyNode {
  id: string;
  level: "tenant" | "plant" | "area" | "line" | "station" | "equipment";
  name: string;
  code: string;
  parent_id?: string;
  item_count?: number;
}

const mockHierarchy: HierarchyNode[] = [
  {
    id: "TEN-001",
    level: "tenant",
    name: "Company A",
    code: "COMP-A",
  },
  {
    id: "PLANT-001",
    level: "plant",
    name: "Plant A - Detroit",
    code: "PLANT-A",
    parent_id: "TEN-001",
    item_count: 3,
  },
  {
    id: "AREA-001",
    level: "area",
    name: "Assembly Area",
    code: "AREA-ASM",
    parent_id: "PLANT-001",
    item_count: 2,
  },
  {
    id: "LINE-001",
    level: "line",
    name: "Assembly Line 1",
    code: "LINE-ASM-01",
    parent_id: "AREA-001",
    item_count: 8,
  },
  {
    id: "ST-001",
    level: "station",
    name: "Welding Station 1",
    code: "ST-01",
    parent_id: "LINE-001",
  },
  {
    id: "EQP-001",
    level: "equipment",
    name: "Robotic Welder - FANUC M20",
    code: "WLD-01",
    parent_id: "ST-001",
  },
  {
    id: "AREA-002",
    level: "area",
    name: "Packaging Area",
    code: "AREA-PKG",
    parent_id: "PLANT-001",
    item_count: 1,
  },
  {
    id: "LINE-002",
    level: "line",
    name: "Packaging Line 1",
    code: "LINE-PKG-01",
    parent_id: "AREA-002",
    item_count: 4,
  },
  {
    id: "PLANT-002",
    level: "plant",
    name: "Plant B - Chicago",
    code: "PLANT-B",
    parent_id: "TEN-001",
    item_count: 2,
  },
];

const getLevelColor = (level: string) => {
  switch (level) {
    case "tenant":
      return "bg-purple-50 text-purple-700 border-purple-200";
    case "plant":
      return "bg-blue-50 text-blue-700 border-blue-200";
    case "area":
      return "bg-green-50 text-green-700 border-green-200";
    case "line":
      return "bg-yellow-50 text-yellow-700 border-yellow-200";
    case "station":
      return "bg-orange-50 text-orange-700 border-orange-200";
    case "equipment":
      return "bg-gray-50 text-gray-700 border-gray-200";
    default:
      return "bg-gray-50 text-gray-700 border-gray-200";
  }
};

const getLevelIndent = (level: string) => {
  const levels = ["tenant", "plant", "area", "line", "station", "equipment"];
  return levels.indexOf(level) * 24;
};

export function PlantHierarchy() {
  const { t } = useI18n();
  const [nodes] = useState(mockHierarchy);

  return (
    <GovernancePageShell
      title="Plant Hierarchy"
      subtitle="Organizational structure and asset hierarchy"
      phase="SHELL"
      bannerNote="Plant hierarchy structure is managed by backend master data system. Frontend hierarchy visualization is read-only."
      actions={
        <button
          disabled
          className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
          title="Backend master data system manages hierarchy"
        >
          <Lock className="w-4 h-4" />
          Add Node (Future)
        </button>
      }
    >
      {/* Hierarchy info */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded flex items-start gap-3">
        <Layers className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-blue-700">
          <strong>Hierarchy Structure:</strong> Tenant → Plant → Area → Line → Station → Equipment
        </div>
      </div>

      {/* Hierarchy Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Code</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Type</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Items</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockHierarchy.map((node) => (
                <tr key={node.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">
                    <div style={{ marginLeft: `${getLevelIndent(node.level)}px` }} className="flex items-center gap-2">
                      {node.level !== "equipment" && <Layers className="w-4 h-4 text-gray-400" />}
                      <span className="font-medium text-gray-900">{node.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-mono text-gray-600">{node.code}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex px-2 py-1 rounded text-xs font-medium border ${getLevelColor(node.level)}`}>
                      {node.level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{node.item_count || "-"}</td>
                  <td className="px-6 py-4 text-sm flex items-center gap-2">
                    <button
                      disabled
                      className="p-1.5 text-gray-400 cursor-not-allowed"
                      title="Backend master data system manages hierarchy"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      {/* Backend notice */}
      <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded text-sm text-slate-700 flex items-start gap-2">
        <Lock className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <span>Hierarchy structure is defined and managed exclusively by backend master data system.</span>
      </div>
    </GovernancePageShell>
  );
}
