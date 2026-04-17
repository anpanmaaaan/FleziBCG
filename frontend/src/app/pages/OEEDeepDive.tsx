import { useState } from 'react';
import { Breadcrumb } from '@/app/components';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Zap,
  Target,
  ChevronDown,
  Info,
  Lightbulb,
  Brain,
  Sparkles,
  Download,
  Clock,
  CheckCircle,
  Settings as SettingsIcon
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area
} from 'recharts';
import { format } from 'date-fns';
import {
  generateOEETrendData,
  getSixBigLossesData,
  getDowntimeData,
  getLineComparisonData,
  getCurrentOEEMetrics,
  getTopLossInsight,
  getNextShiftRiskPrediction,
  getWhatIfEstimation
} from '@/app/data/oee-mock-data';

type TimeRange = 'today' | 'shift' | '7days' | 'month';
type ShiftType = 'all' | 'day' | 'night';

export function OEEDeepDive() {
  const [timeRange, setTimeRange] = useState<TimeRange>('today');
  const [shift, setShift] = useState<ShiftType>('all');
  const [selectedLines, setSelectedLines] = useState<string[]>(['all']);
  const [showAlert, setShowAlert] = useState(true);

  // Load data from centralized mock data
  const trendData = generateOEETrendData(30);
  const sixBigLossesData = getSixBigLossesData();
  const downtimeData = getDowntimeData();
  const lineComparisonData = getLineComparisonData();
  const currentMetrics = getCurrentOEEMetrics();
  const topLossInsight = getTopLossInsight();
  const riskPrediction = getNextShiftRiskPrediction();
  const whatIfEstimation = getWhatIfEstimation('setup loss', 10);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500';
      case 'reduced': return 'text-yellow-500';
      case 'setup': return 'text-orange-500';
      case 'downtime': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return '🟢';
      case 'reduced': return '🟡';
      case 'setup': return '🟠';
      case 'downtime': return '🔴';
      default: return '⚫';
    }
  };

  const getOEEColor = (value: number) => {
    if (value >= 85) return 'text-green-600';
    if (value >= 70) return 'text-blue-600';
    if (value >= 60) return 'text-yellow-600';
    if (value >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getOEEBadge = (value: number) => {
    if (value >= 85) return { text: 'High Performance', color: 'bg-green-500' };
    if (value >= 70) return { text: 'Standard', color: 'bg-blue-500' };
    if (value >= 60) return { text: 'Below Standard', color: 'bg-yellow-500' };
    if (value >= 40) return { text: 'Low Performance', color: 'bg-orange-500' };
    return { text: 'Critical', color: 'bg-red-500' };
  };

  const KPICard = ({ 
    title, 
    value, 
    trend, 
    icon: Icon, 
    color 
  }: { 
    title: string; 
    value: number; 
    trend: number; 
    icon: any; 
    color: string;
  }) => {
    const badge = getOEEBadge(value);
    return (
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-lg ${color} bg-opacity-10`}>
            <Icon className={`w-6 h-6 ${color}`} />
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${badge.color} text-white font-medium`}>
            {badge.text}
          </span>
        </div>
        <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
        <div className="flex items-baseline gap-3">
          <span className={`text-3xl font-bold ${getOEEColor(value)}`}>
            {value.toFixed(1)}%
          </span>
          <div className={`flex items-center gap-1 text-sm font-medium ${
            trend >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span>{Math.abs(trend).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    );
  };

  const AIInsightCard = ({ 
    icon: Icon, 
    title, 
    content, 
    confidence 
  }: { 
    icon: any; 
    title: string; 
    content: React.ReactNode; 
    confidence?: string;
  }) => {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow p-6 border-2 border-purple-200">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 rounded-lg bg-purple-500 bg-opacity-10">
            <Icon className="w-5 h-5 text-purple-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-purple-900 mb-1">{title}</h3>
            {confidence && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-600">Confidence:</span>
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full ${
                        i < (confidence === 'High' ? 4 : confidence === 'Medium' ? 3 : 2)
                          ? 'bg-purple-600'
                          : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs font-medium text-purple-700">{confidence}</span>
              </div>
            )}
          </div>
        </div>
        <div className="text-sm text-gray-700">{content}</div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="px-6 py-4">
          {/* Breadcrumb */}
          <Breadcrumb
            items={[
              { label: 'Performance' },
              { label: 'OEE Deep Dive' }
            ]}
          />
          
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">OEE Deep Dive Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">
                Real-time Overall Equipment Effectiveness analytics with AI insights
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                {format(new Date(), 'PPP p')}
              </span>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex items-center gap-3 flex-wrap">
            {/* Quick Presets */}
            <div className="flex items-center gap-2">
              {(['today', 'shift', '7days', 'month'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors ${
                    timeRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {range === 'today' ? 'Today' : range === 'shift' ? 'This Shift' : range === '7days' ? 'Last 7 Days' : 'This Month'}
                </button>
              ))}
            </div>

            <div className="h-6 w-px bg-gray-300" />

            {/* Shift Selector */}
            <select
              value={shift}
              onChange={(e) => setShift(e.target.value as ShiftType)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Shifts</option>
              <option value="day">Day Shift</option>
              <option value="night">Night Shift</option>
            </select>

            {/* Line Selector */}
            <select
              value={selectedLines[0]}
              onChange={(e) => setSelectedLines([e.target.value])}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Lines</option>
              <option value="line1">Line 1</option>
              <option value="line2">Line 2</option>
              <option value="line3">Line 3</option>
              <option value="line4">Line 4</option>
              <option value="line5">Line 5</option>
            </select>

            {/* Active Filter Badge */}
            {(timeRange !== 'today' || shift !== 'all' || selectedLines[0] !== 'all') && (
              <div className="ml-auto flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 text-sm rounded-lg">
                <span>
                  Showing: {timeRange === 'today' ? 'Today' : timeRange === 'shift' ? 'This Shift' : timeRange === '7days' ? 'Last 7 Days' : 'This Month'}
                  {shift !== 'all' && `, ${shift === 'day' ? 'Day' : 'Night'} Shift`}
                  {selectedLines[0] !== 'all' && `, ${selectedLines[0]}`}
                </span>
                <button
                  onClick={() => {
                    setTimeRange('today');
                    setShift('all');
                    setSelectedLines(['all']);
                  }}
                  className="text-blue-600 hover:text-blue-800"
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Alert Banner */}
        {showAlert && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-red-900">OEE Alert: Line 3 downtime exceeded 30 minutes</h3>
                <p className="text-sm text-red-700 mt-1">Equipment failure detected. Maintenance team notified.</p>
                <div className="flex items-center gap-3 mt-2">
                  <button className="text-sm font-medium text-red-700 hover:text-red-900">View Details</button>
                  <button className="text-sm font-medium text-red-700 hover:text-red-900">Snooze 15 min</button>
                </div>
              </div>
            </div>
            <button onClick={() => setShowAlert(false)} className="text-red-600 hover:text-red-800">
              ✕
            </button>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Overall OEE"
            value={currentMetrics.oee}
            trend={currentMetrics.trends.oee}
            icon={Activity}
            color="text-purple-600"
          />
          <KPICard
            title="Availability"
            value={currentMetrics.availability}
            trend={currentMetrics.trends.availability}
            icon={Clock}
            color="text-blue-600"
          />
          <KPICard
            title="Performance"
            value={currentMetrics.performance}
            trend={currentMetrics.trends.performance}
            icon={Zap}
            color="text-green-600"
          />
          <KPICard
            title="Quality"
            value={currentMetrics.quality}
            trend={currentMetrics.trends.quality}
            icon={CheckCircle}
            color="text-emerald-600"
          />
        </div>

        {/* AI Insight Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <AIInsightCard
            icon={Sparkles}
            title="AI Insight - Biggest OEE Impact Today"
            confidence="High"
            content={
              <div className="space-y-2">
                <p className="font-semibold text-purple-900">Equipment Failure – 48 min</p>
                <p className="text-sm text-gray-600">Impact: -5.2% OEE</p>
                <p className="text-sm text-gray-600">Suggested focus: <span className="font-medium">Line 3</span></p>
                <div className="flex gap-2 mt-3">
                  <button className="text-xs px-3 py-1.5 bg-purple-600 text-white rounded hover:bg-purple-700">
                    🔧 Create Work Order
                  </button>
                  <button className="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200">
                    View History
                  </button>
                </div>
              </div>
            }
          />
          <AIInsightCard
            icon={Target}
            title="AI Prediction - Next Shift OEE Risk"
            content={
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded">Medium Risk</span>
                  <span className="text-xs text-gray-600">Next shift: 2:00 PM - 10:00 PM</span>
                </div>
                <p className="text-sm font-medium text-gray-900 mt-3">Reasons:</p>
                <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                  <li>High downtime frequency</li>
                  <li>Slow recovery after stops</li>
                </ul>
                <p className="text-sm font-medium text-purple-900 mt-3">💡 Recommended actions:</p>
                <ul className="text-xs text-gray-600 space-y-1 list-disc list-inside">
                  <li>Pre-position maintenance team</li>
                  <li>Check spare parts availability</li>
                </ul>
              </div>
            }
          />
          <AIInsightCard
            icon={Lightbulb}
            title="What If... (AI Estimation)"
            content={
              <div className="space-y-2">
                <p className="text-sm text-gray-700">Reduce <span className="font-semibold">setup loss by 10%</span></p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-2xl font-bold text-purple-900">+3.4%</span>
                  <span className="text-sm text-gray-600">OEE gain</span>
                </div>
                <p className="text-xs text-gray-600 mt-2">New projected OEE: <span className="font-semibold">88.6%</span></p>
                <div className="flex gap-2 mt-3">
                  <button className="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200">
                    🎯 Simulate 20%
                  </button>
                  <button className="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200">
                    Create Goal
                  </button>
                </div>
              </div>
            }
          />
        </div>

        {/* Six Big Losses */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Six Big Losses - Today
          </h2>
          <div className="space-y-3">
            {sixBigLossesData.map((loss, index) => (
              <div key={index} className="group">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{loss.name}</span>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-medium ${loss.trend >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {loss.trend >= 0 ? '↗' : '↘'} {Math.abs(loss.trend)}% vs yesterday
                    </span>
                    <span className="text-sm font-semibold text-gray-900">{loss.minutes} min</span>
                    <span className="text-sm text-gray-600">({loss.impact.toFixed(1)}%)</span>
                  </div>
                </div>
                <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                  <div
                    className={`absolute h-full transition-all ${
                      loss.category === 'availability'
                        ? 'bg-blue-500'
                        : loss.category === 'performance'
                        ? 'bg-green-500'
                        : 'bg-purple-500'
                    }`}
                    style={{ width: `${(loss.impact / 6) * 100}%` }}
                  />
                  <div className="absolute inset-0 flex items-center px-3">
                    <span className="text-xs font-medium text-white mix-blend-difference">
                      {loss.category.charAt(0).toUpperCase() + loss.category.slice(1)} Loss
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Downtime Pareto */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Downtime Causes - This Week</h2>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={downtimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="cause" angle={-45} textAnchor="end" height={100} tick={{ fontSize: 12 }} />
                <YAxis yAxisId="left" label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" label={{ value: 'Cumulative %', angle: 90, position: 'insideRight' }} />
                <Tooltip />
                <Legend />
                <Bar 
                  yAxisId="left" 
                  dataKey="minutes" 
                  fill="#3b82f6" 
                  name="Downtime (min)"
                  isAnimationActive={false}
                />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="cumulative" 
                  stroke="#ef4444" 
                  strokeWidth={2} 
                  name="Cumulative %"
                  isAnimationActive={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
            <div className="mt-3 text-sm text-gray-600 text-center">
              <span className="font-medium text-orange-600">80%</span> of losses from top 3 causes (Pareto Rule)
            </div>
          </div>

          {/* OEE Trend */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">OEE Trend - Last 30 Days</h2>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke="#94a3b8" 
                  strokeDasharray="5 5" 
                  name="Target"
                  isAnimationActive={false}
                />
                <Area 
                  type="monotone" 
                  dataKey="oee" 
                  fill="#8b5cf6" 
                  fillOpacity={0.1}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="oee" 
                  stroke="#8b5cf6" 
                  strokeWidth={2} 
                  name="OEE"
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="availability" 
                  stroke="#3b82f6" 
                  strokeWidth={1.5} 
                  name="Availability"
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="performance" 
                  stroke="#10b981" 
                  strokeWidth={1.5} 
                  name="Performance"
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="quality" 
                  stroke="#6366f1" 
                  strokeWidth={1.5} 
                  name="Quality"
                  isAnimationActive={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Line Comparison Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">Production Lines Comparison - Today</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Line
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    OEE
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Availability
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quality
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {lineComparisonData.map((line, index) => (
                  <tr key={index} className="hover:bg-gray-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">{line.line}</span>
                        {line.bottleneck && (
                          <span className="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded font-semibold">
                            ⚠️ BOTTLENECK
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-semibold ${getOEEColor(line.oee)}`}>
                        {line.oee}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {line.availability}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {line.performance}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {line.quality}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span>{getStatusIcon(line.status)}</span>
                        <span className={`text-sm font-medium ${getStatusColor(line.status)}`}>
                          {line.status === 'running' ? 'Running' : 
                           line.status === 'reduced' ? 'Reduced Speed' :
                           line.status === 'setup' ? 'Setup' :
                           line.status === 'downtime' ? 'Downtime' : 'Offline'}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
                <tr className="bg-gray-100 font-semibold">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    Average
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(lineComparisonData.reduce((sum, l) => sum + l.oee, 0) / lineComparisonData.length).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(lineComparisonData.reduce((sum, l) => sum + l.availability, 0) / lineComparisonData.length).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(lineComparisonData.reduce((sum, l) => sum + l.performance, 0) / lineComparisonData.length).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(lineComparisonData.reduce((sum, l) => sum + l.quality, 0) / lineComparisonData.length).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    -
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}