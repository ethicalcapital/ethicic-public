# Performance Calculation System

## Overview

The strategy pages now have an automated performance calculation system. You only need to enter the latest month's performance data, and all other metrics (YTD, 1-year, 3-year, since inception) will be calculated automatically.

## How to Update Performance

### Via CMS (Recommended)

1. Go to `/cms/` and log in
2. Navigate to **Pages** → Find your strategy page (e.g., "Growth")
3. Click **Edit**
4. Scroll to the **📊 Performance Update - Enter New Month** section
5. Fill in:
   - **Latest month return**: e.g., "3.25%"
   - **Latest month benchmark**: e.g., "2.10%"
   - **Latest month date**: e.g., "2025-07-31"
6. Click **Save**

The system will:
- Store the monthly data in the database
- Automatically recalculate all performance metrics
- Clear the input fields
- Update the timestamp

### Via Command Line

You can also use management commands for bulk operations:

```bash
# Import historical data from CSV
python manage.py import_performance_csv --csv-file growth_performance.csv --strategy-title "Growth"

# View current performance
python manage.py show_performance --strategy "Growth"
python manage.py show_performance  # Shows all strategies
```

## What Gets Calculated

When you enter monthly data, the system automatically calculates:

- **YTD Return**: Compounds monthly returns for the current year
- **1-Year Return**: Compounds the last 12 months of returns
- **3-Year Return**: Annualized return over 3 years
- **Since Inception Return**: Annualized return since the inception date
- **Benchmark comparisons**: Same calculations for benchmark data
- **Differences**: Strategy performance minus benchmark performance

## Data Storage

- **Monthly Returns**: Stored as JSON in the database format:
  ```json
  {
    "2025": {
      "Jan": {"strategy": "2.74%", "benchmark": "3.28%"},
      "Feb": {"strategy": "2.49%", "benchmark": "-0.35%"}
    }
  }
  ```
- **Calculated Fields**: Stored as formatted percentage strings (e.g., "23.17%")

## File Structure

- `public_site/models.py` - StrategyPage model with new fields and save() method
- `public_site/utils/performance_calculator.py` - Calculation logic
- `public_site/management/commands/import_performance_csv.py` - CSV import
- `public_site/management/commands/show_performance.py` - Display performance

## Benefits

- **One-time entry**: Just enter the latest month's data
- **Automatic calculations**: All metrics update instantly
- **Historical preservation**: All monthly data is preserved
- **Error reduction**: No manual calculation of compound returns
- **Audit trail**: Performance update timestamps

## CSV Format Support

The system can import from CSV files with this format:
```
,2025,Jan,Feb,Mar,Apr,May,Jun,...
,Strategy TWR,2.74%,2.49%,-5.65%,5.92%,7.44%,5.51%,...
,MSCI ACWI TR,3.28%,-0.35%,-3.81%,0.76%,5.71%,4.64%,...
```

## Troubleshooting

- **Malformed percentages**: The parser handles common issues like "7,94%" or "94%""
- **Missing data**: Empty months are skipped in calculations
- **Inception date**: Set this field to get accurate since-inception calculations
- **Read-only fields**: Most performance fields are auto-calculated and read-only in the CMS

## Migration Notes

- Historical data was imported from `growth_performance.csv`
- Existing performance fields remain but are now auto-populated
- The system is backward compatible with manual entry if needed
