# Traffic Analysis System - main module
# Reimagined version of first-year coursework, main processing module

import csv
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, ttk
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
from collections import defaultdict

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


# ─────────────────────────── Terminal helpers ─────────────────────────────────

# Force UTF-8 output on Windows so box-drawing chars render correctly
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

_USE_COLOR = sys.stdout.isatty()

if _USE_COLOR and sys.platform == 'win32':
    import ctypes
    try:
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        _USE_COLOR = False


def _c(code):
    return code if _USE_COLOR else ''


RST = _c('\033[0m');  BOLD = _c('\033[1m');  DIM  = _c('\033[2m')
RED = _c('\033[91m'); GRN  = _c('\033[92m'); YLW  = _c('\033[93m')
BLU = _c('\033[94m'); CYN  = _c('\033[96m'); WHT  = _c('\033[97m')
MGT = _c('\033[95m')

# Box-drawing chars with ASCII fallback for terminals that can't render Unicode
try:
    '╔═╗║╚╝├┤'.encode(sys.stdout.encoding or 'ascii')
    _B = dict(tl='╔', tr='╗', bl='╚', br='╝', h='═', v='║',
              hl='─', ml='├', mr='┤', cx='┼', mj='╠', rj='╣', tj='╦', bj='╩')
except (UnicodeEncodeError, LookupError):
    _B = dict(tl='+', tr='+', bl='+', br='+', h='=', v='|',
              hl='-', ml='+', mr='+', cx='+', mj='+', rj='+', tj='+', bj='+')

_W = 64  # column budget


def _rule():
    print(f"{DIM}{'─' * _W}{RST}")


def _thick_rule():
    print(f"{CYN}{_B['h'] * _W}{RST}")


def _section(title):
    print(f"{YLW}{BOLD}  {title}{RST}")
    print(f"{DIM}  {'─' * len(title)}{RST}")


def _metric(label, value, unit='', color=WHT):
    line = f"    {DIM}{label:<40}{RST}{color}{BOLD}{value}{RST}"
    if unit:
        line += f" {DIM}{unit}{RST}"
    print(line)


def _error(msg):
    print(f"\n  {RED}{BOLD}✗  {msg}{RST}")


def _success(msg):
    print(f"  {GRN}{BOLD}✓  {msg}{RST}")


def _info(msg):
    print(f"  {CYN}ℹ  {msg}{RST}")


def _prompt(msg):
    try:
        return input(f"\n  {YLW}{BOLD}{msg}{RST} ")
    except (KeyboardInterrupt, EOFError):
        print()
        return 'q'


def _parse_date_from_filename(fname):
    m = re.search(r'(\d{2})(\d{2})(\d{4})', fname)
    return f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else '—'


def print_banner():
    inner = _W - 2
    print(f"\n{BLU}{BOLD}")
    print(_B['tl'] + _B['h'] * inner + _B['tr'])
    print(_B['v']  + ' ' * inner         + _B['v'])
    print(_B['v']  + 'TRAFFIC  ANALYSIS  SYSTEM'.center(inner) + _B['v'])
    print(_B['v']  + 'Junction Data Processor'.center(inner)   + _B['v'])
    print(_B['v']  + ' ' * inner         + _B['v'])
    print(_B['bl'] + _B['h'] * inner + _B['br'])
    print(RST)


# -----------------------------
# Helpers: normalization & parsing
# -----------------------------
def normalize_vehicle_type(v):
    if not v:
        return ''
    s = v.strip().lower()
    if s in ('buss', 'bus'):
        return 'bus'
    if 'truck' in s:
        return 'truck'
    if 'motor' in s or 'motorbike' in s or 'motorcycle' in s:
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
        _error(f"File not found: {file_path}")
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
    outcomes['junction_breakdown'] = dict(junction_counts)

    return outcomes, dict(junction_counts)


def display_outcomes(outcomes):
    if not outcomes:
        _error("No outcomes to display.")
        return

    print()
    _thick_rule()
    title = f"  Results  ·  {outcomes.get('selected_file')}  ·  {outcomes.get('date')}"
    print(f"{CYN}{BOLD}{title}{RST}")
    _thick_rule()

    # ── Overview ──────────────────────────────────────────────────────────────
    _section("Overview")
    _metric("Total vehicles recorded", outcomes.get('total_vehicles'))

    # ── Vehicle breakdown ─────────────────────────────────────────────────────
    _section("Vehicle Breakdown")
    _metric("Trucks",                  outcomes.get('total_trucks'))
    _metric("Electric / hybrid",       outcomes.get('total_electric'), color=GRN)
    _metric("Two-wheeled",             outcomes.get('two_wheeled'))
    _metric("Average bicycles per hour", outcomes.get('avg_bicycles_per_hour'))

    # ── Speed & safety ────────────────────────────────────────────────────────
    _section("Speed & Safety")
    over = outcomes.get('total_over_speed', 0)
    over_color = RED if over > 0 else GRN
    _metric("Vehicles over speed limit", over, color=over_color)
    pct = outcomes.get('pct_trucks', 0)
    _metric("Trucks as % of total",    f"{pct}%",
            color=YLW if pct >= 10 else WHT)

    # ── Junction breakdown ────────────────────────────────────────────────────
    _section("Junction Breakdown")
    breakdown = outcomes.get('junction_breakdown') or {}
    for jname, count in sorted(breakdown.items(), key=lambda x: -x[1]):
        _metric(f"Through {jname}", count)
    if 'Elm Avenue/Rabbit Road' in breakdown:
        _metric("Elm scooters as % of Elm traffic", f"{outcomes.get('pct_elm_scooters')}%")
        _metric("Buses leaving Elm heading north",  outcomes.get('buss_elm_north'))

    # ── Traffic patterns ──────────────────────────────────────────────────────
    _section("Traffic Patterns")
    _metric("Vehicles with no direction change",  outcomes.get('no_turn_both'))

    # ── Weather ───────────────────────────────────────────────────────────────
    _section("Weather")
    rain = outcomes.get('rain_hours_count', 0)
    _metric("Hours of rain recorded", rain,
            color=CYN if rain > 0 else WHT)

    print()
    _thick_rule()
    print()


def save_results_to_file(outcomes, file_name="results.txt"):
    try:
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write('--- Processed Outcomes ---\n')
            for k, v in outcomes.items():
                f.write(f"{k}: {v}\n")
            f.write('\n')
    except Exception as e:
        _error(f"Failed to write results: {e}")


def plot_histogram_matplotlib(traffic_data, date, top_n=None, save_path=None):
    """Build the histogram figure. Returns the figure, or None when saving to file."""
    if not MATPLOTLIB_AVAILABLE:
        _error("Matplotlib not available; pip install matplotlib to enable this feature.")
        return None
    if not traffic_data:
        _error("No data to plot.")
        return None
    items = sorted(traffic_data.items(), key=lambda x: x[1], reverse=True)
    if top_n:
        items = items[:top_n]
    labels = [it[0] for it in items]
    values = [it[1] for it in items]
    fig_w = max(8, len(labels) * 0.5)
    fig, ax = plt.subplots(figsize=(fig_w, 6))
    colors = plt.get_cmap('tab20').colors
    bars = ax.bar(range(len(values)), values,
                  color=[colors[i % len(colors)] for i in range(len(values))])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title(f'Vehicle counts per junction — {date}')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(val),
                ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    if save_path:
        try:
            fig.savefig(save_path, dpi=150)
            _success(f"Saved histogram to {save_path}")
        except Exception as e:
            _error(f"Failed to save histogram: {e}")
        plt.close(fig)
        return None
    return fig


def _draw_junction_ax(ax, jname, count, max_count, color):
    from matplotlib.patches import FancyBboxPatch, Rectangle

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('white')

    # Card border
    ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                boxstyle='round,pad=0.02',
                                facecolor='white', edgecolor=color, linewidth=1.5))

    # Coloured header
    ax.add_patch(Rectangle((0.02, 0.82), 0.96, 0.16, facecolor=color, edgecolor='none'))
    ax.text(0.5, 0.90, jname, ha='center', va='center',
            fontsize=8, fontweight='bold', color='white')

    # Road intersection
    parts = jname.split('/')
    road1 = parts[0].strip()
    road2 = parts[1].strip() if len(parts) > 1 else ''

    cx, cy, arm = 0.5, 0.52, 0.26
    ax.plot([cx - arm, cx + arm], [cy, cy], color=color, linewidth=4, solid_capstyle='round')
    ax.plot([cx, cx], [cy - arm, cy + arm], color=color, linewidth=4, solid_capstyle='round')
    ax.plot(cx, cy, 'o', color=color,   markersize=11, zorder=5)
    ax.plot(cx, cy, 'o', color='white', markersize=5,  zorder=6)

    fc = '#444'
    ax.text(cx - arm - 0.03, cy, road1, ha='right',  va='center', fontsize=6.5, color=fc)
    ax.text(cx + arm + 0.03, cy, road1, ha='left',   va='center', fontsize=6.5, color=fc)
    ax.text(cx, cy + arm + 0.04, road2, ha='center', va='bottom', fontsize=6.5, color=fc)
    ax.text(cx, cy - arm - 0.04, road2, ha='center', va='top',    fontsize=6.5, color=fc)

    # Count bar
    bx, by, bw, bh = 0.08, 0.13, 0.84, 0.07
    ax.add_patch(Rectangle((bx, by), bw, bh, facecolor='#e0e0e0', edgecolor='#bbb', linewidth=0.5))
    fill = bw * (count / max_count) if max_count else 0
    if fill > 0:
        ax.add_patch(Rectangle((bx, by), fill, bh, facecolor=color, edgecolor='none'))

    ax.text(0.5, 0.062, f'{count:,} vehicles', ha='center', va='center',
            fontsize=9, fontweight='bold', color='#222')


def plot_junctions_matplotlib(traffic_data, date):
    """Build the junction-cards figure. Returns the figure."""
    if not MATPLOTLIB_AVAILABLE or not traffic_data:
        return None

    items = sorted(traffic_data.items(), key=lambda x: -x[1])
    n = len(items)
    max_count = items[0][1] if items else 1
    colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
              "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]

    cols = min(3, n)
    rows = (n + cols - 1) // cols

    fig = plt.figure(figsize=(cols * 4.5, rows * 4.2 + 0.6), facecolor='#f0f2f5')
    fig.suptitle(f'Junction Breakdown  —  {date}', fontsize=13, fontweight='bold')

    for i, (jname, count) in enumerate(items):
        ax = fig.add_subplot(rows, cols, i + 1)
        _draw_junction_ax(ax, jname, count, max_count, colors[i % len(colors)])

    for j in range(n, rows * cols):
        fig.add_subplot(rows, cols, j + 1).axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    return fig


class HistogramApp:
    def __init__(self, traffic_data, date):
        self.traffic_data = traffic_data
        self.date = date
        self.root = None
        self.canvas = None
        self.junction_canvas = None
        self._bar_items = []
        self._sort_desc = True
        self.tooltip = None

    def setup_window(self):
        self.root = tk.Tk()
        self.root.title(f"Junction View — {self.date}")
        self.root.geometry("960x680")

        jf = tk.Frame(self.root)
        jf.pack(fill='both', expand=True)
        self.junction_canvas = tk.Canvas(jf, bg='#f0f2f5')
        jvbar = tk.Scrollbar(jf, orient='vertical', command=self.junction_canvas.yview)
        self.junction_canvas.configure(yscrollcommand=jvbar.set)
        jvbar.pack(side='right', fill='y')
        self.junction_canvas.pack(side='left', fill='both', expand=True)
        self.junction_canvas.bind(
            '<MouseWheel>',
            lambda e: self.junction_canvas.yview_scroll(-1 * (e.delta // 120), 'units')
        )

    def draw_histogram(self):
        if not self.traffic_data:
            self.canvas.create_text(self.width // 2, self.height // 2,
                                    text="No data to display", font=("Arial", 16))
            return
        items = sorted(self.traffic_data.items(), key=lambda x: x[1], reverse=self._sort_desc)
        values = [t[1] for t in items]
        left_margin = 100; right_margin = 50; top_margin = 50; bottom_margin = 100
        plot_width  = self.width  - left_margin - right_margin
        plot_height = self.height - top_margin  - bottom_margin
        self.canvas.create_line(left_margin, top_margin, left_margin, top_margin + plot_height, width=2)
        self.canvas.create_line(left_margin, top_margin + plot_height,
                                left_margin + plot_width, top_margin + plot_height, width=2)
        max_val = max(values) if values else 1
        bar_width = max(20, min(40, plot_width // (len(values) * 2)))
        spacing = 20
        total_plot_width = left_margin + right_margin + (bar_width + spacing) * len(values) + spacing
        scroll_w = max(total_plot_width, self.width)
        self.canvas.configure(scrollregion=(0, 0, scroll_w, self.height))
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
                  "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]
        x = left_margin + spacing
        self._bar_items.clear()
        for i, (label, val) in enumerate(items):
            h   = int((val / max_val) * (plot_height - 20))
            y0  = top_margin + plot_height - h
            y1  = top_margin + plot_height
            color = colors[i % len(colors)]
            rect_id = self.canvas.create_rectangle(x, y0, x + bar_width, y1,
                                                   fill=color, outline="black", tags=(f'bar{i}',))
            self.canvas.create_text(x + bar_width // 2, y1 + 12, text=label,
                                    angle=45, anchor="nw", font=("Arial", 9))
            self.canvas.create_text(x + bar_width // 2, y0 - 10, text=str(val), font=("Arial", 9))
            self.canvas.tag_bind(rect_id, '<Enter>',  lambda e, L=label, V=val: self._show_tooltip(e, L, V))
            self.canvas.tag_bind(rect_id, '<Leave>',  lambda e: self._hide_tooltip())
            self.canvas.tag_bind(rect_id, '<Motion>', lambda e: self._move_tooltip(e))
            self._bar_items.append((rect_id, label, val))
            x += bar_width + spacing
        self.canvas.create_text(self.width // 2, 20,
                                text=f"Vehicle counts per junction — {self.date}",
                                font=("Arial", 14, "bold"))
        self.canvas.create_text(40, top_margin + plot_height // 2,
                                text="Count", angle=90, font=("Arial", 12))
        self.add_legend()

    def _show_tooltip(self, event, label, val):
        self.tooltip.config(text=f"{label}: {val}")
        self.tooltip.place(x=event.x_root - self.root.winfo_rootx() + 10,
                           y=event.y_root - self.root.winfo_rooty() + 10)

    def _move_tooltip(self, event):
        self.tooltip.place(x=event.x_root - self.root.winfo_rootx() + 10,
                           y=event.y_root - self.root.winfo_rooty() + 10)

    def _hide_tooltip(self):
        self.tooltip.place_forget()

    def toggle_sort(self):
        self._sort_desc = not self._sort_desc
        self.canvas.delete('all')
        self.draw_histogram()

    def save_as_postscript(self):
        fname = filedialog.asksaveasfilename(defaultextension='.ps',
                                             filetypes=[('PostScript', '*.ps')])
        if not fname:
            return
        try:
            self.canvas.postscript(file=fname)
            _success(f"Saved canvas as {fname}")
        except Exception as e:
            _error(f"Failed to save canvas: {e}")

    def open_matplotlib(self):
        if not MATPLOTLIB_AVAILABLE:
            _error("Matplotlib not available.")
            return
        plot_histogram_matplotlib(self.traffic_data, self.date)

    def save_as_png(self):
        if not MATPLOTLIB_AVAILABLE:
            _error("Matplotlib not available.")
            return
        fname = filedialog.asksaveasfilename(defaultextension='.png',
                                             filetypes=[('PNG Image', '*.png')])
        if not fname:
            return
        plot_histogram_matplotlib(self.traffic_data, self.date, save_path=fname)

    def add_legend(self):
        legend_x = self.width - 200
        legend_y = 60
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
                  "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]
        for i, label in enumerate(list(self.traffic_data.keys())[:8]):
            y = legend_y + i * 20
            self.canvas.create_rectangle(legend_x, y, legend_x + 15, y + 12,
                                         fill=colors[i % len(colors)], outline="black")
            self.canvas.create_text(legend_x + 20, y + 6, anchor="w",
                                    text=label, font=("Arial", 9))

    def draw_junction_view(self):
        c = self.junction_canvas
        c.delete('all')

        if not self.traffic_data:
            c.create_text(400, 300, text="No junction data", font=("Arial", 16), fill='#888')
            return

        items = sorted(self.traffic_data.items(), key=lambda x: -x[1])
        max_count = items[0][1] if items else 1
        colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
                  "#59a14f", "#edc949", "#af7aa1", "#ff9da7"]

        card_w, card_h = 268, 248
        pad = 24

        # Determine column count from actual canvas width once rendered
        c.update_idletasks()
        canvas_w = c.winfo_width()
        if canvas_w < 50:
            canvas_w = 900
        cols = max(1, (canvas_w - pad) // (card_w + pad))

        for i, (jname, count) in enumerate(items):
            col = i % cols
            row = i // cols
            x = pad + col * (card_w + pad)
            y = pad + row * (card_h + pad)
            self._draw_junction_card(c, x, y, card_w, card_h, jname, count, max_count,
                                     colors[i % len(colors)])

        total_rows = (len(items) + cols - 1) // cols
        total_h = pad + total_rows * (card_h + pad)
        c.configure(scrollregion=(0, 0, canvas_w, max(total_h, 600)))

    def _draw_junction_card(self, c, x, y, w, h, jname, count, max_count, color):
        # Drop shadow
        c.create_rectangle(x + 4, y + 4, x + w + 4, y + h + 4, fill='#cccccc', outline='')
        # Card background
        c.create_rectangle(x, y, x + w, y + h, fill='white', outline=color, width=2)

        # Coloured header strip
        hdr = 38
        c.create_rectangle(x, y, x + w, y + hdr, fill=color, outline='')
        c.create_text(x + w // 2, y + hdr // 2, text=jname, fill='white',
                      font=('Arial', 9, 'bold'), width=w - 12)

        # Road intersection diagram
        parts = jname.split('/')
        road_h = parts[0].strip()
        road_v = parts[1].strip() if len(parts) > 1 else ''

        cx = x + w // 2
        cy = y + hdr + 88          # centre of diagram area
        arm = 58                   # road arm length
        lw  = 5                    # road line width

        # Horizontal road (road_h)
        c.create_line(cx - arm, cy, cx + arm, cy, fill=color, width=lw, capstyle='round')
        # Vertical road (road_v)
        c.create_line(cx, cy - arm, cx, cy + arm, fill=color, width=lw, capstyle='round')
        # Intersection circle
        r = 7
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline='white', width=2)

        lbl_font = ('Arial', 7, 'bold')
        lbl_col  = '#333333'
        c.create_text(cx - arm - 5, cy,        text=road_h, font=lbl_font, anchor='e',  fill=lbl_col)
        c.create_text(cx + arm + 5, cy,        text=road_h, font=lbl_font, anchor='w',  fill=lbl_col)
        c.create_text(cx,           cy - arm - 5, text=road_v, font=lbl_font, anchor='s', fill=lbl_col)
        c.create_text(cx,           cy + arm + 5, text=road_v, font=lbl_font, anchor='n', fill=lbl_col)

        # Count bar + label
        bar_x  = x + 12
        bar_y  = y + h - 52
        bar_w  = w - 24
        bar_hh = 13
        filled = max(4, int(bar_w * count / max_count)) if max_count else 4

        c.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_hh,
                           fill='#e0e0e0', outline='#bbb')
        c.create_rectangle(bar_x, bar_y, bar_x + filled, bar_y + bar_hh,
                           fill=color, outline='')
        c.create_text(x + w // 2, y + h - 22,
                      text=f"{count:,} vehicles",
                      font=('Arial', 11, 'bold'), fill='#222')

    def run(self):
        if MATPLOTLIB_AVAILABLE:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            fig_graph = plot_histogram_matplotlib(self.traffic_data, self.date)
            fig_junc  = plot_junctions_matplotlib(self.traffic_data, self.date)

            root = tk.Tk()
            root.title(f"Traffic Analysis — {self.date}")
            root.geometry("1100x700")

            nb = ttk.Notebook(root)
            nb.pack(fill='both', expand=True, padx=4, pady=4)

            for fig, label in [(fig_graph, '  Graph  '), (fig_junc, '  Junctions  ')]:
                if fig is None:
                    continue
                tab = tk.Frame(nb)
                nb.add(tab, text=label)
                canvas = FigureCanvasTkAgg(fig, master=tab)
                canvas.draw()
                NavigationToolbar2Tk(canvas, tab).update()
                canvas.get_tk_widget().pack(fill='both', expand=True)

            root.mainloop()
            plt.close('all')
        else:
            self.setup_window()
            self.root.after(50, self.draw_junction_view)
            self.root.mainloop()


# ─────────────────────────── Multi-file processor ────────────────────────────

class MultiCSVProcessor:
    def __init__(self):
        self.current_data = None
        self.current_date = None
        self._processed = []   # [(filename, date, total_vehicles)]

    def load_csv_file(self, file_path):
        counts = defaultdict(int)
        date_found = None
        try:
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
            _error(f"File not found: {file_path}")
            return {}, None
        self.current_data = dict(counts)
        self.current_date = date_found
        return self.current_data, date_found

    def clear_previous_data(self):
        self.current_data = None
        self.current_date = None

    # ── File selection ────────────────────────────────────────────────────────

    def _list_files(self):
        data_dir = DEFAULT_DATA_DIR
        if not os.path.isdir(data_dir):
            _error(f"Data directory not found: {data_dir}")
            return []
        files = sorted(f for f in os.listdir(data_dir) if f.lower().endswith('.csv'))
        return files

    def _print_file_table(self, files):
        # column widths
        w_idx  = 3
        w_name = max(len(f) for f in files) if files else 30
        w_date = 12
        w_size = 9

        B = _B
        sep = (f"  {B['ml']}{B['hl'] * (w_idx + 2)}{B['cx']}{B['hl'] * (w_name + 2)}{B['cx']}"
               f"{B['hl'] * (w_date + 2)}{B['cx']}{B['hl'] * (w_size + 2)}{B['mr']}")
        top = (f"  {B['tl']}{B['h'] * (w_idx + 2)}{B['tj']}{B['h'] * (w_name + 2)}{B['tj']}"
               f"{B['h'] * (w_date + 2)}{B['tj']}{B['h'] * (w_size + 2)}{B['tr']}")
        hdr = (f"  {B['v']} {' # ':<{w_idx}} {B['v']} {'File':<{w_name}} {B['v']} "
               f"{'Date':<{w_date}} {B['v']} {'Size':>{w_size}} {B['v']}")
        bot = (f"  {B['bl']}{B['h'] * (w_idx + 2)}{B['bj']}{B['h'] * (w_name + 2)}{B['bj']}"
               f"{B['h'] * (w_date + 2)}{B['bj']}{B['h'] * (w_size + 2)}{B['br']}")

        print(f"{DIM}{top}{RST}")
        print(f"{BOLD}{hdr}{RST}")
        print(f"{DIM}{sep}{RST}")

        for i, fname in enumerate(files, 1):
            fpath = os.path.join(DEFAULT_DATA_DIR, fname)
            size_kb = os.path.getsize(fpath) / 1024 if os.path.exists(fpath) else 0
            date_str = _parse_date_from_filename(fname)
            idx_col  = f"{i:>{w_idx}}"
            name_col = f"{fname:<{w_name}}"
            date_col = f"{date_str:<{w_date}}"
            size_col = f"{size_kb:>{w_size - 3}.1f} KB"
            print(f"  {B['v']} {CYN}{idx_col}{RST} {B['v']} {WHT}{name_col}{RST} {B['v']} "
                  f"{DIM}{date_col}{RST} {B['v']} {DIM}{size_col}{RST} {B['v']}")

        print(f"{DIM}{bot}{RST}")

    def handle_user_interaction(self):
        files = self._list_files()
        if not files:
            _error("No CSV files found in the data directory.")
            return None

        _section(f"Available Data Files  ({len(files)} total)")
        self._print_file_table(files)

        while True:
            raw = _prompt(f"Select file [1–{len(files)}] or  q  to quit:")
            choice = raw.strip().lower()
            if choice in ('q', 'quit', 'exit'):
                return None
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(files):
                    return os.path.normpath(os.path.join(DEFAULT_DATA_DIR, files[idx - 1]))
            _error(f"Enter a number between 1 and {len(files)}, or q to quit.")

    # ── Session loop ──────────────────────────────────────────────────────────

    def _print_session_summary(self):
        if not self._processed:
            return
        print()
        _thick_rule()
        print(f"{CYN}{BOLD}  Session Summary  —  {len(self._processed)} file(s) processed{RST}")
        _rule()
        for fname, date, total in self._processed:
            print(f"    {DIM}{date or '—':<14}{RST} {WHT}{fname:<36}{RST} "
                  f"{DIM}{total:>5} vehicles{RST}")
        _thick_rule()
        print()

    def process_files(self):
        while True:
            selected = self.handle_user_interaction()
            if selected is None:
                break

            self.clear_previous_data()

            fname = os.path.basename(selected)
            _info(f"Processing  {fname} …")

            outcomes, junction_counts = process_csv_data(selected)
            if not outcomes:
                _error("No data found or failed to process file.")
            else:
                display_outcomes(outcomes)
                save_results_to_file(outcomes, file_name='results.txt')
                _success(f"Results appended to  results.txt")

                self._processed.append((
                    fname,
                    outcomes.get('date'),
                    outcomes.get('total_vehicles', 0),
                ))

                app = HistogramApp(junction_counts, outcomes.get('date') or selected)
                app.run()

            while True:
                raw = _prompt("Process another file?  [y / n]:")
                ans = raw.strip().lower()
                if ans in ('y', 'yes'):
                    break
                if ans in ('n', 'no', 'q'):
                    self._print_session_summary()
                    print(f"  {GRN}Goodbye.{RST}\n")
                    return
                _error("Please enter  y  or  n.")


if __name__ == '__main__':
    print_banner()
    try:
        proc = MultiCSVProcessor()
        proc.process_files()
    except KeyboardInterrupt:
        print(f"\n\n  {YLW}Interrupted.{RST}\n")
