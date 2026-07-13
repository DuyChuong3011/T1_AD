'use client'

import Navigation from '@/components/Navigation'
import dynamic from 'next/dynamic'

const BeforeAfterChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.BeforeAfterChart })), { ssr: false })
const TimeSeriesChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.TimeSeriesChart })), { ssr: false })
const RollingStatsChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.RollingStatsChart })), { ssr: false })

export default function ComparisonPage() {
  return (
    <>
      <Navigation />
      <header>
        <div className="container">
          <h1>🔀 Before & After Comparison</h1>
          <p>Compare raw data with engineered features side-by-side</p>
        </div>
      </header>

      <main className="container">
        {/* Main Comparison */}
        <section>
          <h2>Statistical Comparison</h2>
          <div className="card">
            <h3>Key Metrics: Before vs After Processing</h3>
            <BeforeAfterChart />
            <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
              <div className="card">
                <h4>📊 Mean Value</h4>
                <p>Before: <strong>47.34</strong></p>
                <p>After: <strong>47.31</strong></p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Slight decrease due to outlier removal and smoothing.
                </p>
              </div>

              <div className="card">
                <h4>📈 Standard Deviation</h4>
                <p>Before: <strong>2.15</strong></p>
                <p>After: <strong>1.98</strong></p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Variance reduced through smoothing operations.
                </p>
              </div>

              <div className="card">
                <h4>📉 Min Value</h4>
                <p>Before: <strong>44.22</strong></p>
                <p>After: <strong>45.12</strong></p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Extreme values smoothed out in processed data.
                </p>
              </div>

              <div className="card">
                <h4>📈 Max Value</h4>
                <p>Before: <strong>51.87</strong></p>
                <p>After: <strong>50.23</strong></p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Peak values tempered by rolling window averaging.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Visual Comparison */}
        <section>
          <h2>Visual Transformation</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Time Series: Original vs Smoothed</h3>
              <TimeSeriesChart />
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
                The rolling mean (orange line) smooths out noise while preserving the overall trend of the original data (blue line).
              </p>
            </div>

            <div className="card">
              <h3>Rolling Window Effects</h3>
              <RollingStatsChart />
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
                Larger windows produce smoother trends with lower variance, trading detail for robustness.
              </p>
            </div>
          </div>
        </section>

        {/* Impact Analysis */}
        <section>
          <h2>Processing Impact Analysis</h2>
          <div className="card-grid">
            <div className="card">
              <h3>✅ Advantages of Processing</h3>
              <ul>
                <li><strong>Noise Reduction:</strong> Removed outliers and anomalies</li>
                <li><strong>Trend Clarity:</strong> Smoothing reveals underlying patterns</li>
                <li><strong>Feature Enrichment:</strong> 40 new features from 5 originals</li>
                <li><strong>Normalization:</strong> Z-scores enable fair feature comparison</li>
                <li><strong>Temporal Patterns:</strong> Lag differences capture momentum</li>
                <li><strong>Data Quality:</strong> 99.87% validity after cleaning</li>
              </ul>
            </div>

            <div className="card">
              <h3>⚠️ Trade-offs to Consider</h3>
              <ul>
                <li><strong>Information Loss:</strong> Smoothing reduces granularity</li>
                <li><strong>Computational Cost:</strong> 78 seconds for full pipeline</li>
                <li><strong>Feature Complexity:</strong> 45 features harder to interpret than 5</li>
                <li><strong>Lag Introduction:</strong> Moving windows create dependencies</li>
                <li><strong>Memory Usage:</strong> 2.4 MB output vs 0.3 MB input</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Data Volume */}
        <section>
          <h2>Data Volume & Efficiency</h2>
          <div className="card-grid">
            <div className="card">
              <h3>📥 Input</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#0066cc' }}>
                15,420
              </p>
              <p>Records processed</p>
              <hr style={{ margin: '1rem 0', border: 'none', borderTop: '1px solid #dee2e6' }} />
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                5
              </p>
              <p>Original columns</p>
            </div>

            <div className="card">
              <h3>📤 Output</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00cc00' }}>
                15,400
              </p>
              <p>Clean records (0.13% removed)</p>
              <hr style={{ margin: '1rem 0', border: 'none', borderTop: '1px solid #dee2e6' }} />
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                45
              </p>
              <p>Total features (40 engineered)</p>
            </div>

            <div className="card">
              <h3>📊 File Size</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff6600' }}>
                0.3 MB
              </p>
              <p>Raw input</p>
              <hr style={{ margin: '1rem 0', border: 'none', borderTop: '1px solid #dee2e6' }} />
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                2.4 MB
              </p>
              <p>Engineered output (8x)</p>
            </div>

            <div className="card">
              <h3>⚡ Processing Time</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#9933cc' }}>
                154 sec
              </p>
              <p>Total pipeline</p>
              <hr style={{ margin: '1rem 0', border: 'none', borderTop: '1px solid #dee2e6' }} />
              <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                78 sec
              </p>
              <p>Feature engineering</p>
            </div>
          </div>
        </section>

        {/* Feature Comparison */}
        <section>
          <h2>Original vs Engineered Features</h2>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Features</th>
                  <th>Count</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Original</strong></td>
                  <td>value, temp, humidity, pressure, humidity_ratio</td>
                  <td>5</td>
                  <td>Raw measurements</td>
                </tr>
                <tr style={{ background: '#f8f9fa' }}>
                  <td><strong>Rolling Mean</strong></td>
                  <td>value_roll_mean_[3,6,12,24], temp_roll_mean_[3,6,12,24], ...</td>
                  <td>20</td>
                  <td>Trend smoothing</td>
                </tr>
                <tr>
                  <td><strong>Rolling Std</strong></td>
                  <td>value_roll_std_[3,6,12,24], temp_roll_std_[3,6,12,24], ...</td>
                  <td>20</td>
                  <td>Volatility measurement</td>
                </tr>
                <tr style={{ background: '#f8f9fa' }}>
                  <td><strong>Z-Score</strong></td>
                  <td>value_zscore, temp_zscore, humidity_zscore, ...</td>
                  <td>5</td>
                  <td>Normalization</td>
                </tr>
                <tr>
                  <td><strong>Differences</strong></td>
                  <td>value_diff_1, temp_diff_1, humidity_diff_1, ...</td>
                  <td>5</td>
                  <td>Change detection</td>
                </tr>
                <tr style={{ background: '#e8f4f8', fontWeight: 'bold' }}>
                  <td>Total</td>
                  <td>—</td>
                  <td>45</td>
                  <td>ML-ready feature set</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Recommendations */}
        <section>
          <h2>✨ Recommendations</h2>
          <div className="card-grid">
            <div className="card">
              <h3>🎯 For ML Models</h3>
              <ul>
                <li>Use rolling statistics for trend-based models</li>
                <li>Include differences for RNN/LSTM models</li>
                <li>Consider z-scores for distance-based algorithms</li>
                <li>Drop highly correlated features (>0.95) if needed</li>
                <li>Normalize before training non-tree models</li>
              </ul>
            </div>

            <div className="card">
              <h3>🔍 For Feature Selection</h3>
              <ul>
                <li>Use correlation analysis to reduce redundancy</li>
                <li>Apply mutual information for nonlinear relationships</li>
                <li>Test feature importance with tree models</li>
                <li>Consider domain knowledge in selection</li>
                <li>Validate selected features on holdout set</li>
              </ul>
            </div>

            <div className="card">
              <h3>📊 For Production</h3>
              <ul>
                <li>Monitor data drift for original columns</li>
                <li>Version the feature engineering pipeline</li>
                <li>Log feature statistics for anomaly detection</li>
                <li>Use the same window sizes in inference</li>
                <li>Store preprocessing parameters (mean, std)</li>
              </ul>
            </div>

            <div className="card">
              <h3>🚀 Next Steps</h3>
              <ul>
                <li>Exploratory Data Analysis (EDA) on features</li>
                <li>Feature selection/dimensionality reduction</li>
                <li>Model training and validation</li>
                <li>Hyperparameter optimization</li>
                <li>Performance evaluation & deployment</li>
              </ul>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #dee2e6', marginTop: '3rem', paddingTop: '2rem', textAlign: 'center', color: '#6c757d' }}>
        <div className="container">
          <p>T1_AD Demo | Before & After Comparison | 2026</p>
        </div>
      </footer>
    </>
  )
}
