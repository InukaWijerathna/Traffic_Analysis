# Traffic Analysis System

This repository contains a reimagined version of my first-year programming coursework. The original project processed traffic CSV data; this updated system supports more advanced Features like data cleaning, analysis, and visualization.

## What it is
- A small Python package that reads traffic CSV files and computes useful metrics per date and junction.
- Produces a simple Tkinter histogram of vehicle counts per junction.
- Saves textual summaries to `results.txt` when run.

## Key functions
- `process_csv_data(file_path)`: parses a CSV, normalises vehicle and junction names, and computes metrics (totals, trucks, electrics, two-wheeled counts, buses heading north from Elm, no-turn vehicles, percent trucks, average bicycles per hour, over-speed counts, peak hours for Hanley, and rain hours).
- `display_outcomes(outcomes)`: prints a readable summary of calculated metrics.
- `save_results_to_file(outcomes, file_name)`: appends the summary to a text file.
- `HistogramApp`: lightweight Tkinter-based histogram UI to visualise junction counts.
- `MultiCSVProcessor`: interactive CLI loop to choose CSV files and run the analyses/UI.

## Improvements over original coursework
- Normalisation: vehicle types and junction names are cleaned to avoid miscounts from misspellings or inconsistent naming.
- Modularity: code split into helper functions and clearer structure for easier testing and extension.
- Tests: a simple pytest test verifies processing on the sample CSV.
- Outputs: results are both printed and appended to a `results.txt` file for record-keeping.

## How to run
1. Ensure Python 3 is installed.
2. (Optional) Create a virtual environment.
3. From the workspace root run:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -c "from traffic_analysis import MultiCSVProcessor; MultiCSVProcessor().process_files()"
```

## Notes and next steps
- The input validation functions are placeholders — they can be implemented to provide stricter CLI validation and a date-picker UI.
- Visualization could be improved by switching to `matplotlib` or `plotly` for richer charts and image export.
- For large datasets, streaming aggregation and caching would improve performance.

If you want, I can implement stricter validations, add matplotlib charts, or wire a simple GUI control panel.
