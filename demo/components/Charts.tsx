'use client'

import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts'

// Time Series Data
export function TimeSeriesChart() {
  const data = [
    { date: 'Jan 1', value: 45.2, smooth: 45.0, zscore: -0.5 },
    { date: 'Jan 2', value: 47.8, smooth: 46.3, zscore: 0.2 },
    { date: 'Jan 3', value: 46.5, smooth: 47.2, zscore: -0.1 },
    { date: 'Jan 4', value: 48.3, smooth: 48.1, zscore: 0.8 },
    { date: 'Jan 5', value: 49.1, smooth: 49.0, zscore: 1.1 },
    { date: 'Jan 6', value: 48.7, smooth: 48.9, zscore: 0.9 },
    { date: 'Jan 7', value: 50.2, smooth: 49.7, zscore: 1.4 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="value" stroke="#0066cc" name="Original" strokeWidth={2} />
        <Line type="monotone" dataKey="smooth" stroke="#ff6600" name="Rolling Mean" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}

// Rolling Stats
export function RollingStatsChart() {
  const data = [
    { window: '3', mean: 47.87, std: 1.32 },
    { window: '6', mean: 47.92, std: 1.28 },
    { window: '12', mean: 48.01, std: 1.35 },
    { window: '24', mean: 48.10, std: 1.42 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="window" label={{ value: 'Window Size', position: 'insideBottomRight', offset: -5 }} />
        <YAxis yAxisId="left" label={{ value: 'Mean', angle: -90, position: 'insideLeft' }} />
        <YAxis yAxisId="right" orientation="right" label={{ value: 'Std Dev', angle: 90, position: 'insideRight' }} />
        <Tooltip />
        <Legend />
        <Bar yAxisId="left" dataKey="mean" fill="#0099ff" name="Rolling Mean" />
        <Bar yAxisId="right" dataKey="std" fill="#ff6600" name="Std Deviation" />
      </BarChart>
    </ResponsiveContainer>
  )
}

// Z-Score Distribution
export function ZScoreChart() {
  const data = [
    { zscore: -2.0, count: 5 },
    { zscore: -1.5, count: 18 },
    { zscore: -1.0, count: 45 },
    { zscore: -0.5, count: 87 },
    { zscore: 0.0, count: 125 },
    { zscore: 0.5, count: 98 },
    { zscore: 1.0, count: 52 },
    { zscore: 1.5, count: 28 },
    { zscore: 2.0, count: 12 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="zscore" />
        <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Bar dataKey="count" fill="#00ccff" name="Frequency" />
      </BarChart>
    </ResponsiveContainer>
  )
}

// Feature Distribution
export function FeatureDistributionChart() {
  const data = [
    { name: 'Roll Mean', value: 40 },
    { name: 'Roll Std', value: 40 },
    { name: 'Z-Score', value: 20 },
    { name: 'Diff', value: 20 },
  ]

  const COLORS = ['#0066cc', '#0099ff', '#ff6600', '#00cc00']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Bar dataKey="value" fill="#0066cc" name="Features">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// Before vs After Comparison
export function BeforeAfterChart() {
  const data = [
    { metric: 'Mean', before: 47.34, after: 47.31 },
    { metric: 'Std Dev', before: 2.15, after: 1.98 },
    { metric: 'Min', before: 44.22, after: 45.12 },
    { metric: 'Max', before: 51.87, after: 50.23 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="metric" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="before" fill="#ff9999" name="Original Data" />
        <Bar dataKey="after" fill="#99cc99" name="After Engineering" />
      </BarChart>
    </ResponsiveContainer>
  )
}

// Correlation Heatmap alternative (using scatter)
export function FeatureLagChart() {
  const data = [
    { lag: 0, corr: 1.0 },
    { lag: 1, corr: 0.85 },
    { lag: 2, corr: 0.71 },
    { lag: 3, corr: 0.62 },
    { lag: 4, corr: 0.54 },
    { lag: 5, corr: 0.48 },
    { lag: 6, corr: 0.42 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="lag" label={{ value: 'Lag Period', position: 'insideBottomRight', offset: -5 }} />
        <YAxis label={{ value: 'Correlation', angle: -90, position: 'insideLeft' }} domain={[0, 1]} />
        <Tooltip formatter={(value) => value.toFixed(2)} />
        <Line type="monotone" dataKey="corr" stroke="#9933cc" strokeWidth={3} name="Autocorrelation" dot={{ fill: '#9933cc', r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

// Processing Time Breakdown
export function ProcessingTimeChart() {
  const data = [
    { stage: 'Data Load', time: 12, color: '#0066cc' },
    { stage: 'Preprocessing', time: 45, color: '#0099ff' },
    { stage: 'Feature Eng', time: 78, color: '#ff6600' },
    { stage: 'Validation', time: 28, color: '#00cc00' },
    { stage: 'Output Write', time: 11, color: '#9933cc' },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" label={{ value: 'Time (seconds)', position: 'insideBottomRight', offset: -5 }} />
        <YAxis dataKey="stage" type="category" width={100} />
        <Tooltip />
        <Bar dataKey="time" name="Duration (sec)">
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// Data Quality Metrics
export function DataQualityChart() {
  const data = [
    { metric: 'Completeness', value: 100 },
    { metric: 'Validity', value: 99.87 },
    { metric: 'Uniqueness', value: 99.87 },
    { metric: 'Timeliness', value: 100 },
    { metric: 'Consistency', value: 99.95 },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="metric" />
        <YAxis domain={[95, 100]} />
        <Tooltip formatter={(value) => `${value}%`} />
        <Bar dataKey="value" fill="#00cc00" name="Score (%)" />
      </BarChart>
    </ResponsiveContainer>
  )
}
