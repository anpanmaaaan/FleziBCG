import { useState, useEffect } from "react";
import { Link } from "react-router";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle2,
  Clock,
  Package,
  Target,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
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

// Sample data
const productionTrendData = [
  { id: 'prod-1', date: '03/20', planned: 1200, actual: 1150 },
  { id: 'prod-2', date: '03/21', planned: 1250, actual: 1220 },
  { id: 'prod-3', date: '03/22', planned: 1300, actual: 1180 },
  { id: 'prod-4', date: '03/23', planned: 1280, actual: 1260 },
  { id: 'prod-5', date: '03/24', planned: 1350, actual: 1310 },
  { id: 'prod-6', date: '03/25', planned: 1400, actual: 1380 },
  { id: 'prod-7', date: '03/26', planned: 1420, actual: 1400 },
  { id: 'prod-8', date: '03/27', planned: 1450, actual: 1280 },
];

const qualityTrendData = [
  { id: 'qual-1', date: '03/20', rate: 95.2 },
  { id: 'qual-2', date: '03/21', rate: 96.1 },
  { id: 'qual-3', date: '03/22', rate: 94.8 },
  { id: 'qual-4', date: '03/23', rate: 97.2 },
  { id: 'qual-5', date: '03/24', rate: 96.5 },
  { id: 'qual-6', date: '03/25', rate: 95.9 },
  { id: 'qual-7', date: '03/26', rate: 96.8 },
  { id: 'qual-8', date: '03/27', rate: 95.5 },
];

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
  const getTrendIcon = () => {
    if (!trend || trend === 'neutral') return <Minus className="w-4 h-4" />;
    return trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />;
  };

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
            {getTrendIcon()}
            <span>{Math.abs(change)}%</span>
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
  const [timeRange, setTimeRange] = useState<'today' | 'week' | 'month'>('today');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const totalPlanned = productionTrendData.reduce((sum, d) => sum + d.planned, 0);
  const totalActual = productionTrendData.reduce((sum, d) => sum + d.actual, 0);
  const overallEfficiency = Math.round((totalActual / totalPlanned) * 100);

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Alert Banner with CTA */}
        <div className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 border-l-4 border-orange-500 p-4 rounded-r-lg">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-orange-900">OEE Alert: Equipment Failure on Line 3</h3>
                <p className="text-sm text-orange-700 mt-1">
                  Overall OEE dropped to 72% today. Equipment Failure is the biggest loss (48 min, -5.2% OEE impact).
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
            value={`${overallEfficiency}%`}
            change={3.2}
            trend="up"
            icon={<Target className="w-6 h-6 text-blue-600" />}
            iconBgColor="bg-blue-100"
            subtitle="Target: 95%"
          />
          <KPICard
            title="Production Volume"
            value={totalActual.toLocaleString()}
            change={5.8}
            trend="up"
            icon={<Package className="w-6 h-6 text-green-600" />}
            iconBgColor="bg-green-100"
            subtitle={`Planned: ${totalPlanned.toLocaleString()}`}
          />
          <KPICard
            title="Quality Rate"
            value="96.2%"
            change={1.2}
            trend="up"
            icon={<CheckCircle2 className="w-6 h-6 text-purple-600" />}
            iconBgColor="bg-purple-100"
            subtitle="9,700 inspected"
          />
          <KPICard
            title="Active Lines"
            value="7/8"
            trend="neutral"
            icon={<Activity className="w-6 h-6 text-indigo-600" />}
            iconBgColor="bg-indigo-100"
            subtitle="Production lines"
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
                <div className="text-sm text-gray-600 mb-1">Availability</div>
                <div className="text-2xl font-bold text-blue-600">90.5%</div>
                <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                  <TrendingDown className="w-3 h-3" />
                  <span>-2.1% vs yesterday</span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-100">
                <div className="text-sm text-gray-600 mb-1">Performance</div>
                <div className="text-2xl font-bold text-green-600">94.8%</div>
                <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>+5.8% vs yesterday</span>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-100">
                <div className="text-sm text-gray-600 mb-1">Quality</div>
                <div className="text-2xl font-bold text-emerald-600">99.3%</div>
                <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>+0.5% vs yesterday</span>
                </div>
              </div>
            </div>
            <div className="mt-4 p-3 bg-purple-100 rounded-lg">
              <p className="text-sm text-purple-900">
                <strong>🔍 Top Issue:</strong> Equipment Failure on Line 3 (48 min downtime, -5.2% OEE impact)
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
                <span className="text-sm font-semibold text-green-600">+5.8%</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300} key="production-responsive">
              <LineChart data={productionTrendData} id="production-line-chart">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" key="prod-grid" />
                <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: '12px' }} key="prod-xaxis" />
                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} key="prod-yaxis" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                  key="prod-tooltip"
                />
                <Legend wrapperStyle={{ fontSize: '14px' }} key="prod-legend" />
                <Line
                  key="prod-line-planned"
                  type="monotone"
                  dataKey="planned"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Planned"
                  dot={{ fill: '#3b82f6', r: 4 }}
                  isAnimationActive={false}
                />
                <Line
                  key="prod-line-actual"
                  type="monotone"
                  dataKey="actual"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Actual"
                  dot={{ fill: '#10b981', r: 4 }}
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
                <span className="text-sm font-semibold text-purple-600">+1.2%</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300} key="quality-responsive">
              <BarChart data={qualityTrendData} id="quality-bar-chart">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" key="qual-grid" />
                <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: '12px' }} key="qual-xaxis" />
                <YAxis domain={[90, 100]} stroke="#6b7280" style={{ fontSize: '12px' }} key="qual-yaxis" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                  formatter={(value: any) => `${value}%`}
                  key="qual-tooltip"
                />
                <Legend wrapperStyle={{ fontSize: '14px' }} key="qual-legend" />
                <Bar
                  key="qual-bar"
                  dataKey="rate"
                  fill="#9333ea"
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