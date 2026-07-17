'use client'

import Navigation from '@/components/Navigation'
import dynamic from 'next/dynamic'

const ZScoreChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.ZScoreChart })), { ssr: false })
const FeatureDistributionChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.FeatureDistributionChart })), { ssr: false })
const DataQualityChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.DataQualityChart })), { ssr: false })
const RollingStatsChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.RollingStatsChart })), { ssr: false })

export default function AnalysisPage() {
  return (
    <>
      <Navigation />
      <header>
        <div className="container">
          <h1>📊 Feature Analysis</h1>
          <p>Detailed statistical analysis of engineered features</p>
        </div>
      </header>

      <main className="container">
        {/* Feature Distribution */}
        <section>
          <h2>Feature Distribution</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Feature Type Breakdown</h3>
              <FeatureDistributionChart />
              <table style={{ width: '100%', marginTop: '1.5rem', textAlign: 'center' }}>
                <tbody>
                  <tr>
                    <td><strong>Rolling Mean:</strong> 20 features</td>
                  </tr>
                  <tr>
                    <td><strong>Rolling Std:</strong> 20 features</td>
                  </tr>
                  <tr>
                    <td><strong>Z-Scores:</strong> 5 features</td>
                  </tr>
                  <tr>
                    <td><strong>Differences:</strong> 5 features</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Statistics by Window Size</h3>
              <RollingStatsChart />
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
                Larger windows produce smoother trends with lower variance.
              </p>
            </div>
          </div>
        </section>

        {/* Z-Score Analysis */}
        <section>
          <h2>Z-Score Distribution</h2>
          <div className="card">
            <h3>Normalized Feature Distribution</h3>
            <ZScoreChart />
            <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
              <div>
                <h4 style={{ marginBottom: '0.5rem' }}>Mean = 0</h4>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Distribution is centered around 0, as expected for z-scores.
                </p>
              </div>
              <div>
                <h4 style={{ marginBottom: '0.5rem' }}>Std = 1</h4>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Standard deviation normalized to 1 unit.
                </p>
              </div>
              <div>
                <h4 style={{ marginBottom: '0.5rem' }}>Outliers</h4>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  Values beyond ±3σ considered outliers (24 detected).
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Data Quality */}
        <section>
          <h2>📈 Data Quality Metrics</h2>
          <div className="card">
            <h3>Quality Score by Dimension</h3>
            <DataQualityChart />
            <div style={{ marginTop: '2rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div className="card">
                <p><strong>Completeness</strong></p>
                <p style={{ fontSize: '2rem', color: '#00cc00' }}>100%</p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>No missing values</p>
              </div>
              <div className="card">
                <p><strong>Validity</strong></p>
                <p style={{ fontSize: '2rem', color: '#00cc00' }}>99.87%</p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>Valid data points</p>
              </div>
              <div className="card">
                <p><strong>Uniqueness</strong></p>
                <p style={{ fontSize: '2rem', color: '#00cc00' }}>99.87%</p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>Unique records</p>
              </div>
              <div className="card">
                <p><strong>Timeliness</strong></p>
                <p style={{ fontSize: '2rem', color: '#00cc00' }}>100%</p>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>Current data</p>
              </div>
            </div>
          </div>
        </section>

        {/* Detailed Statistics */}
        <section>
          <h2>Detailed Feature Statistics</h2>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>Mean</th>
                  <th>Std Dev</th>
                  <th>Min</th>
                  <th>Max</th>
                  <th>Skewness</th>
                  <th>Kurtosis</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>value</strong></td>
                  <td>47.34</td>
                  <td>2.15</td>
                  <td>44.22</td>
                  <td>51.87</td>
                  <td>0.18</td>
                  <td>-0.45</td>
                </tr>
                <tr>
                  <td><strong>value_roll_mean_3</strong></td>
                  <td>47.31</td>
                  <td>1.98</td>
                  <td>45.12</td>
                  <td>50.23</td>
                  <td>0.12</td>
                  <td>-0.32</td>
                </tr>
                <tr>
                  <td><strong>value_roll_std_3</strong></td>
                  <td>1.24</td>
                  <td>0.45</td>
                  <td>0.12</td>
                  <td>2.89</td>
                  <td>0.87</td>
                  <td>1.23</td>
                </tr>
                <tr>
                  <td><strong>value_zscore</strong></td>
                  <td>0.00</td>
                  <td>1.00</td>
                  <td>-1.45</td>
                  <td>2.12</td>
                  <td>0.18</td>
                  <td>-0.45</td>
                </tr>
                <tr>
                  <td><strong>value_diff_1</strong></td>
                  <td>0.05</td>
                  <td>1.35</td>
                  <td>-3.21</td>
                  <td>3.18</td>
                  <td>0.02</td>
                  <td>0.54</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Correlation Analysis */}
        <section>
          <h2>Feature Correlations</h2>
          <div className="card">
            <h3>Pearson Correlation Matrix (Sample)</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ fontSize: '0.9rem' }}>
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>value</th>
                    <th>roll_mean_3</th>
                    <th>roll_mean_6</th>
                    <th>zscore</th>
                    <th>diff_1</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>value</strong></td>
                    <td style={{ background: '#e8f4f8' }}>1.00</td>
                    <td>0.98</td>
                    <td>0.92</td>
                    <td>0.99</td>
                    <td>0.41</td>
                  </tr>
                  <tr>
                    <td><strong>roll_mean_3</strong></td>
                    <td>0.98</td>
                    <td style={{ background: '#e8f4f8' }}>1.00</td>
                    <td>0.97</td>
                    <td>0.98</td>
                    <td>0.35</td>
                  </tr>
                  <tr>
                    <td><strong>roll_mean_6</strong></td>
                    <td>0.92</td>
                    <td>0.97</td>
                    <td style={{ background: '#e8f4f8' }}>1.00</td>
                    <td>0.92</td>
                    <td>0.22</td>
                  </tr>
                  <tr>
                    <td><strong>zscore</strong></td>
                    <td>0.99</td>
                    <td>0.98</td>
                    <td>0.92</td>
                    <td style={{ background: '#e8f4f8' }}>1.00</td>
                    <td>0.41</td>
                  </tr>
                  <tr>
                    <td><strong>diff_1</strong></td>
                    <td>0.41</td>
                    <td>0.35</td>
                    <td>0.22</td>
                    <td>0.41</td>
                    <td style={{ background: '#e8f4f8' }}>1.00</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p style={{ marginTop: '1rem', color: '#6c757d' }}>
              <strong>Note:</strong> High correlation between value and derivatives indicates strong feature dependency. Differences show moderate correlation, useful for capturing trends.
            </p>
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #dee2e6', marginTop: '3rem', paddingTop: '2rem', textAlign: 'center', color: '#6c757d' }}>
        <div className="container">
          <p>T1_AD Demo | Feature Analysis | 2026</p>
        </div>
      </footer>
    </>
  )
}
