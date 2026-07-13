# T1_AD Demo - Feature Engineering Results Dashboard

A minimal Next.js web dashboard showcasing the **T1_AD Feature Engineering & SageMaker Processing** pipeline results with real data samples.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
# Build
npm run build

# Run production server
npm start
```

## 📊 What's Displayed

- **Processing Summary** - Input/output records, features created, execution time
- **Data Transformation** - Before/after examples with raw vs engineered features
- **Feature Breakdown** - All 13 engineered features with statistics
- **Processing Configuration** - SageMaker setup and output details
- **Data Quality Metrics** - Missing values, outliers, duplicates, validity
- **Statistical Results** - Mean, std dev, min/max of transformed features
- **Pipeline Status** - Current status of each processing stage

## 📁 Project Structure

```
demo/
├── app/
│   ├── layout.tsx      # Root layout (metadata, imports)
│   ├── page.tsx        # Main demo page with sample data
│   └── globals.css     # Clean, minimal styling
├── package.json        # Next.js dependencies
├── tsconfig.json       # TypeScript config
├── next.config.js      # Next.js configuration
└── README.md          # This file
```

## 🎨 Design Philosophy

- **Minimal** - Clean, clutter-free layout
- **Clear** - Easy to scan and understand results
- **Responsive** - Works perfectly on all devices
- **Fast** - Zero external dependencies, pure CSS
- **Data-Focused** - Emphasizes the actual results

## 🔧 Customization

### Update Sample Data
Edit the data in `app/page.tsx`:
- `rawDataSample` - Before processing example
- `engineeredDataSample` - After feature engineering example
- `stats` - Processing statistics

### Modify Styling
Edit `app/globals.css` to change colors, fonts, layout, etc.

### Add New Sections
Add new `<section>` elements to `page.tsx` to display additional information.

## 📖 Related Files

- [Preprocessing Script](../../PRE_at/T1_AD/src/preprocessing.py)
- [Feature Engineering](../../PRE_at/T1_AD/src/feature_engineering.py)
- [SageMaker Processing Job](../../PRE_at/T1_AD/src/processing_job.py)

## 📝 License

Part of T1_AD Project
