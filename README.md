# Traffic Analysis

Lightweight Python tools to process, summarise, and visualise CSV traffic-count data collected across multiple dates and junctions.

## Features

- Reads one or more CSV files from the `data/` folder
- Normalises vehicle types (handles misspellings: `buss` → `bus`, etc.) and canonicalises junction names
- Computes per-date metrics including:
  - Total vehicles, trucks, electric/hybrid, and two-wheeled counts
  - Buses leaving Elm Avenue/Rabbit Road heading north
  - Vehicles that did not turn (same entry and exit direction)
  - Percentage of trucks and Elm Avenue scooters
  - Average bicycles per hour
  - Vehicles exceeding the speed limit
  - Peak hour(s) at Hanley Highway/Westway
  - Number of rainy hours
- Appends human-readable summaries to `results.txt`
- Interactive matplotlib histogram embedded in a Tkinter window — toggle sort order, save PNG
- Batch mode aggregates all files into a combined summary

## Requirements

- Python 3.9+
- matplotlib (for histogram visualisation)
- pytest (for tests)

```bash
python -m pip install -r requirements.txt
```

## Quickstart

Run the interactive processor:

```bash
python traffic_analysis.py
```

Or invoke it from a script:

```bash
python -c "from traffic_analysis import MultiCSVProcessor; MultiCSVProcessor().process_files()"
```

The menu lets you pick a single date file or process all files at once.

## Running tests

```bash
python -m pytest -q
```

CI runs tests against Python 3.9, 3.10, and 3.11 on every push and pull request to `main`.

## Project structure

```
Traffic_Analysis/
├── traffic_analysis.py      # Core processing, histogram UI, CLI processor
├── data/                    # CSV input files (traffic_dataXX062024.csv)
├── results.txt              # Appended output summaries
├── tests/
│   └── test_processing.py   # pytest tests for CSV parsing and aggregation
└── requirements.txt
```

## Data files

Place CSV files in the `data/` directory. Each file should contain columns including `Date`, `JunctionName`, `VehicleType`, `VehicleSpeed`, `JunctionSpeedLimit`, `timeOfDay`, `elctricHybrid`, `travel_Direction_in`, `travel_Direction_out`, and `Weather_Conditions`.

Sample files covering 15–29 June 2024 are included in `data/`.

## Output

- Metrics for each processed file are printed to the terminal and appended to `results.txt`.
- An interactive matplotlib histogram shows vehicle counts per junction, embedded in a Tkinter window with toggle-sort and save-PNG controls.
