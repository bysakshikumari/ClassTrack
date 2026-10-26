from datetime import datetime, timedelta, timezone
from html import escape as e
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ClassTrack", layout="center")

FILE = Path(__file__).parent / "data" / "hostel_timetable.xlsx"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS = ["8:30", "9:30", "10:30", "11:30", "1:00", "2:00", "3:00", "4:00"]
ENDS = ["9:30", "10:30", "11:30", "12:30", "2:00", "3:00", "4:00", "5:00"]
STARTS = [510, 570, 630, 690, 780, 840, 900, 960]  # minutes from midnight
INFO = ["Name", "Room", "Year", "Course"]
IST = timezone(timedelta(hours=5, minutes=30))

GLASS = "background:rgba(255,255,255,.72)!important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid rgba(0,0,0,.08)!important;border-radius:16px;"
INK, MUTED, ACCENT, WARN = "#1f2328", "#4b535c", "#2f6f5e", "180,35,24"
# Every colour is set explicitly, so the look is the same whatever theme/dark mode the visitor's device uses.
st.markdown(f"""<style>
:root{{color-scheme:light}}
.stApp{{background:linear-gradient(160deg,#f8f8f5,#eceeea) fixed}}
.stApp *,[role="listbox"] *,[data-baseweb="popover"] *{{color:{INK}!important}}
.stApp [data-testid="stCaptionContainer"] *,.row span{{color:{MUTED}!important}}
[data-testid="stCaptionContainer"]{{opacity:1!important}}
.stApp input::placeholder{{color:#8a9099!important;opacity:1}}
header[data-testid="stHeader"]{{background:rgba(248,248,245,.85)!important;backdrop-filter:blur(10px)}}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stLayoutWrapper"]>[data-testid="stVerticalBlock"],[data-testid="stCheckbox"],[data-testid="stTextInputRootElement"],[data-testid="stSelectbox"] [role="group"],[data-baseweb="input"],[data-baseweb="select"]>div,[data-testid="stAlert"],.row{{{GLASS}}}
[data-testid="stAlert"] *{{background:transparent!important;border:0!important}}
.stApp input{{background:transparent!important}}
[role="listbox"],[data-baseweb="popover"] ul,[data-baseweb="menu"]{{background:#fff!important}}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stLayoutWrapper"]>[data-testid="stVerticalBlock"]{{backdrop-filter:none;-webkit-backdrop-filter:none;background:rgba(255,255,255,.6)!important;box-shadow:0 8px 30px rgba(0,0,0,.10);border:1px solid rgba(0,0,0,.1)!important;border-radius:22px}}
[data-testid="stCheckbox"]{{padding:.55rem .8rem;margin-bottom:.4rem}}
[data-testid="stCheckbox"] label>span+div{{background:#fff!important;border:1.5px solid #8a939c!important;border-radius:6px}}
[data-testid="stCheckbox"] label:has(input:checked)>span+div{{background:{ACCENT}!important;border-color:{ACCENT}!important}}
[data-testid="stCheckbox"]:has(input:checked){{background:rgba({WARN},.08)!important;border-color:rgba({WARN},.3)!important}}
[data-testid="stRadioOption"]{{{GLASS}border-radius:999px;padding:.3rem 1rem}}
[data-testid="stRadioOption"]>div>div:first-child{{display:none}}
[data-testid="stRadioOption"]:has(input:checked){{background:{ACCENT}!important;border-color:{ACCENT}!important}}
[data-testid="stRadioOption"]:has(input:checked) *{{color:#fff!important}}
[data-testid="stCode"],[data-testid="stCode"] pre,[data-testid="stCode"] code{{background:#f1f3f0!important;border-radius:12px}}
[data-testid="stCode"] pre,[data-testid="stCode"] code{{white-space:pre-wrap!important;word-break:break-word}}
[data-testid="stCode"] div:has(>[data-testid="stElementToolbarButton"]){{background:rgba(255,255,255,.92)!important;border:1px solid rgba(0,0,0,.12);box-shadow:0 2px 8px rgba(0,0,0,.08)}}
[data-testid="stCode"] button:hover{{background:rgba(0,0,0,.06)!important}}
.row{{display:flex;flex-direction:column;padding:.55rem .8rem;margin-bottom:.4rem}}
.row span{{font-size:.85rem}}
</style>""", unsafe_allow_html=True)


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


def order(d):
    return d.assign(_r=pd.to_numeric(d["Room"], errors="coerce")).sort_values(["_r", "Room", "Name"]).drop(columns="_r")


st.title("ClassTrack")
st.caption("college class tracker")

try:
    df = load(str(FILE), FILE.stat().st_mtime)
except Exception as err:
    st.error(f"Could not read `data/hostel_timetable.xlsx`. {err}")
    st.stop()

now = datetime.now(IST)
wd = now.weekday()
mins = now.hour * 60 + now.minute
cur = next((i for i, s in enumerate(STARTS) if s + 60 > mins), 7)

day = st.radio("Day", DAYS, index=wd if wd < 5 else 0, horizontal=True)
slot = st.radio("Time", range(8), index=cur, horizontal=True, format_func=lambda i: SLOTS[i])
st.caption(f"Slot {slot + 1}: {SLOTS[slot]} – {ENDS[slot]}  ·  lunch 12:30 – 1:00")

c1, c2 = st.columns(2)
q = c1.text_input("Search", placeholder="Name / room / course")
yr = c2.selectbox("Year", ["All"] + sorted(df["Year"].unique()))

view = df if yr == "All" else df[df["Year"] == yr]
if q:
    view = view[view[INFO].agg(" ".join, axis=1).str.lower().str.contains(q.strip().lower(), regex=False)]
if view.empty:
    st.info("No students match.")
    st.stop()

col = f"{day}-{slot + 1}"
has = view[col]
marks = st.session_state.setdefault("marks", set())  # students ticked as missing
mid = lambda n, r: (now.strftime("%Y-%m-%d"), col, n, r)

with st.container(border=True):
    st.subheader(f"In class ({int(has.sum())})")
    st.caption("Check these rooms and tick the students you find in the hostel.")
    for _, r in order(view[has]).iterrows():
        label = f"**{r.Name}** · Room {r.Room} · Yr {r.Year} · {r.Course}"
        if st.checkbox(label, value=mid(r.Name, r.Room) in marks, key="|".join(mid(r.Name, r.Room))):
            marks.add(mid(r.Name, r.Room))
        else:
            marks.discard(mid(r.Name, r.Room))
    if not has.any():
        st.info("Nobody has class in this slot.")

with st.container(border=True):
    st.subheader(f"No class ({int((~has).sum())})")
    rows = "".join(
        f'<div class="row"><b>{e(r.Name)}</b><span>Room {e(r.Room)} · Yr {e(r.Year)} · {e(r.Course)}</span></div>'
        for _, r in order(view[~has]).iterrows()
    )
    st.markdown(rows or "Everyone has class in this slot.", unsafe_allow_html=True)

# Report covers everyone with class in this slot (ignores search/year filters)
full = df[df[col]]
miss = order(full.loc[[mid(n, r) in marks for n, r in zip(full.Name, full.Room)]])  # .loc: safe when empty
is_today = wd < 5 and day == DAYS[wd]
report = "\n".join(
    [f"ClassTrack report: {day} {SLOTS[slot]}" + (f" ({now:%d %b %Y})" if is_today else ""),
     f"Students with class: {len(full)}",
     f"Found in hostel (missing class): {len(miss)}"]
    + [f"{i}. {r.Name} (Room {r.Room}, Yr {r.Year}, {r.Course})" for i, (_, r) in enumerate(miss.iterrows(), 1)]
)
with st.container(border=True):
    st.subheader("Report")
    st.caption("Use the copy icon at the top right of the box.")
    st.code(report, language=None)
