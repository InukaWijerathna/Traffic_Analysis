# Traffic Analysis System - main module
# Reimagined version of first-year coursework, main processing module

import csv
import os
import tkinter as tk
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


def save_results_to_file(outcomes, file_name="results.txt"):
    try:
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write('--- Processed Outcomes ---\n')
            for k, v in outcomes.items():
                f.write(f"{k}: {v}\n")
            f.write('\n')
    except Exception as e:
        print(f"Failed to write results: {e}")


class HistogramApp:
    def __init__(self, traffic_data, date):
        self.traffic_data = traffic_data
        self.date = date
        self.root = tk.Tk()
        self.canvas = None

    def setup_window(self):
        self.root.title(f"Traffic Histogram - {self.date}")
        width, height = 900, 600
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack()
        self.width = width
        self.height = height

    def draw_histogram(self):
        if not self.traffic_data:
            self.canvas.create_text(self.width // 2, self.height // 2, text="No data to display", font=("Arial", 16))
            return
        items = sorted(self.traffic_data.items(), key=lambda x: x[1], reverse=True)
        values = [t[1] for t in items]
        left_margin = 100
        right_margin = 50
        top_margin = 50
        bottom_margin = 100
        plot_width = self.width - left_margin - right_margin
        plot_height = self.height - top_margin - bottom_margin
        self.canvas.create_line(left_margin, top_margin, left_margin, top_margin + plot_height, width=2)
        self.canvas.create_line(left_margin, top_margin + plot_height, left_margin + plot_width, top_margin + plot_height, width=2)
        max_val = max(values) if values else 1
        bar_width = max(20, plot_width // (len(values) * 2))
        spacing = (plot_width - bar_width * len(values)) // (len(values) + 1)
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]
        x = left_margin + spacing
        for i, (label, val) in enumerate(items):
            h = int((val / max_val) * (plot_height - 20))
            y0 = top_margin + plot_height - h
            y1 = top_margin + plot_height
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(x, y0, x + bar_width, y1, fill=color, outline="black")
            self.canvas.create_text(x + bar_width // 2, y1 + 12, text=label, angle=45, anchor="nw", font=("Arial", 9))
            self.canvas.create_text(x + bar_width // 2, y0 - 10, text=str(val), font=("Arial", 9))
            x += bar_width + spacing
        self.canvas.create_text(self.width // 2, 20, text=f"Vehicle counts per junction — {self.date}", font=("Arial", 14, "bold"))
        self.canvas.create_text(40, top_margin + plot_height // 2, text="Count", angle=90, font=("Arial", 12))
        self.add_legend()

    def add_legend(self):
        legend_x = self.width - 200
        legend_y = 60
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]
        for i, label in enumerate(list(self.traffic_data.keys())[:8]):
            y = legend_y + i * 20
            self.canvas.create_rectangle(legend_x, y, legend_x + 15, y + 12, fill=colors[i % len(colors)], outline="black")
            self.canvas.create_text(legend_x + 20, y + 6, anchor="w", text=label, font=("Arial", 9))

    def run(self):
        self.setup_window()
        self.draw_histogram()
        self.root.mainloop()


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

    def handle_user_interaction(self):
        data_dir = DEFAULT_DATA_DIR
        if not os.path.isdir(data_dir):
            print(f"Data directory not found: {data_dir}")
            return None
        files = [f for f in os.listdir(data_dir) if f.lower().endswith('.csv')]
        if not files:
            print("No CSV files found in the data directory.")
            return None
        print("Available CSV files:")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {f}")
        while True:
            choice = input("Enter file number to process (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
                print("Invalid choice. Please enter a valid number.")
                continue
            idx = int(choice) - 1
            return os.path.normpath(os.path.join(data_dir, files[idx]))

    def process_files(self):
        while True:
            selected = self.handle_user_interaction()
            if not selected:
                print("Exiting processor.")
                break
            self.clear_previous_data()
            outcomes, junction_counts = process_csv_data(selected)
            if not outcomes:
                print("No data found or failed to process file.")
            else:
                display_outcomes(outcomes)
                save_results_to_file(outcomes, file_name='results.txt')
                app = HistogramApp(junction_counts, outcomes.get('date') or selected)
                app.run()
            while True:
                cont = input("Process another file? (Y/N): ").strip().upper()
                if cont in ('Y', 'N'):
                    break
                print("Please enter 'Y' or 'N'.")
            if cont == 'N':
                print("Finished processing files.")
                break


if __name__ == '__main__':
    proc = MultiCSVProcessor()
    proc.process_files()
