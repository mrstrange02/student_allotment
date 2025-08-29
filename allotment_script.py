#!/usr/bin/env python3
"""
Student College Allotment - Standalone Script
Reads: students.csv, seat.csv, preference.csv (from same directory)
Writes: college_allocation_results.csv (with columns: uniqueid,name,gender,caste,rank,collegeid,institution,prefnumber)
Usage: python3 allotment.py
"""

import pandas as pd
import sys

def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    students = load_csv("students.csv")
    seats = load_csv("seat.csv")
    prefs = load_csv("preference.csv")

    # Normalize column names
    students.columns = [c.strip() for c in students.columns]
    seats.columns = [c.strip() for c in seats.columns]
    prefs.columns = [c.strip() for c in prefs.columns]

    # Map 'Caste' -> 'Category' if present
    if "Caste" in students.columns and "Category" not in students.columns:
        students = students.rename(columns={"Caste": "Category"})

    # Map seat column names to expected names
    seats = seats.rename(columns={
        "TOTAL No. of seats": "Total Seats",
        "TOTAL No. of students admitted": "Total Admitted",
        "No. of students joined in Orphan Quota": "Orphan Quota",
        "No. of students Joined in PHC Quota": "PHC Quota"
    })

    # Coerce types
    students["Rank"] = pd.to_numeric(students["Rank"], errors="coerce")
    students["UniqueID"] = pd.to_numeric(students["UniqueID"], errors="coerce")
    prefs["PrefNumber"] = pd.to_numeric(prefs["PrefNumber"], errors="coerce")
    prefs["CollegeID"] = pd.to_numeric(prefs["CollegeID"], errors="coerce")
    prefs["UniqueID"] = pd.to_numeric(prefs["UniqueID"], errors="coerce")
    seats["CollegeID"] = pd.to_numeric(seats["CollegeID"], errors="coerce")

    # Ensure numeric quotas
    numeric_quota_cols = ["Total Seats", "Total Admitted", "Orphan Quota", "PHC Quota", "SC", "SC-CC", "ST", "BC", "Minority", "OC"]
    for col in numeric_quota_cols:
        if col in seats.columns:
            seats[col] = pd.to_numeric(seats[col], errors="coerce").fillna(0).astype(int)
        else:
            seats[col] = 0

    # Sort students by rank
    students_sorted = students.sort_values(by=["Rank", "UniqueID"], ascending=[True, True]).reset_index(drop=True)

    quota_cols = ["SC", "SC-CC", "ST", "BC", "Minority", "OC"]
    seat_state = {}
    for _, row in seats.iterrows():
        seat_state[int(row["CollegeID"])] = {
            "Institution": row.get("Institution", ""),
            "Total Seats": int(row.get("Total Seats", 0)),
            "Total Admitted": int(row.get("Total Admitted", 0)),
            "Orphan Quota": int(row.get("Orphan Quota", 0)),
            "PHC Quota": int(row.get("PHC Quota", 0)),
            "SC": int(row.get("SC", 0)),
            "SC-CC": int(row.get("SC-CC", 0)),
            "ST": int(row.get("ST", 0)),
            "BC": int(row.get("BC", 0)),
            "Minority": int(row.get("Minority", 0)),
            "OC": int(row.get("OC", 0)),
        }

    def allot_student(student_row):
        sid = int(student_row["UniqueID"])
        cat = str(student_row.get("Category","")).strip()
        prefs_for_student = prefs[prefs["UniqueID"] == sid].copy()
        prefs_for_student = prefs_for_student.sort_values(by=["PrefNumber", "CollegeID"])
        for _, pref_row in prefs_for_student.iterrows():
            college_id = int(pref_row["CollegeID"])
            pref_no = int(pref_row["PrefNumber"]) if not pd.isna(pref_row["PrefNumber"]) else None
            if college_id not in seat_state:
                continue
            college = seat_state[college_id]
            if cat in quota_cols and college.get(cat, 0) > 0:
                college[cat] -= 1
                college["Total Admitted"] += 1
                return {
                    "UniqueID": sid,
                    "CollegeID": college_id,
                    "Institution": college["Institution"],
                    "PrefNumber": pref_no,
                    "CategoryUsed": cat
                }
        return {
            "UniqueID": sid,
            "CollegeID": None,
            "Institution": "No College Available",
            "PrefNumber": None,
            "CategoryUsed": cat
        }

    allocations = [allot_student(srow) for _, srow in students_sorted.iterrows()]
    alloc_df = pd.DataFrame(allocations)
    final = (alloc_df.merge(students[["UniqueID", "Name", "Gender", "Category", "Rank"]], on="UniqueID", how="left")
             .rename(columns={"Category": "Caste"}))
    final = final[["UniqueID", "Name", "Gender", "Caste", "Rank", "CollegeID", "Institution", "PrefNumber"]].reset_index(drop=True)

    # Prepare submission format (lowercase field names)
    mapping = {
        "UniqueID": "uniqueid",
        "Name": "name",
        "Gender": "gender",
        "Caste": "caste",
        "Rank": "rank",
        "CollegeID": "collegeid",
        "Institution": "institution",
        "PrefNumber": "prefnumber"
    }
    submission = final[list(mapping.keys())].rename(columns=mapping)
    submission.to_csv("college_allocation_results_submission.csv", index=False)
    print("Wrote college_allocation_results_submission.csv")

if __name__ == '__main__':
    main()
