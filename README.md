<div align="center">

# ClassTrack

**A college class tracker.**
Pick a day and a time slot, and instantly see who has class and who doesn't, so you only check the rooms that matter.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data-150458?logo=pandas&logoColor=white)
![Excel](https://img.shields.io/badge/Data-Excel-217346?logo=microsoftexcel&logoColor=white)

([**Live demo**](https://class-track.streamlit.app/)) · [Report a bug](../../issues)

<!-- Add a screenshot: save it as docs/screenshot.png, then uncomment the line below -->
<!-- <img src="docs/screenshot.png" alt="ClassTrack screenshot" width="360"> -->

</div>

---

## The problem

Hostels in Delhi University colleges house students from many courses and years. Almost every student has a **different timetable**, because of electives, practicals and combinations of subjects. When a hostel rule asks the warden to report students who stay back during class hours, checking every room is slow, and working out who *should* be in class right now is guesswork.

## The solution

ClassTrack turns one Excel sheet into a simple mobile-friendly app.

1. Each student's timetable is entered once, as a **Y** in each slot where they have class.
2. The warden opens the app, picks the day and time (it opens on the **current** day and slot by default).
3. The app shows two lists:
   - **In class**: students who should be in class right now. These are the rooms to check.
   - **No class**: students who are free, so there is nothing to check.

No more asking every student about their schedule, and no timetable images to decode.

## Features

- **Day and time selector** for Mon to Fri, with 8 hourly slots (lunch break included)
- **Auto-selects the current day and slot** in Indian time, and opens on Monday at weekends
- **In class / No class lists** with live counts, sorted by room number
- **Search** by name, room or course, and filter by **year**
- **Excel is the database**: edit the sheet, and the app updates when the file changes
- **Friendly error messages** if the Excel file is missing a required column
- **Works on a phone**, which is where wardens will actually use it

## How it works

```mermaid
flowchart LR
    A[Excel sheet<br/>data/hostel_timetable.xlsx] -->|pandas + openpyxl| B[Cleaned table<br/>cached by file mtime]
    B --> C{Day + time slot}
    C -->|has Y in slot| D[In class list]
    C -->|blank in slot| E[No class list]
```

The app reads the Excel file, cleans it (trims spaces, treats `y` and `Y` the same, ignores blank rows) and caches the result. The cache is tied to the file's modified time, so changing the file refreshes the data automatically.

## Time slots

| Slot | 1 | 2 | 3 | 4 | | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| **Start** | 8:30 | 9:30 | 10:30 | 11:30 | *lunch 12:30 to 1:00* | 1:00 | 2:00 | 3:00 | 4:00 |

Each class is one hour, and college runs from 8:30 am to 5:00 pm.

## Excel format

The data lives in `data/hostel_timetable.xlsx`, on the **Timetable** sheet, with one row per student.

| Name | Room | Year | Course | Mon-1 | Mon-2 | … | Fri-8 |
|---|---|---|---|---|---|---|---|
| Asha | 12 | 2 | BA Hons English | Y | Y | | |

- Type **Y** in every slot where the student has class, and leave free slots blank.
- Keep the header row exactly as it is: `Name, Room, Year, Course, Mon-1 … Fri-8`.
- Slot columns are named `Day-SlotNumber` (for example `Wed-5` means Wednesday, 1:00 pm).

## Quick start

```bash
git clone https://github.com/bysakshikumari/ClassTrack.git
cd ClassTrack
pip install -r requirements.txt
streamlit run app.py
```

Then open the local address Streamlit prints in the terminal (usually http://localhost:8501).


## Project structure

```
ClassTrack/
├── app.py                      # Streamlit app (UI + logic)
├── requirements.txt            # streamlit, pandas, openpyxl
├── data/
│   └── hostel_timetable.xlsx   # student timetable data
└── README.md
```

## Tech stack

- **Python** and **Streamlit** for the interface
- **pandas** for filtering and sorting
- **openpyxl** for reading Excel files


## Roadmap

Ideas for future versions:

- [ ] Mark classes as cancelled for a day, so those students drop out of the "In class" list
- [ ] Approved leave and sick-student list
- [ ] Password protection

## Contributing

Suggestions and pull requests are welcome. Open an issue to discuss what you'd like to change.

---

<div align="center">
⭐ Star the repo if it helped you.
</div>
