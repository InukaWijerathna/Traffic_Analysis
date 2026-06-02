# Traffic Analysis

Lightweight Python tools to process, summarise and visualise CSV traffic-count data collected across dates and junctions.

## Summary
- Reads CSV files from the `data/` folder, normalises vehicle and junction names, computes metrics per date/junction, and saves human-readable summaries to `results.txt`.
- Includes a small Tkinter histogram UI (`HistogramApp`) and a CLI helper `MultiCSVProcessor` for interactive processing.

## Requirements
- Python 3.8+
- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quickstart
- Run tests:

```bash
python -m pytest -q
```

- Run the interactive processor:

```bash
python -c "from traffic_analysis import MultiCSVProcessor; MultiCSVProcessor().process_files()"
```

## Data files
Place CSV files in the `data/` directory. Sample files included:

- [data/traffic_data15062024.csv](data/traffic_data15062024.csv)
- [data/traffic_data16062024.csv](data/traffic_data16062024.csv)
- [data/traffic_data21062024.csv](data/traffic_data21062024.csv)
- [data/traffic_data22062024.csv](data/traffic_data22062024.csv)
- [data/traffic_data23062024.csv](data/traffic_data23062024.csv)
- [data/traffic_data24062024.csv](data/traffic_data24062024.csv)
- [data/traffic_data25062024.csv](data/traffic_data25062024.csv)
- [data/traffic_data26062024.csv](data/traffic_data26062024.csv)
- [data/traffic_data27062024.csv](data/traffic_data27062024.csv)
- [data/traffic_data28062024.csv](data/traffic_data28062024.csv)
- [data/traffic_data29062024.csv](data/traffic_data29062024.csv)

## Output
- Summaries appended to `results.txt` in the repository root.
- The Tkinter histogram provides a basic visualisation of junction counts.

## Tests and development
- Tests live in `tests/test_processing.py` and exercise core CSV parsing and aggregation logic.
- To extend: consider switching the visualisation to `matplotlib` for saved charts, or implement streaming aggregation for larger inputs.

---

If you'd like, I can also add a `CONTRIBUTING.md`, GitHub Actions CI, or convert visualisations to matplotlib. Which would you prefer next?
