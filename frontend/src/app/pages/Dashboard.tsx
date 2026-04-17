import { useMemo, useState, useEffect } from "react";
import { Link } from "react-router";
import {
  Activity,
  TrendingUp,
  CheckCircle2,
  Clock,
  Package,
  Target,
  ArrowRight,
  AlertTriangle
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";
import { dashboardApi, type DashboardHealthResponse, type DashboardSummaryResponse } from "@/app/api";

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  iconBgColor: string;
  subtitle?: string;
}

function KPICard({ title, value, change, trend, icon, iconBgColor, subtitle }: KPICardProps) {
  return (
    <div className="bg-white rounded-xl border shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-lg ${iconBgColor}`}>
          {icon}
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
            trend === 'up' ? 'bg-green-100 text-green-700' :
            trend === 'down' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-700'
          }`}>
            <span>{Math.abs(change)}</span>
          </div>
        )}
      </div>
      <div>
        <div className="text-sm text-gray-600 mb-1">{title}</div>
        <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
        {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
      </div>
    </div>
  );
}

export function Dashboard() {
  const [summaryData, setSummaryData] = useState<DashboardSummaryResponse | null>(null);
  const [healthData, setHealthData] = useState<DashboardHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      setLoading(true);
      setError(null);

      try {
        const [summary, health] = await Promise.all([
          dashboardApi.getSummary(),
          dashboardApi.getHealth(),
        ]);

        if (cancelled) {
          return;
        }

        setSummaryData(summary);
        setHealthData(health);
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Failed to load dashboard";
          setError(message);
          setSummaryData(null);
          setHealthData(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const topRisk = healthData?.riskWorkOrders?.[0] ?? null;
  const topBottleneck = healthData?.bottlenecks?.[0] ?? null;

  const productionTrendData = useMemo(() => {
    if (!summaryData) {
      return [];
    }

    return [
      {
        id: "summary-point",
        date: summaryData.context.date,
        planned: summaryData.workOrders.total,
        actual: summaryData.workOrders.onTime,
      },
    ];
  }, [summaryData]);

  const qualityTrendData = useMemo(() => {
    // TODO: Backend dashboard trend API does not provide quality time-series yet.
    // Keep chart layout intact and render empty data until backend adds trend points.
    return [] as Array<{ id: string; date: string; rate: number }>;
  }, []);

  const severityKey = summaryData?.alerts.highestSeverity
    ? `dashboard.alert.severity.${summaryData.alerts.highestSeverity.toLowerCase()}`
    : "dashboard.alert.severity.unknown";

  const riskReasonKey = topRisk
    ? `dashboard.risk.reason.${topRisk.reasonCode.toLowerCase()}`
    : "dashboard.risk.reason.none";

  const bottleneckStatusKey = topBottleneck
    ? `dashboard.bottleneck.status.${topBottleneck.status.toLowerCase()}`
    : "dashboard.bottleneck.status.none";

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading && (
          <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
            <p className="text-sm text-blue-800">dashboard.loading</p>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
            <p className="text-sm text-red-800">dashboard.error.load_failed: {error}</p>
          </div>
        )}

        {/* Alert Banner with CTA */}
        <div className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 border-l-4 border-orange-500 p-4 rounded-r-lg">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-orange-900">
                  dashboard.alert.summary.{severityKey}
                </h3>
                <p className="text-sm text-orange-700 mt-1">
                  {topRisk
                    ? `dashboard.alert.risk_work_order: ${topRisk.workOrderNumber} (${riskReasonKey})`
                    : "dashboard.alert.risk_work_order.none"}
                </p>
              </div>
            </div>
            <Link
              to="/performance/oee-deep-dive"
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors whitespace-nowrap"
            >
              <span className="font-medium">View OEE Deep Dive</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* KPI Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <KPICard
            title="Overall Equipment Effectiveness"
            value="--"
            trend="neutral"
            icon={<Target className="w-6 h-6 text-blue-600" />}
            iconBgColor="bg-blue-100"
            subtitle="dashboard.kpi.oee.unavailable"
          />
          <KPICard
            title="Production Volume"
            value={summaryData?.workOrders.total ?? "--"}
            icon={<Package className="w-6 h-6 text-green-600" />}
            iconBgColor="bg-green-100"
            subtitle="dashboard.kpi.work_orders.total"
          />
          <KPICard
            title="Quality Rate"
            value="--"
            trend="neutral"
            icon={<CheckCircle2 className="w-6 h-6 text-purple-600" />}
            iconBgColor="bg-purple-100"
            subtitle="dashboard.kpi.quality.unavailable"
          />
          <KPICard
            title="Alerts"
            value={summaryData?.alerts.count ?? "--"}
            trend="neutral"
            icon={<Activity className="w-6 h-6 text-indigo-600" />}
            iconBgColor="bg-indigo-100"
            subtitle={severityKey}
          />
        </div>

        {/* OEE Summary Card with Link */}
        <div className="mb-6">
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border-2 border-purple-200 shadow-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-purple-900 mb-2">OEE Performance Summary</h3>
                <p className="text-sm text-gray-700">Quick overview of equipment effectiveness metrics</p>
              </div>
              <Link
                to="/performance/oee-deep-dive"
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                <span className="font-medium">Deep Dive →</span>
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-purple-100">
                <div className="text-sm text-gray-600 mb-1">work_orders.on_time</div>
                <div className="text-2xl font-bold text-blue-600">{summaryData?.workOrders.onTime ?? "--"}</div>
                <div className="flex items-center gap-1 text-xs text-blue-600 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>dashboard.kpi.work_orders.on_time</span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-100">
                <div className="text-sm text-gray-600 mb-1">operations.in_progress</div>
                <div className="text-2xl font-bold text-green-600">{summaryData?.operations.inProgress ?? "--"}</div>
                <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>dashboard.kpi.operations.in_progress</span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-100">
                <div className="text-sm text-gray-600 mb-1">operations.blocked</div>
                <div className="text-2xl font-bold text-emerald-600">{summaryData?.operations.blocked ?? "--"}</div>
                <div className="flex items-center gap-1 text-xs text-emerald-600 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>dashboard.kpi.operations.blocked</span>
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 bg-purple-100 rounded-lg">
              <p className="text-sm text-purple-900">
                <strong>dashboard.top_issue:</strong> {bottleneckStatusKey}
                {topBottleneck ? ` · ${topBottleneck.scopeCode}` : ""}
              </p>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Production Trend */}
          <div className="bg-white rounded-xl border shadow-lg p-6" key="production-chart">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Production Trend</h3>
                <p className="text-sm text-gray-500">Planned vs Actual Output</p>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <span className="text-sm font-semibold text-green-600">dashboard.trend.summary</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300} key="production-responsive">
              <LineChart data={productionTrendData} id="production-line-chart">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" key="prod-grid" />
                <XAxis dataKey="date" stroke="var(--chart-axis)" style={{ fontSize: '12px' }} key="prod-xaxis" />
                <YAxis stroke="var(--chart-axis)" style={{ fontSize: '12px' }} key="prod-yaxis" />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--chart-tooltip-bg)', border: '1px solid var(--chart-tooltip-border)', borderRadius: '8px' }}
                  key="prod-tooltip"
                />
                <Legend wrapperStyle={{ fontSize: '14px' }} key="prod-legend" />
                <Line
                  key="prod-line-planned"
                  type="monotone"
                  dataKey="planned"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  name="Planned"
                  dot={{ fill: 'var(--chart-1)', r: 4 }}
                  isAnimationActive={false}
                />
                <Line
                  key="prod-line-actual"
                  type="monotone"
                  dataKey="actual"
                  stroke="var(--chart-2)"
                  strokeWidth={2}
                  name="Actual"
                  dot={{ fill: 'var(--chart-2)', r: 4 }}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Quality Trend */}
          <div className="bg-white rounded-xl border shadow-lg p-6" key="quality-chart">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Quality Rate Trend</h3>
                <p className="text-sm text-gray-500">Daily quality performance</p>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <span className="text-sm font-semibold text-purple-600">dashboard.trend.pending_backend</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300} key="quality-responsive">
              <BarChart data={qualityTrendData} id="quality-bar-chart">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" key="qual-grid" />
                <XAxis dataKey="date" stroke="var(--chart-axis)" style={{ fontSize: '12px' }} key="qual-xaxis" />
                <YAxis domain={[90, 100]} stroke="var(--chart-axis)" style={{ fontSize: '12px' }} key="qual-yaxis" />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--chart-tooltip-bg)', border: '1px solid var(--chart-tooltip-border)', borderRadius: '8px' }}
                  formatter={(value: any) => `${value}%`}
                  key="qual-tooltip"
                />
                <Legend wrapperStyle={{ fontSize: '14px' }} key="qual-legend" />
                <Bar
                  key="qual-bar"
                  dataKey="rate"
                  fill="var(--chart-7)"
                  name="Quality Rate"
                  radius={[8, 8, 0, 0]}
                  isAnimationActive={false}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}