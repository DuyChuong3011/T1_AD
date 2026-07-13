'use client'

import Navigation from '@/components/Navigation'
import dynamic from 'next/dynamic'

const TimeSeriesChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.TimeSeriesChart })), { ssr: false })
const RollingStatsChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.RollingStatsChart })), { ssr: false })
const FeatureLagChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.FeatureLagChart })), { ssr: false })
const ProcessingTimeChart = dynamic(() => import('@/components/Charts').then(m => ({ default: m.ProcessingTimeChart })), { ssr: false })

export default function TransformationPage() {
  return (
    <>
      <Navigation />
      <header>
        <div className="container">
          <h1>🔄 Data Transformation</h1>
          <p>Visualize how raw data is transformed through feature engineering</p>
        </div>
      </header>

      <main className="container">
        {/* Original vs Processed */}
        <section>
          <h2>Original vs Processed Time Series</h2>
          <div className="card">
            <p style={{ marginBottom: '1.5rem' }}>
              The chart below shows the original values alongside the rolling mean smoothing applied during preprocessing.
            </p>
            <TimeSeriesChart />
          </div>
        </section>

        {/* Rolling Statistics */}
        <section>
          <h2>Rolling Window Statistics</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Rolling Mean vs Std Dev</h3>
              <RollingStatsChart />
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
                Shows how rolling mean and standard deviation vary across different window sizes (3, 6, 12, 24).
              </p>
            </div>

            <div className="card">
              <h3>Feature Lag Autocorrelation</h3>
              <FeatureLagChart />
              <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#6c757d' }}>
                Autocorrelation decay over lag periods helps identify temporal dependencies.
              </p>
            </div>
          </div>
        </section>

        {/* Processing Pipeline */}
        <section>
          <h2>Processing Pipeline Timeline</h2>
          <div className="card">
            <h3>Stage Duration Breakdown</h3>
            <ProcessingTimeChart />
            <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  <strong>Data Load:</strong> Loading raw data from S3
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  <strong>Preprocessing:</strong> Cleaning and validation
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  <strong>Feature Eng:</strong> Creating engineered features
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  <strong>Validation:</strong> Quality checks
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.9rem', color: '#6c757d' }}>
                  <strong>Output Write:</strong> Saving results
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Transformation Details */}
        <section>
          <h2>Applied Transformations</h2>
          <div className="card-grid">
            <div className="card">
              <h3>1. Rolling Statistics</h3>
              <p>
                Calculates rolling mean and standard deviation across multiple window sizes.
              </p>
              <pre><code>{`Windows: [3, 6, 12, 24]
For each window:
  - mean = rolling_mean(value, window)
  - std = rolling_std(value, window)
Result: 8 new features`}</code></pre>
            </div>

            <div className="card">
              <h3>2. Z-Score Normalization</h3>
              <p>
                Standardizes values to have mean 0 and std 1.
              </p>
              <pre><code>{`For each column:
  z_score = (value - mean) / std_dev

Useful for:
  - Outlier detection
  - Algorithm normalization
  - Interpretability`}</code></pre>
            </div>

            <div className="card">
              <h3>3. Lag Differences</h3>
              <p>
                Calculates differences between consecutive values.
              </p>
              <pre><code>{`For each column:
  diff_1 = current_value - previous_value

Captures:
  - Trend changes
  - Volatility
  - Momentum`}</code></pre>
            </div>

            <div className="card">
              <h3>4. Data Validation</h3>
              <p>
                Ensures data quality throughout the pipeline.
              </p>
              <pre><code>{`Checks performed:
  - Missing value detection
  - Outlier identification
  - Duplicate removal
  - Type validation`}</code></pre>
            </div>
          </div>
        </section>

        {/* Key Insights */}
        <section>
          <h2>💡 Key Insights</h2>
          <div className="card-grid">
            <div className="card">
              <h3>📊 Data Reduction</h3>
              <p>20 duplicate records were identified and removed during preprocessing.</p>
              <p className="badge badge-info">99.87% unique records</p>
            </div>

            <div className="card">
              <h3>📈 Feature Explosion</h3>
              <p>5 original columns expanded to 45 total features (40 engineered).</p>
              <p className="badge badge-warning">8x feature enrichment</p>
            </div>

            <div className="card">
              <h3>⚡ Processing Efficiency</h3>
              <p>Feature engineering completed in 78 seconds on SageMaker ml.m5.large.</p>
              <p className="badge badge-success">Optimized pipeline</p>
            </div>

            <div className="card">
              <h3>✅ Data Quality</h3>
              <p>99.87% of records passed validation with no missing values.</p>
              <p className="badge badge-success">Production ready</p>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #dee2e6', marginTop: '3rem', paddingTop: '2rem', textAlign: 'center', color: '#6c757d' }}>
        <div className="container">
          <p>T1_AD Demo | Data Transformation Pipeline | 2026</p>
        </div>
      </footer>
    </>
  )
}
