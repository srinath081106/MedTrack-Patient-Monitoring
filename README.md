# MedTrack – Patient Health Monitoring System

MedTrack is a beginner-friendly Python desktop application for learning patient-record management. It uses **Tkinter** for the interface and **SQLite** for local data storage.

## Features

- Register patients with a unique patient code, name, and age
- Search patient records by code or name
- Record heart rate (bpm), SpO₂ (%), body temperature (°C), and optional notes
- Store data locally in an SQLite database
- View measurement history
- Flag measurements outside configurable example ranges
- Validate user input and prevent duplicate patient codes

## Technology

- Python 3
- Tkinter (included with most standard Windows Python installations)
- SQLite (included with Python)

No third-party Python packages are required.

## Requirements

- Windows 10/11
- Python 3.10 or later recommended

## Run on Windows

1. Install Python from https://www.python.org/downloads/windows/
2. During installation, select **Add python.exe to PATH**.
3. Download or clone this repository and open its folder.
4. Open Command Prompt in that folder.
5. Run:

   ```bash
   python --version
   python main.py
   ```

   If `python` is not recognized, try `py --version` and `py main.py`.

The first run creates `medtrack.db` in the same folder. This database contains the patients and measurements you enter. Keep real personal/medical data out of public repositories.

## How to use

1. Open **Patients**.
2. Enter a unique patient code, name, and age; click **Add Patient**.
3. Select that patient in the table.
4. Open **Record Vital Signs**.
5. Enter heart rate, SpO₂, temperature, and optional notes; click **Save Reading**.
6. Open **Reading History** to review saved measurements.

## Testing checklist

- [ ] Add a patient with code `P001`, name `Demo Patient`, age `25`.
- [ ] Try adding `P001` again and confirm the duplicate code is rejected.
- [ ] Search for `Demo`.
- [ ] Select the patient and save a test reading: HR `75`, SpO₂ `98`, temperature `36.8`.
- [ ] Check that the measurement appears in Reading History.
- [ ] Try an educational out-of-range example such as HR `120` and confirm an example flag appears.
- [ ] Close and reopen the application; confirm records remain saved.

Use fictional sample data for testing.

## Example ranges and safety note

The current code uses simple illustrative thresholds:
- Heart rate: 60–100 bpm
- SpO₂: at least 95%
- Temperature: 36.1–37.8 °C

These are **educational example ranges only**, not personalized clinical reference ranges. Age, activity, altitude, device accuracy, medical history, and clinical context can change interpretation. This project is not validated for clinical use, does not diagnose conditions, and must not be used to make treatment decisions. A “no flag” result does not mean a person is healthy.

## Project structure

```text
MedTrack-Patient-Monitoring/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Future improvements

- Export history to CSV
- Add date filters and trend charts
- Add user login and access control
- Add configurable thresholds with clear clinical review
- Add automated tests

## License

This project is shared for educational and portfolio use. Add a license file if you want to specify reuse permissions.
