'use client'

import React from 'react'
import Navigation from '@/components/Navigation'

export default function Home() {
  // Sample data - before processing
  const rawDataSample = [
    { timestamp: '2024-01-01', value: 45.2, temp: 22.5, humidity: 65 },
    { timestamp: '2024-01-02', value: 47.8, temp: 23.1, humidity: 68 },
    { timestamp: '2024-01-03', value: 46.5, temp: 21.9, humidity: 62 },
    { timestamp: '2024-01-04', value: 48.3, temp: 24.0, humidity: 70 },
    { timestamp: '2024-01-05', value: 49.1, temp: 25.5, humidity: 72 },
  ]

  // Sample data - after feature engineering
  const engineeredDataSample = [
    {
      timestamp: '2024-01-05',
      value: 49.1,
      'value_roll_mean_3': 47.87,
      'value_roll_std_3': 1.32,
      'value_zscore': 0.85,
      'value_diff_1': 0.8,
    },
    {
      timestamp: '2024-01-06',
      value: 50.5,
      'value_roll_mean_3': 49.30,
      'value_roll_std_3': 0.94,
      'value_zscore': 1.24,
      'value_diff_1': 1.4,
    },
  ]

  // Statistics
  const stats = {
    rawRecords: 15420,
    processedRecords: 15400,
    featuresGenerated: 13,
    processingTime: '2m 34s',
    outputSize: '2.4 MB',
  }

  const features = [
    { name: 'Rolling Mean (3)', count: 5, color: '#0066cc' },
    { name: 'Rolling Mean (6)', count: 5, color: '#0099ff' },
    { name: 'Rolling Mean (12)', count: 5, color: '#00ccff' },
    { name: 'Rolling Mean (24)', count: 5, color: '#33ddff' },
    { name: 'Rolling Std (3-24)', count: 20, color: '#ff6600' },
    { name: 'Z-Scores', count: 5, color: '#ff0066' },
    { name: 'Lag Differences', count: 5, color: '#00cc00' },
  ]

  return (
    <>
      <Navigation />
      <header>
        <div className="container">
          <h1>T1_AD Demo</h1>
          <p>Feature Engineering & SageMaker Processing Results</p>
        </div>
      </header>

      <main className="container">
        {/* Executive Summary */}
        <section>
          <h2>📊 Processing Summary</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Input Records</h3>
              <p style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#0066cc' }}>
                {stats.rawRecords.toLocaleString()}
              </p>
              <p style={{ color: '#6c757d' }}>Raw data points processed</p>
            </div>

            <div className="card">
              <h3>Output Records</h3>
              <p style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#00cc00' }}>
                {stats.processedRecords.toLocaleString()}
              </p>
              <p style={{ color: '#6c757d' }}>After cleaning & deduplication</p>
            </div>

            <div className="card">
              <h3>Features Created</h3>
              <p style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#ff6600' }}>
                {stats.featuresGenerated}
              </p>
              <p style={{ color: '#6c757d' }}>Automated engineered features</p>
            </div>

            <div className="card">
              <h3>Processing Time</h3>
              <p style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#9933cc' }}>
                {stats.processingTime}
              </p>
              <p style={{ color: '#6c757d' }}>On SageMaker Processing</p>
            </div>
          </div>
        </section>

        {/* Data Transformation */}
        <section>
          <h2>🔄 Data Transformation Example</h2>

          <h3>Before: Raw Data</h3>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table style={{ fontSize: '0.9rem' }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Value</th>
                  <th>Temp</th>
                  <th>Humidity</th>
                </tr>
              </thead>
              <tbody>
                {rawDataSample.map((row, i) => (
                  <tr key={i}>
                    <td>{row.timestamp}</td>
                    <td>{row.value}</td>
                    <td>{row.temp}°C</td>
                    <td>{row.humidity}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3>After: With Engineered Features</h3>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table style={{ fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Value</th>
                  <th>Roll Mean (3)</th>
                  <th>Roll Std (3)</th>
                  <th>Z-Score</th>
                  <th>Diff (1)</th>
                </tr>
              </thead>
              <tbody>
                {engineeredDataSample.map((row, i) => (
                  <tr key={i}>
                    <td>{row.timestamp}</td>
                    <td>{row.value}</td>
                    <td>{row['value_roll_mean_3'].toFixed(2)}</td>
                    <td>{row['value_roll_std_3'].toFixed(2)}</td>
                    <td>{row['value_zscore'].toFixed(2)}</td>
                    <td>{row['value_diff_1'].toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card" style={{ marginTop: '1rem', background: '#f0f7ff', borderColor: '#0066cc' }}>
            <p>
              <strong>✨ Features Generated:</strong>
            </p>
            <ul style={{ columnCount: 2, columnGap: '2rem' }}>
              <li>Rolling Mean (windows: 3, 6, 12, 24)</li>
              <li>Rolling Std Dev (windows: 3, 6, 12, 24)</li>
              <li>Z-Score Normalization</li>
              <li>Lag Differences (period: 1)</li>
            </ul>
          </div>
        </section>

        {/* Feature Statistics */}
        <section>
          <h2>📈 Feature Engineering Breakdown</h2>
          <div className="card">
            <p style={{ marginBottom: '1.5rem' }}>
              Total of <strong>13 new features</strong> created from original columns:
            </p>
            <div style={{ display: 'grid', gap: '0.5rem' }}>
              {features.map((feat, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      background: feat.color,
                      borderRadius: '3px',
                    }}
                  />
                  <span>{feat.name}</span>
                  <span style={{ marginLeft: 'auto', color: '#6c757d', fontWeight: 'bold' }}>
                    {feat.count} features
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Processing Details */}
        <section>
          <h2>⚙️ Processing Configuration</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Environment</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Service:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      SageMaker Processing
                    </td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Instance:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      ml.m5.large
                    </td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Region:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      ap-southeast-1
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <strong>Framework:</strong>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      scikit-learn 1.2
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Output Details</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Format:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      CSV
                    </td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Size:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      {stats.outputSize}
                    </td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>
                      <strong>Location:</strong>
                    </td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right' }}>
                      S3: features/
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <strong>Time Taken:</strong>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {stats.processingTime}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Data Quality */}
        <section>
          <h2>✅ Data Quality Metrics</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Missing Values</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00cc00' }}>
                0%
              </p>
              <p style={{ color: '#6c757d' }}>All records complete</p>
            </div>

            <div className="card">
              <h3>Outliers Detected</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff9900' }}>
                24
              </p>
              <p style={{ color: '#6c757d' }}>Flagged but preserved</p>
            </div>

            <div className="card">
              <h3>Duplicates Removed</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0066cc' }}>
                20
              </p>
              <p style={{ color: '#6c757d' }}>Exact duplicates cleaned</p>
            </div>

            <div className="card">
              <h3>Data Validity</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00cc00' }}>
                99.87%
              </p>
              <p style={{ color: '#6c757d' }}>Pass data validation</p>
            </div>
          </div>
        </section>

        {/* Results Samples */}
        <section>
          <h2>🎯 Sample Results</h2>
          <div className="card">
            <h3>Statistical Summary</h3>
            <table style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left' }}>Metric</th>
                  <th style={{ textAlign: 'center' }}>Original Value</th>
                  <th style={{ textAlign: 'center' }}>Roll Mean (3)</th>
                  <th style={{ textAlign: 'center' }}>Roll Std (3)</th>
                  <th style={{ textAlign: 'center' }}>Z-Score</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Mean</strong></td>
                  <td style={{ textAlign: 'center' }}>47.34</td>
                  <td style={{ textAlign: 'center' }}>47.31</td>
                  <td style={{ textAlign: 'center' }}>1.24</td>
                  <td style={{ textAlign: 'center' }}>0.00</td>
                </tr>
                <tr>
                  <td><strong>Std Dev</strong></td>
                  <td style={{ textAlign: 'center' }}>2.15</td>
                  <td style={{ textAlign: 'center' }}>1.98</td>
                  <td style={{ textAlign: 'center' }}>0.45</td>
                  <td style={{ textAlign: 'center' }}>1.00</td>
                </tr>
                <tr>
                  <td><strong>Min</strong></td>
                  <td style={{ textAlign: 'center' }}>44.22</td>
                  <td style={{ textAlign: 'center' }}>45.12</td>
                  <td style={{ textAlign: 'center' }}>0.12</td>
                  <td style={{ textAlign: 'center' }}>-1.45</td>
                </tr>
                <tr>
                  <td><strong>Max</strong></td>
                  <td style={{ textAlign: 'center' }}>51.87</td>
                  <td style={{ textAlign: 'center' }}>50.23</td>
                  <td style={{ textAlign: 'center' }}>2.89</td>
                  <td style={{ textAlign: 'center' }}>2.12</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Status */}
        <section>
          <h2>✨ Pipeline Status</h2>
          <div className="card-grid">
            <div className="card">
              <h3>📥 Data Ingestion</h3>
              <p className="badge badge-success">✓ Complete</p>
              <p style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
                15,420 records loaded
              </p>
            </div>

            <div className="card">
              <h3>🔍 Data Cleaning</h3>
              <p className="badge badge-success">✓ Complete</p>
              <p style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
                Removed 20 duplicates
              </p>
            </div>

            <div className="card">
              <h3>✨ Feature Engineering</h3>
              <p className="badge badge-success">✓ Complete</p>
              <p style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
                13 features created
              </p>
            </div>

            <div className="card">
              <h3>📊 Ready for ML</h3>
              <p className="badge badge-success">✓ Ready</p>
              <p style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
                In S3: features/
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #dee2e6', marginTop: '3rem', paddingTop: '2rem', textAlign: 'center', color: '#6c757d' }}>
        <div className="container">
          <p>T1_AD Demo | Feature Engineering Results | 2026</p>
        </div>
      </footer>
    </>
  )
}
