import { useState } from "react";
import { Search, Plus, Edit, Trash, Lock, Shield, Eye } from "lucide-react";
import { toast } from "sonner";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  scope: string;
  status: "active" | "inactive" | "pending";
  created_at: string;
}

const mockUsers: User[] = [
  {
    id: "USR-001",
    username: "john_doe",
    email: "john.doe@company.com",
    role: "SUP",
    scope: "Plant A",
    status: "active",
    created_at: "2024-01-15",
  },
  {
    id: "USR-002",
    username: "jane_smith",
    email: "jane.smith@company.com",
    role: "IEP",
    scope: "Plant A",
    status: "active",
    created_at: "2024-02-20",
  },
  {
    id: "USR-003",
    username: "bob_wilson",
    email: "bob.wilson@company.com",
    role: "QC",
    scope: "Plant B",
    status: "active",
    created_at: "2024-03-10",
  },
];

export function UserManagement() {
  const { t } = useI18n();
  const [users] = useState(mockUsers);
  const [searchValue, setSearchValue] = useState("");

  const filteredUsers = users.filter(
    (u) =>
      u.username.toLowerCase().includes(searchValue.toLowerCase()) ||
      u.email.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <GovernancePageShell
      title="User Management"
      subtitle="Manage user accounts, roles, and access scope assignments"
      phase="SHELL"
      bannerNote="User management and IAM workflows are not yet connected to backend. Backend authentication and authorization systems remain source of truth."
      actions={
        <button
          disabled
          onClick={() => toast.info("User creation requires backend workflow")}
          className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
          title="This action requires backend IAM workflow"
        >
          <Lock className="w-4 h-4" />
          Create User (Future)
        </button>
      }
    >
      {/* Filters & Summary */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by username or email..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full sm:w-80"
            />
          </div>
          <div className="text-sm text-gray-600">
            Total: <strong>{filteredUsers.length}</strong> users
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full min-w-[700px]">
          <thead className="bg-gray-50 border-b sticky top-0">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Username</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Email</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Role</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Scope</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Created</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user) => (
              <tr key={user.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium">{user.username}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                <td className="px-6 py-4 text-sm">
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 rounded border border-blue-200">
                    <Shield className="w-3 h-3" />
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.scope}</td>
                <td className="px-6 py-4 text-sm">
                  <span
                    className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                      user.status === "active"
                        ? "bg-green-50 text-green-700"
                        : user.status === "inactive"
                          ? "bg-gray-100 text-gray-600"
                          : "bg-yellow-50 text-yellow-700"
                    }`}
                  >
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.created_at}</td>
                <td className="px-6 py-4 text-sm">
                  <div className="flex items-center gap-2">
                    <button
                      disabled
                      aria-label="View user (requires backend IAM workflow)"
                      className="p-2 text-gray-400 cursor-not-allowed"
                      title="This action requires backend IAM workflow"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      disabled
                      aria-label="Edit user (requires backend IAM workflow)"
                      className="p-2 text-gray-400 cursor-not-allowed"
                      title="This action requires backend IAM workflow"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      disabled
                      aria-label="Delete user (requires backend IAM workflow)"
                      className="p-2 text-gray-400 cursor-not-allowed"
                      title="This action requires backend IAM workflow"
                    >
                      <Trash className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GovernancePageShell>
  );
}
