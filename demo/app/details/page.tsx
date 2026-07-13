'use client'

import Navigation from '@/components/Navigation'

export default function DetailsPage() {
  return (
    <>
      <Navigation />
      <header>
        <div className="container">
          <h1>📋 Detailed Information</h1>
          <p>Complete documentation and technical details</p>
        </div>
      </header>

      <main className="container">
        {/* System Configuration */}
        <section>
          <h2>⚙️ System Configuration</h2>
          <div className="card-grid">
            <div className="card">
              <h3>AWS SageMaker</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Service</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>Processing Job</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Instance Type</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>ml.m5.large</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Instance Count</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>1</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Region</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>ap-southeast-1</td>
                  </tr>
                  <tr>
                    <td>Framework</td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold' }}>scikit-learn 1.2</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Python Environment</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Python</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>3.10+</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>pandas</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>2.0+</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>numpy</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>1.24+</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>scikit-learn</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>1.2+</td>
                  </tr>
                  <tr>
                    <td>boto3</td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold' }}>1.28+</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Storage Configuration</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Input Path</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>s3://bucket/processed/</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Output Path</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>s3://bucket/features/</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Input Format</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>CSV</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Output Format</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>CSV</td>
                  </tr>
                  <tr>
                    <td>Storage Class</td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold' }}>S3 Standard</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Performance Metrics</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <tbody>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Total Time</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>154 seconds</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Data Load</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>12 seconds</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Preprocessing</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>45 seconds</td>
                  </tr>
                  <tr>
                    <td style={{ paddingBottom: '0.5rem' }}>Feature Eng</td>
                    <td style={{ paddingBottom: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>78 seconds</td>
                  </tr>
                  <tr>
                    <td>Output Write</td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold' }}>19 seconds</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Data Schema */}
        <section>
          <h2>📊 Data Schema</h2>

          <h3>Input Schema (Processed Data)</h3>
          <div className="card" style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Data Type</th>
                  <th>Description</th>
                  <th>Example</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>timestamp</strong></td>
                  <td>datetime</td>
                  <td>Date/time of measurement</td>
                  <td>2024-01-01 12:00:00</td>
                </tr>
                <tr>
                  <td><strong>value</strong></td>
                  <td>float64</td>
                  <td>Primary measurement (target variable)</td>
                  <td>47.35</td>
                </tr>
                <tr>
                  <td><strong>temp</strong></td>
                  <td>float64</td>
                  <td>Temperature in Celsius</td>
                  <td>22.5</td>
                </tr>
                <tr>
                  <td><strong>humidity</strong></td>
                  <td>float64</td>
                  <td>Humidity percentage (0-100)</td>
                  <td>65.2</td>
                </tr>
                <tr>
                  <td><strong>pressure</strong></td>
                  <td>float64</td>
                  <td>Atmospheric pressure in hPa</td>
                  <td>1013.25</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h3>Output Schema (Engineered Features)</h3>
          <div className="card" style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
            <table>
              <thead>
                <tr>
                  <th>Feature Category</th>
                  <th>Generated Columns</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Original</strong></td>
                  <td>value, temp, humidity, pressure, humidity_ratio</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Rolling Mean (3)</strong></td>
                  <td>value_roll_mean_3, temp_roll_mean_3, humidity_roll_mean_3, ...</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Rolling Mean (6)</strong></td>
                  <td>value_roll_mean_6, temp_roll_mean_6, humidity_roll_mean_6, ...</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Rolling Mean (12)</strong></td>
                  <td>value_roll_mean_12, temp_roll_mean_12, humidity_roll_mean_12, ...</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Rolling Mean (24)</strong></td>
                  <td>value_roll_mean_24, temp_roll_mean_24, humidity_roll_mean_24, ...</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Rolling Std (All)</strong></td>
                  <td>*_roll_std_3, *_roll_std_6, *_roll_std_12, *_roll_std_24</td>
                  <td>20</td>
                </tr>
                <tr>
                  <td><strong>Z-Scores</strong></td>
                  <td>value_zscore, temp_zscore, humidity_zscore, ...</td>
                  <td>5</td>
                </tr>
                <tr>
                  <td><strong>Differences (Lag-1)</strong></td>
                  <td>value_diff_1, temp_diff_1, humidity_diff_1, ...</td>
                  <td>5</td>
                </tr>
                <tr style={{ background: '#f0f7ff', fontWeight: 'bold' }}>
                  <td>Total</td>
                  <td>—</td>
                  <td>45</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Feature Engineering Details */}
        <section>
          <h2>✨ Feature Engineering Algorithms</h2>

          <div className="card-grid">
            <div className="card">
              <h3>1. Rolling Statistics</h3>
              <pre><code>{`# Pseudo-code
for col in numeric_columns:
  for window in [3, 6, 12, 24]:
    df[f'{col}_roll_mean_{window}'] =
      df[col].rolling(window, min_periods=1).mean()

    df[f'{col}_roll_std_{window}'] =
      df[col].rolling(window, min_periods=1).std()

    # Fill NaN in std with 0
    df[f'{col}_roll_std_{window}'].fillna(0)`}</code></pre>
            </div>

            <div className="card">
              <h3>2. Z-Score Normalization</h3>
              <pre><code>{`# Pseudo-code
for col in numeric_columns:
  mean = df[col].mean()
  std = df[col].std()

  if std != 0:
    df[f'{col}_zscore'] =
      (df[col] - mean) / std
  else:
    df[f'{col}_zscore'] = 0.0`}</code></pre>
            </div>

            <div className="card">
              <h3>3. Lag Differences</h3>
              <pre><code>{`# Pseudo-code
for col in numeric_columns:
  for period in [1]:
    df[f'{col}_diff_{period}'] =
      df[col].diff(periods=period)

    # Fill initial NaNs
    df[f'{col}_diff_{period}'].fillna(0)`}</code></pre>
            </div>

            <div className="card">
              <h3>4. Data Cleaning</h3>
              <pre><code>{`# Pseudo-code
# Remove duplicates
df = df.drop_duplicates()

# Handle missing values
df = df.dropna() or df.fillna(strategy)

# Validate types
df = df.astype(dtype_map)

# Check ranges
assert df.columns >= min_val
assert df.columns <= max_val`}</code></pre>
            </div>
          </div>
        </section>

        {/* API Reference */}
        <section>
          <h2>🔌 Processing Job API</h2>
          <div className="card">
            <h3>Command Line Interface</h3>
            <pre><code>{`python src/processing_job.py \\
    --bucket <bucket_name> \\
    --region <aws_region> \\
    --role <iam_role_arn> \\
    [--instance-type <instance_type>] \\
    [--instance-count <count>] \\
    [--framework-version <version>]`}</code></pre>

            <h3>Arguments</h3>
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th>Argument</th>
                  <th>Type</th>
                  <th>Required</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>--bucket</code></td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>S3 bucket name for data storage</td>
                </tr>
                <tr>
                  <td><code>--region</code></td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>AWS region code (default: ap-southeast-1)</td>
                </tr>
                <tr>
                  <td><code>--role</code></td>
                  <td>string</td>
                  <td>Yes</td>
                  <td>IAM role ARN for SageMaker execution</td>
                </tr>
                <tr>
                  <td><code>--instance-type</code></td>
                  <td>string</td>
                  <td>No</td>
                  <td>Instance type (default: ml.m5.large)</td>
                </tr>
                <tr>
                  <td><code>--instance-count</code></td>
                  <td>int</td>
                  <td>No</td>
                  <td>Number of instances (default: 1)</td>
                </tr>
                <tr>
                  <td><code>--framework-version</code></td>
                  <td>string</td>
                  <td>No</td>
                  <td>scikit-learn version (default: 1.2-1)</td>
                </tr>
              </tbody>
            </table>

            <h3>Return Values</h3>
            <pre><code>{`{
  "status": "Completed|Failed|Stopped",
  "output_path": "s3://bucket/features/",
  "job_name": "feature-engineering-xxxx",
  "duration_seconds": 154
}`}</code></pre>
          </div>
        </section>

        {/* Cost Breakdown */}
        <section>
          <h2>💰 Cost Breakdown</h2>
          <div className="card-grid">
            <div className="card">
              <h3>Compute Cost</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                $0.02
              </p>
              <p style={{ color: '#6c757d' }}>
                ml.m5.large: $0.115/hour × 0.043 hours
              </p>
            </div>

            <div className="card">
              <h3>Data Transfer</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                $0.00
              </p>
              <p style={{ color: '#6c757d' }}>
                Inbound: Free | Outbound: &lt;100 GB/month free
              </p>
            </div>

            <div className="card">
              <h3>Storage (S3)</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                ~$0.00006
              </p>
              <p style={{ color: '#6c757d' }}>
                2.4 MB × $0.023/GB/month
              </p>
            </div>

            <div className="card">
              <h3>Total per Run</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#00cc00' }}>
                $0.02
              </p>
              <p style={{ color: '#6c757d' }}>
                ~20,000 VND per execution
              </p>
            </div>
          </div>
        </section>

        {/* Troubleshooting */}
        <section>
          <h2>🔧 Troubleshooting</h2>
          <div className="card-grid">
            <div className="card">
              <h3>❌ Job Failed</h3>
              <p><strong>Solution:</strong></p>
              <ul>
                <li>Check CloudWatch logs</li>
                <li>Verify IAM role permissions</li>
                <li>Confirm S3 paths are correct</li>
                <li>Check data format (CSV required)</li>
              </ul>
            </div>

            <div className="card">
              <h3>⏱️ Timeout</h3>
              <p><strong>Solution:</strong></p>
              <ul>
                <li>Increase instance type (ml.m5.xlarge)</li>
                <li>Reduce data size for testing</li>
                <li>Check for infinite loops in code</li>
                <li>Monitor memory usage</li>
              </ul>
            </div>

            <div className="card">
              <h3>💾 Out of Memory</h3>
              <p><strong>Solution:</strong></p>
              <ul>
                <li>Use larger instance type</li>
                <li>Process data in chunks</li>
                <li>Remove unused columns</li>
                <li>Use dtype optimization (int32, float32)</li>
              </ul>
            </div>

            <div className="card">
              <h3>🔐 Permission Error</h3>
              <p><strong>Solution:</strong></p>
              <ul>
                <li>Add S3:GetObject permission</li>
                <li>Add S3:PutObject permission</li>
                <li>Verify role trust relationship</li>
                <li>Check bucket policies</li>
              </ul>
            </div>
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid #dee2e6', marginTop: '3rem', paddingTop: '2rem', textAlign: 'center', color: '#6c757d' }}>
        <div className="container">
          <p>T1_AD Demo | Technical Details | 2026</p>
        </div>
      </footer>
    </>
  )
}
