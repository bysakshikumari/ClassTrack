from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ClassTrack", layout="centered")

FILE = Path(__file__).parent / "data" / "hostel_timetable.xlsx"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS = ["8:30", "9:30", "10:30", "11:30", "1:00", "2:00", "3:00", "4:00"]
ENDS = ["9:30", "10:30", "11:30", "12:30", "2:00", "3:00", "4:00", "5:00"]
STARTS = [510, 570, 630, 690, 780, 840, 900, 960]  # minutes from midnight
INFO = ["Name", "Room", "Year", "Course"]


def clean(v):
    if pd.isna(v):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


@st.cache_data
def load(path: str, mtime: float) -> pd.DataFrame:
    """Read the Excel sheet. `mtime` makes the cache refresh when the file changes."""
    df = pd.read_excel(path, sheet_name=0, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in INFO if c not in df.columns]
    if missing:
        raise ValueError(f"Missing column(s) in Excel: {', '.join(missing)}")
    df = df[df["Name"].notna() & (df["Name"].astype(str).str.strip() != "")].copy()
    for c in INFO:
        df[c] = df[c].map(clean)
    for d in DAYS:
        for i in range(1, 9):
            col = f"{d}-{i}"
            df[col] = (df[col].astype(str).str.strip().str.upper() == "Y") if col in df.columns else False
    return df.reset_index(drop=True)


def show(df: pd.DataFrame):
    out = df[INFO].copy()
    out["_r"] = pd.to_numeric(out["Room"], errors="coerce")
    out = out.sort_values(["_r", "Room", "Name"]).drop(columns="_r")
    st.dataframe(out, hide_index=True)


st.title("ClassTrack")
st.caption("college class tracker")

try:
    df = load(str(FILE), FILE.stat().st_mtime)
except Exception as e:
    st.error(f"Could not read `data/hostel_timetable.xlsx`. {e}")
    st.stop()

now = datetime.now(timezone(timedelta(hours=5, minutes=30)))  # IST
wd = now.weekday()
mins = now.hour * 60 + now.minute
cur = next((i for i, s in enumerate(STARTS) if s + 60 > mins), 7)

day = st.radio("Day", DAYS, index=wd if wd < 5 else 0, horizontal=True)
slot = st.radio(
    "Time", range(8), index=cur, horizontal=True,
    format_func=lambda i: SLOTS[i],
)
st.caption(f"Slot {slot + 1}: {SLOTS[slot]} – {ENDS[slot]} ")

c1, c2 = st.columns(2)
q = c1.text_input("Search", placeholder="Name / room / course")
years = sorted(df["Year"].unique())
yr = c2.selectbox("Year", ["All"] + years)

view = df
if yr != "All":
    view = view[view["Year"] == yr]
if q:
    key = view[INFO].agg(" ".join, axis=1).str.lower()
    view = view[key.str.contains(q.strip().lower(), regex=False)]

if view.empty:
    st.info("No students match.")
    st.stop()

has = view[f"{day}-{slot + 1}"]
st.subheader(f"In class ({int(has.sum())})")
st.caption("Check these rooms.")
if has.any():
    show(view[has])
else:
    st.info("Nobody has class in this slot.")

st.subheader(f"No class ({int((~has).sum())})")
if (~has).any():
    show(view[~has])
else:
    st.info("Everyone has class in this slot.")

st.caption(f"{len(df)} students loaded from Excel.")
