export function AccessDeniedScreen() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-6">
      <div className="max-w-xl w-full rounded-xl border border-slate-200 bg-white shadow-sm p-8">
        <h1 className="text-2xl font-semibold text-slate-900 mb-3">Access Denied</h1>
        <p className="text-slate-700 leading-relaxed">
          User role is not configured. Please contact MES Administrator.
        </p>
      </div>
    </div>
  );
}