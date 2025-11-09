
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Dict, Tuple, Literal

Mode = Literal["all_days", "weekdays"]

@dataclass(frozen=True)
class ShiftConfig:
    """Single shift definition."""
    start_hhmm: str  # "HH:MM"
    end_hhmm: str    # "HH:MM"

    def duration_hours(self) -> float:
        """Compute duration in hours, handling overnight span."""
        sh, sm = map(int, self.start_hhmm.split(":"))
        eh, em = map(int, self.end_hhmm.split(":"))
        start_min = sh * 60 + sm
        end_min = eh * 60 + em
        dur = end_min - start_min
        if dur < 0:
            # overnight
            dur += 24 * 60
        return round(dur / 60.0, 2)

    def is_off(self) -> bool:
        return (self.start_hhmm == "00:00" and self.end_hhmm == "00:00")

@dataclass
class LeaveResult:
    days_counted: int
    hours_total: float
    details: Dict[str, float]  # "YYYY-MM-DD" -> hours counted that day

def _daterange_inclusive(start: date, end: date):
    d = start
    delta = timedelta(days=1)
    while d <= end:
        yield d
        d += delta

def _is_weekday(d: date) -> bool:
    return d.weekday() < 5  # Mon-Fri

def _normalize_hhmm(s: str | None) -> str:
    s = (s or "00:00").strip()
    if len(s) == 4:  # e.g., "6:00"
        s = "0" + s
    return s

def calculate_leave_hours(
    start_date_str: str,
    end_date_str: str,
    shift_letter: str,
    shifts_config: Dict[str, Tuple[str, str]],
    mode: Mode = "all_days",
) -> LeaveResult:
    """
    Calculate URLoP hours for an employee who does NOT have a per-day schedule.
    Rule of thumb used here:
      - If the assigned shift (by letter) has working hours (not 00:00-00:00),
        we count that shift's duration for each day included according to `mode`.
      - If the assigned shift has 00:00-00:00 (Wolne), we count 0h for those days.
      - Weekends handling:
           * mode='all_days'   -> count all calendar days (weekends included)
           * mode='weekdays'   -> count only Mon–Fri
    Limitations:
      - Without a real schedule, this assumes the same shift letter applies for every day.
      - If your plant uses rotation, integrate with a schedule later.
    """
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    if end < start:
        raise ValueError("end_date must be on/after start_date")

    # Resolve shift
    if shift_letter not in shifts_config:
        raise KeyError(f"Unknown shift letter: {shift_letter}")
    st = _normalize_hhmm(shifts_config[shift_letter][1] if isinstance(shifts_config[shift_letter], tuple) else shifts_config[shift_letter][0])
    # shifts_config expected as { 'A': ('06:00','14:00'), ... }
    s_start, s_end = shifts_config[shift_letter]
    s_start = _normalize_hhmm(s_start)
    s_end = _normalize_hhmm(s_end)

    sc = ShiftConfig(s_start, s_end)
    dur = 0.0 if sc.is_off() else sc.duration_hours()

    details: Dict[str, float] = {}
    counted_days = 0
    for d in _daterange_inclusive(start, end):
        if mode == "weekdays" and not _is_weekday(d):
            continue
        hours = 0.0 if sc.is_off() else dur
        details[d.strftime("%Y-%m-%d")] = hours
        counted_days += 1

    total_hours = round(sum(details.values()), 2)
    return LeaveResult(days_counted=counted_days, hours_total=total_hours, details=details)

def calculate_l4_hours(
    start_date_str: str,
    end_date_str: str,
    shift_letter: str,
    shifts_config: Dict[str, Tuple[str, str]],
    mode: Mode = "all_days",
) -> LeaveResult:
    """
    Calculate L4 (sick leave) hours numerator for reporting.
    Notes:
      - L4 obowiązuje kalendarzowo (dni kalendarzowe), ale raportowo możesz policzyć
        ile 'zaplanowanych godzin' zostało objętych. Bez harmonogramu używamy tej samej
        logiki co przy urlopie: per-day hours = duration of the shift letter.
      - If you want strictly calendar-day count, use mode='all_days'.
      - For a white-collar Mon–Fri context, use mode='weekdays'.
    """
    return calculate_leave_hours(start_date_str, end_date_str, shift_letter, shifts_config, mode)


# --------------------- DB LOADER (optional) ---------------------
def load_shifts_config_from_db(db_path: str) -> Dict[str, Tuple[str, str]]:
    """
    Reads shifts from SQLite DB (table 'shifts' with columns: name, start_time, end_time).
    Returns: { 'A': ('06:00','14:00'), ... }
    """
    import sqlite3
    cfg: Dict[str, Tuple[str, str]] = {}
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("SELECT name, start_time, end_time FROM shifts ORDER BY name ASC")
        for name, start, end in cur.fetchall():
            s = (str(start or "00:00")[:5], str(end or "00:00")[:5])
            cfg[str(name).strip()] = s
    finally:
        con.close()
    return cfg

# --------------------- DEMO / CLI ---------------------
if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser(description="Probe calculator for leave/L4 without schedule (with optional DB loader)")
    p.add_argument("--db", help="Path to hr_system.db (loads shifts from table `shifts`)")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD")
    p.add_argument("--shift", required=True, help="Shift letter, e.g., A")
    p.add_argument("--mode", choices=["all_days","weekdays"], default="all_days")
    p.add_argument("--cfg", help="JSON mapping like: {'A':['06:00','14:00'],'B':['14:00','22:00'],'C':['22:00','06:00'],'D':['00:00','00:00']}")
    args = p.parse_args()

    # Default example config if none passed
    if args.db:
        cfg = load_shifts_config_from_db(args.db)
    elif args.cfg:
        cfg = json.loads(args.cfg.replace("'", '"'))
    else:
        cfg = {"A":["06:00","14:00"], "B":["14:00","22:00"], "C":["22:00","06:00"], "D":["00:00","00:00"]}

    # Normalize tuple format
    norm_cfg = {k: (v[0], v[1]) for k,v in cfg.items()}

    res = calculate_leave_hours(args.start, args.end, args.shift, norm_cfg, args.mode)
    print("URLoP -> days_counted:", res.days_counted, "hours_total:", res.hours_total)
    print("details:", json.dumps(res.details, indent=2, ensure_ascii=False))

    res_l4 = calculate_l4_hours(args.start, args.end, args.shift, norm_cfg, args.mode)
    print("L4     -> days_counted:", res_l4.days_counted, "hours_total:", res_l4.hours_total)
