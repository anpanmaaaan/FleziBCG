import { useEffect, useState } from "react";
import { Search, Lock, Shield, UserCheck, UserX } from "lucide-react";
import { toast } from "sonner";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { iamApi } from "@/app/api/iamApi";
import type { UserLifecycleItem } from "@/app/api/iamApi";

export function UserManagement() {
  const { t } = useI18n();
  const [users, setUsers] = useState<UserLifecycleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchValue, setSearchValue] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [actingOn, setActingOn] = useState<string | null>(null);

  const loadUsers = (inactive: boolean) => {
    setLoading(true);
    iamApi
      .listUsers(inactive)
      .then((res) => setUsers(res.users))
      .catch(() => toast.error(t("userManagement.notice.failed_to_load_users")))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadUsers(includeInactive);
  }, [includeInactive]);

  const handleToggleActive = (user: UserLifecycleItem) => {
    setActingOn(user.user_id);
    const action = user.is_active ? iamApi.deactivateUser : iamApi.activateUser;
    action(user.user_id)
      .then(() => {
        toast.success(`User ${user.username} ${user.is_active ? "deactivated" : "activated"}.`);
        loadUsers(includeInactive);
      })
      .catch(() => toast.error(t("userManagement.notice.action_failed")))
      .finally(() => setActingOn(null));
  };

  const filteredUsers = users.filter(
    (u) =>
      u.username.toLowerCase().includes(searchValue.toLowerCase()) ||
      (u.email ?? "").toLowerCase().includes(searchValue.toLowerCase()) ||
      u.user_id.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <GovernancePageShell
      title={t("userManagement.tooltip.user_management")}
      subtitle={t("userManagement.tooltip.manage_user_accounts_and_lifecycle_actio")}
      phase="PARTIAL"
      bannerNote="User list is live from the backend IAM system. Create user and role/scope assignment require additional workflows."
      actions={
        <button
          disabled
          className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
          title={t("common.notice.iamRequired")}
        >
          <Lock className="w-4 h-4" />
          Create User (Future)
        </button>
      }
    >
      {/* Filters */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by username, email, or ID..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full sm:w-80"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="rounded"
            />
            Include inactive
          </label>
          <div className="text-sm text-gray-600">
            Total: <strong>{filteredUsers.length}</strong> users
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        {loading ? (
          <div className="p-8 text-center text-gray-400 text-sm">{t("userManagement.label.loading_users")}</div>
        ) : (
          <table className="w-full min-w-[600px]">
            <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("userManagement.label.user_id")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("userManagement.label.username")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("userManagement.label.email")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("common.status")}</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">{t("userManagement.label.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400 text-sm">
                    No users found.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.user_id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-xs font-mono text-gray-500">{user.user_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium flex items-center gap-1">
                      <Shield className="w-3 h-3 text-blue-400" />
                      {user.username}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{user.email ?? "—"}</td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                          user.is_active
                            ? "bg-green-50 text-green-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleToggleActive(user)}
                        disabled={actingOn === user.user_id}
                        className={`flex items-center gap-1 px-3 py-1 rounded text-xs font-medium transition-colors ${
                          user.is_active
                            ? "bg-red-50 text-red-700 hover:bg-red-100 border border-red-200"
                            : "bg-green-50 text-green-700 hover:bg-green-100 border border-green-200"
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {user.is_active ? (
                          <><UserX className="w-3 h-3" /> {t("userManagement.label.deactivate")}</>
                        ) : (
                          <><UserCheck className="w-3 h-3" /> {t("userManagement.label.activate")}</>
                        )}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </GovernancePageShell>
  );
}
