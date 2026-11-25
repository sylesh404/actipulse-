"""Create a sample Excel file for testing."""

import pandas as pd

data = {
    "date": [
        "2024-01-18", "2024-01-18", "2024-01-18", "2024-01-18",
        "2024-01-18", "2024-01-18", "2024-01-18", "2024-01-18",
        "2024-01-19", "2024-01-19", "2024-01-19", "2024-01-19",
        "2024-01-19", "2024-01-19", "2024-01-19", "2024-01-19",
    ],
    "start_time": [
        "07:00", "07:30", "09:00", "10:00",
        "12:00", "13:00", "15:00", "17:00",
        "06:45", "07:15", "09:00", "11:00",
        "12:30", "14:00", "16:00", "18:00",
    ],
    "end_time": [
        "07:30", "09:00", "10:00", "12:00",
        "13:00", "15:00", "17:00", "18:00",
        "07:15", "09:00", "11:00", "12:30",
        "14:00", "16:00", "18:00", "19:00",
    ],
    "activity": [
        "Walking", "Sitting", "Standing", "Sitting",
        "Walking", "Sitting", "Standing", "Sitting",
        "Running", "Sitting", "Standing", "Sitting",
        "Walking", "Sitting", "Cycling", "Sitting",
    ],
}

df = pd.DataFrame(data)
df.to_excel("data/sample_activity.xlsx", index=False, engine="openpyxl")
print("✓ Created sample_activity.xlsx")
