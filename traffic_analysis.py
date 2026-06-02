# Traffic Analysis System - main module
# Reimagined version of first-year coursework, main processing module

import csv
import os
import tkinter as tk
from tkinter import filedialog
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
from collections import defaultdict

# Default data directory inside the package
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


# -----------------------------
# Helpers: normalization & parsing
# -----------------------------
def normalize_vehicle_type(v):
    if not v:
        return ''
    s = v.strip().lower()
    # normalize common misspellings and variants
    if s in ('buss', 'bus'):
        return 'bus'
    if 'truck' in s:
        return 'truck'
    if 'motor' in s or 'motorcycle' in s:
        return 'motorcycle'
    if 'scooter' in s:
        return 'scooter'
    if 'bicycle' in s or 'bike' in s:
        return 'bicycle'
    if 'van' in s:
        return 'van'
    if 'car' in s:
        return 'car'
    return s


def normalize_junction_name(j):
    if not j:
        return ''
    s = j.strip()
    # canonicalize two known junctions
    low = s.lower()
    if 'elm avenue' in low or 'rabbit road' in low:
        return 'Elm Avenue/Rabbit Road'
    if 'hanley highway' in low or 'westway' in low:
        return 'Hanley Highway/Westway'
    return s


def parse_hour(time_str):
    if not time_str:
        return None
    parts = time_str.split(':')
    try:
        return int(parts[0])
    except Exception:
        return None


# -----------------------------
# Task A: Input Validation (placeholders)
# -----------------------------
def validate_date_input():
    pass

def validate_continue_input():
    pass


# -----------------------------
# Task B: Processed Outcomes
# -----------------------------
def process_csv_data(file_path):
    outcomes = {}
    junction_counts = defaultdict(int)
    rows = []
    date_found = None
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
                if not date_found:
                    date_found = row.get('Date')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None, None

    data_rows = [r for r in rows if r.get('Date') == date_found]
    total = len(data_rows)

    trucks = 0
    electric = 0
    two_wheel = 0
    buss_elm_north = 0
    no_turn_both = 0
    over_speed = 0
    elm_count = 0
    hanley_count = 0
    elm_scooters = 0

    bicycle_count = 0
    bicycle_hours = set()

    hanley_hour_counts = defaultdict(int)
    rain_hours = set()

    for r in data_rows:
        raw_junc = r.get('JunctionName') or r.get('Junction') or ''
        junc = normalize_junction_name(raw_junc)
        junction_counts[junc] += 1

        raw_vtype = r.get('VehicleType') or ''
        vtype = normalize_vehicle_type(raw_vtype)

        if vtype == 'truck':
            trucks += 1
        if (r.get('elctricHybrid') or '').strip().lower() == 'true':
            electric += 1
        if vtype in ('bicycle', 'motorcycle', 'scooter'):
            two_wheel += 1
        if junc == 'Elm Avenue/Rabbit Road' and vtype == 'bus' and (r.get('travel_Direction_out', '').strip().upper() == 'N'):
            buss_elm_north += 1
        if (r.get('travel_Direction_in') or '').strip().upper() == (r.get('travel_Direction_out') or '').strip().upper():
            no_turn_both += 1
        try:
            speed = int(float(r.get('VehicleSpeed') or 0))
            limit = int(float(r.get('JunctionSpeedLimit') or 0))
            if speed > limit:
                over_speed += 1
        except Exception:
            pass
        if junc == 'Elm Avenue/Rabbit Road':
            elm_count += 1
            if vtype == 'scooter':
                elm_scooters += 1
        if junc == 'Hanley Highway/Westway':
            hanley_count += 1

        if vtype == 'bicycle':
            bicycle_count += 1
            hour = parse_hour(r.get('timeOfDay') or '')
            if hour is not None:
                bicycle_hours.add(hour)

        if junc == 'Hanley Highway/Westway':
            hour = parse_hour(r.get('timeOfDay') or '')
            if hour is not None:
                hanley_hour_counts[str(hour)] += 1

        wc = (r.get('Weather_Conditions') or '').strip().lower()
        if 'rain' in wc:
            hour = parse_hour(r.get('timeOfDay') or '')
            if hour is not None:
                rain_hours.add(hour)

    pct_trucks = round((trucks / total) * 100) if total else 0

    hours_present = set()
    for r in data_rows:
        t = r.get('timeOfDay') or ''
        if t:
            hours_present.add(t.split(':')[0])
    num_hours = len(hours_present) if hours_present else 1
    avg_bicycles_per_hour = round(bicycle_count / num_hours) if num_hours else 0

    peak_count = 0
    peak_hours = []
    if hanley_hour_counts:
        peak_count = max(hanley_hour_counts.values())
        peak_hours = [h for h, c in hanley_hour_counts.items() if c == peak_count]

    outcomes['selected_file'] = os.path.basename(file_path)
    outcomes['date'] = date_found
    outcomes['total_vehicles'] = total
    outcomes['total_trucks'] = trucks
    outcomes['total_electric'] = electric
    outcomes['two_wheeled'] = two_wheel
    outcomes['buss_elm_north'] = buss_elm_north
    outcomes['no_turn_both'] = no_turn_both
    outcomes['pct_trucks'] = pct_trucks
    outcomes['avg_bicycles_per_hour'] = avg_bicycles_per_hour
    outcomes['total_over_speed'] = over_speed
    outcomes['total_only_elm'] = elm_count
    outcomes['total_only_hanley'] = hanley_count
    outcomes['pct_elm_scooters'] = round((elm_scooters / elm_count) * 100) if elm_count else 0
    outcomes['hanley_peak_count'] = peak_count
    outcomes['hanley_peak_hours'] = sorted(peak_hours)
    outcomes['rain_hours_count'] = len(rain_hours)

    return outcomes, dict(junction_counts)


def display_outcomes(outcomes):
    if not outcomes:
        print("No outcomes to display")
        return
    print("\n--- Processed Outcomes ---")
    print(f"Selected file: {outcomes.get('selected_file')}")
    print(f"Date: {outcomes.get('date')}")
    print(f"Total vehicles: {outcomes.get('total_vehicles')}")
    print(f"Total trucks: {outcomes.get('total_trucks')}")
    print(f"Total electric vehicles: {outcomes.get('total_electric')}")
    print(f"Two-wheeled vehicles: {outcomes.get('two_wheeled')}")
    print(f"Busses leaving Elm heading north: {outcomes.get('buss_elm_north')}")
    print(f"Vehicles without turning (in==out) across both junctions: {outcomes.get('no_turn_both')}")
    print(f"Percentage trucks: {outcomes.get('pct_trucks')}%")
    print(f"Average bicycles per hour: {outcomes.get('avg_bicycles_per_hour')}")
    print(f"Vehicles over speed limit: {outcomes.get('total_over_speed')}")
    print(f"Total through Elm Avenue/Rabbit Road: {outcomes.get('total_only_elm')}")
    print(f"Total through Hanley Highway/Westway: {outcomes.get('total_only_hanley')}")
    print(f"Percentage of Elm vehicles that are Scooters: {outcomes.get('pct_elm_scooters')}%")
    print(f"Hanley peak hour vehicle count: {outcomes.get('hanley_peak_count')}")
    if outcomes.get('hanley_peak_hours'):
        times = [f"Between {h}:00 and {int(h)+1:02d}:00" for h in outcomes.get('hanley_peak_hours')]
        print("Hanley peak hours: " + ", ".join(times))
    else:
        print("Hanley peak hours: None")
    print(f"Total hours of rain on date: {outcomes.get('rain_hours_count')}")
    print("--- End Outcomes ---\n")


RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.txt')


def save_results_to_file(outcomes, file_name=None):
    path = file_name or RESULTS_FILE
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write('--- Processed Outcomes ---\n')
            for k, v in outcomes.items():
                f.write(f"{k}: {v}\n")
            f.write('\n')
    except Exception as e:
        print(f"Failed to write results: {e}")


def plot_histogram_matplotlib(traffic_data, date, top_n=None, save_path=None):
    """Create an improved histogram using matplotlib. If `save_path` is provided,
    the figure is saved to that path; otherwise it is shown interactively."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available; please install matplotlib to use this feature.")
        return
    if not traffic_data:
        print("No data to plot")
        return
    items = sorted(traffic_data.items(), key=lambda x: x[1], reverse=True)
    if top_n:
        items = items[:top_n]
    labels = [it[0] for it in items]
    values = [it[1] for it in items]
    fig_w = max(8, len(labels) * 0.5)
    fig, ax = plt.subplots(figsize=(fig_w, 6))
    colors = plt.get_cmap('tab20').colors
    bars = ax.bar(range(len(values)), values, color=[colors[i % len(colors)] for i in range(len(values))])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title(f'Vehicle counts per junction — {date}')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(val), ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    if save_path:
        try:
            fig.savefig(save_path, dpi=150)
            print(f"Saved histogram to {save_path}")
        except Exception as e:
            print(f"Failed to save histogram: {e}")
    else:
        plt.show()
    plt.close(fig)


class HistogramApp:
    def __init__(self, traffic_data, date):
        self.traffic_data = traffic_data
        self.date = date
        self._sort_desc = True
        self.fig = None
        self.ax = None
        self._mpl_canvas = None

    def _draw_figure(self):
        self.ax.clear()
        items = sorted(self.traffic_data.items(), key=lambda x: x[1], reverse=self._sort_desc)
        labels = [it[0] for it in items]
        values = [it[1] for it in items]
        colors = plt.get_cmap('tab20').colors
        bars = self.ax.bar(
            range(len(values)),
            values,
            color=[colors[i % len(colors)] for i in range(len(values))],
        )
        self.ax.set_xticks(range(len(labels)))
        self.ax.set_xticklabels(labels, rotation=45, ha='right')
        self.ax.set_ylabel('Count')
        self.ax.set_title(f'Vehicle counts per junction — {self.date}')
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        for bar, val in zip(bars, values):
            self.ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                str(val),
                ha='center', va='bottom', fontsize=8,
            )
        self.fig.tight_layout()
        self._mpl_canvas.draw()

    def toggle_sort(self):
        self._sort_desc = not self._sort_desc
        self._draw_figure()

    def save_as_png(self):
        fname = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG Image', '*.png')])
        if not fname:
            return
        try:
            self.fig.savefig(fname, dpi=150)
            print(f"Saved histogram to {fname}")
        except Exception as e:
            print(f"Failed to save: {e}")

    def run(self):
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available; please install matplotlib.")
            return
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        root = tk.Tk()
        root.title(f"Traffic Histogram — {self.date}")

        toolbar_frame = tk.Frame(root)
        toolbar_frame.pack(fill='x', padx=6, pady=4)
        tk.Button(toolbar_frame, text='Toggle Sort', command=self.toggle_sort).pack(side='left')
        tk.Button(toolbar_frame, text='Save PNG', command=self.save_as_png).pack(side='left', padx=(6, 0))

        fig_w = max(8, len(self.traffic_data) * 0.8)
        self.fig, self.ax = plt.subplots(figsize=(fig_w, 6))
        self._mpl_canvas = FigureCanvasTkAgg(self.fig, master=root)
        self._mpl_canvas.get_tk_widget().pack(fill='both', expand=True)

        nav = NavigationToolbar2Tk(self._mpl_canvas, root)
        nav.update()

        self._draw_figure()
        root.mainloop()


class MultiCSVProcessor:
    def __init__(self):
        self.current_data = None
        self.current_date = None

    def load_csv_file(self, file_path):
        counts = defaultdict(int)
        date_found = None
        try:
            # support passing a basename or full path; prefer file_path as given
            target_path = file_path
            if not os.path.isabs(target_path) and not os.path.exists(target_path):
                candidate = os.path.join(DEFAULT_DATA_DIR, target_path)
                if os.path.exists(candidate):
                    target_path = candidate
            with open(target_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    junction = row.get('JunctionName') or row.get('Junction')
                    date = row.get('Date')
                    if not date_found and date:
                        date_found = date
                    if junction:
                        counts[junction] += 1
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {}, None
        self.current_data = dict(counts)
        self.current_date = date_found
        return self.current_data, date_found

    def clear_previous_data(self):
        self.current_data = None
        self.current_date = None

    def _list_files(self):
        data_dir = DEFAULT_DATA_DIR
        if not os.path.isdir(data_dir):
            print(f"Data directory not found: {data_dir}")
            return data_dir, []
        files = sorted(f for f in os.listdir(data_dir) if f.lower().endswith('.csv'))
        return data_dir, files

    def _print_menu(self, files):
        print()
        print("=" * 50)
        print("  Traffic Analysis — Select a file")
        print("=" * 50)
        for i, f in enumerate(files, 1):
            size_kb = os.path.getsize(os.path.join(DEFAULT_DATA_DIR, f)) // 1024
            print(f"  {i:>2}. {f}  ({size_kb} KB)")
        print()
        print(f"   a. Process ALL {len(files)} files")
        print("   q. Quit")
        print("=" * 50)

    def handle_user_interaction(self):
        data_dir, files = self._list_files()
        if not files:
            print("No CSV files found in the data directory.")
            return []
        self._print_menu(files)
        while True:
            choice = input("Enter choice: ").strip().lower()
            if choice == 'q':
                return []
            if choice == 'a':
                return [os.path.normpath(os.path.join(data_dir, f)) for f in files]
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    return [os.path.normpath(os.path.join(data_dir, files[idx]))]
            print(f"  Invalid choice. Enter a number 1–{len(files)}, 'a' for all, or 'q' to quit.")

    def _process_single(self, path):
        self.clear_previous_data()
        outcomes, junction_counts = process_csv_data(path)
        if not outcomes:
            print(f"No data found or failed to process: {os.path.basename(path)}")
            return
        display_outcomes(outcomes)
        save_results_to_file(outcomes)
        app = HistogramApp(junction_counts, outcomes.get('date') or os.path.basename(path))
        app.run()

    def _process_all(self, paths):
        combined_junctions = defaultdict(int)
        total_files = len(paths)
        agg = defaultdict(int)

        for i, path in enumerate(paths, 1):
            print(f"[{i}/{total_files}] Reading: {os.path.basename(path)}")
            outcomes, junction_counts = process_csv_data(path)
            if not outcomes:
                print(f"  Skipped — no data.")
                continue
            for key in ('total_vehicles', 'total_trucks', 'total_electric', 'two_wheeled',
                        'buss_elm_north', 'no_turn_both', 'total_over_speed',
                        'total_only_elm', 'total_only_hanley'):
                agg[key] += outcomes.get(key, 0)
            elm = outcomes.get('total_only_elm', 0)
            agg['_elm_scooters'] += round(outcomes.get('pct_elm_scooters', 0) / 100 * elm)
            for junc, count in junction_counts.items():
                combined_junctions[junc] += count

        if not agg['total_vehicles']:
            print("No data to display.")
            return

        combined = {
            'selected_file': f"All {total_files} files",
            'date': f"{total_files} dates combined",
            'total_vehicles':    agg['total_vehicles'],
            'total_trucks':      agg['total_trucks'],
            'total_electric':    agg['total_electric'],
            'two_wheeled':       agg['two_wheeled'],
            'buss_elm_north':    agg['buss_elm_north'],
            'no_turn_both':      agg['no_turn_both'],
            'pct_trucks':        round(agg['total_trucks'] / agg['total_vehicles'] * 100),
            'avg_bicycles_per_hour': 'N/A',
            'total_over_speed':  agg['total_over_speed'],
            'total_only_elm':    agg['total_only_elm'],
            'total_only_hanley': agg['total_only_hanley'],
            'pct_elm_scooters':  round(agg['_elm_scooters'] / agg['total_only_elm'] * 100) if agg['total_only_elm'] else 0,
            'hanley_peak_count': 'N/A',
            'hanley_peak_hours': [],
            'rain_hours_count':  'N/A',
        }

        display_outcomes(combined)
        save_results_to_file(combined)
        app = HistogramApp(dict(combined_junctions), f"All {total_files} files combined")
        app.run()

    def process_files(self):
        while True:
            selected = self.handle_user_interaction()
            if not selected:
                print("Exiting processor.")
                break

            if len(selected) == 1:
                self._process_single(selected[0])
            else:
                self._process_all(selected)

            print()
            print("  R — Run another analysis")
            print("  Q — Quit")
            while True:
                cont = input("Enter choice: ").strip().upper()
                if cont in ('R', 'Q'):
                    break
                print("  Please enter 'R' to run again or 'Q' to quit.")
            if cont == 'Q':
                print("Finished.")
                break


if __name__ == '__main__':
    proc = MultiCSVProcessor()
    proc.process_files()
