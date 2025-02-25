import streamlit as st
import pandas as pd
import datetime

# Set page title and icon
st.set_page_config(page_title="QET-1 Monthly Attendance Tracker", page_icon="📅", layout="wide")

# Load and display company logo
logo_url = "https://erp.optisolbusiness.com/web/image/res.company/1/logo"
st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <img src="{logo_url}" width="150">
        <h1 style="margin-left: 20px;">QET-1 Monthly Attendance Tracker</h1>
    </div>
""", unsafe_allow_html=True)

# Define employee list
employees = [
    "Select Employee", "Balakumar", "Benita Devanesam", "Hari Abinaya M", "Hemanth", "Kishore",
    "Lavanya K", "Naga Arjun", "NandhaGopal E", "Nanthini E", "PavithraDevi",
    "Rajagopal B", "Rajalakshmi D", "Rajeswari M", "Sanjay Ram R", "Sendursuriyavel A",
    "Suganya R", "Vidya D", "Nanthini S", "Oviya", "Tharani"
]

# Get today's date
today = datetime.date.today()

# Function to get working days for a given month and year
def get_working_days(month, year):
    month_start = datetime.date(year, month, 1)
    month_days = [month_start + datetime.timedelta(days=i) for i in range(31)]
    return [day for day in month_days if day.weekday() < 5 and day.month == month]

# User selects month (default to current month)
month_options = [datetime.date(today.year, i, 1).strftime("%B %Y") for i in range(1, 13)]
current_month = datetime.date(today.year, today.month, 1).strftime("%B %Y")
month_selected = st.selectbox("📅 Select Month", month_options, index=month_options.index(current_month))
selected_month = datetime.datetime.strptime(month_selected, "%B %Y").month
selected_year = datetime.datetime.strptime(month_selected, "%B %Y").year
working_days = get_working_days(selected_month, selected_year)
total_days = len(working_days)

# Load attendance data from CSV
def load_data():
    try:
        df = pd.read_csv("attendance.csv")
        if "Dates" not in df.columns:
            df["Dates"] = ""
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Employee", "Dates"])

df = load_data()

# Employee selection (default to "Select Employee")
selected_employee = st.selectbox("🧑‍🏢 Select Employee", employees, index=0)

# Ensure an employee is selected before proceeding
if selected_employee != "Select Employee":
    existing_attendance = df[df["Employee"] == selected_employee]
    selected_dates = existing_attendance["Dates"].values[0].split(', ') if not existing_attendance.empty and isinstance(existing_attendance["Dates"].values[0], str) else []
    
    # Attendance selection with "N/A"
    attendance_options = [str(day) for day in working_days] + ["N/A"]
    selected_dates = st.multiselect("📌 Select Attendance Dates", attendance_options, default=selected_dates)

    # If "N/A" is selected, auto-fill all dates with "N/A"
    if "N/A" in selected_dates:
        selected_dates = ["N/A"]

    if st.button("✅ Update Attendance"):
        if existing_attendance.empty:
            df = pd.concat([df, pd.DataFrame([{ "Employee": selected_employee, "Dates": ', '.join(selected_dates)}])], ignore_index=True)
        else:
            df.loc[df["Employee"] == selected_employee, "Dates"] = ', '.join(selected_dates)
        df.to_csv("attendance.csv", index=False)
        st.success("🎉 Attendance updated successfully!")

# Transform attendance data
def transform_attendance_data(df, working_days):
    date_columns = [str(day) for day in working_days]
    transformed_df = pd.DataFrame(columns=["Employee"] + date_columns)
    for _, row in df.iterrows():
        employee = row["Employee"]
        attended_dates = row["Dates"].split(", ") if isinstance(row["Dates"], str) else []
        row_data = {"Employee": employee}
        for date in date_columns:
            row_data[date] = "Office" if date in attended_dates else "-"
        transformed_df = pd.concat([transformed_df, pd.DataFrame([row_data])], ignore_index=True)
    return transformed_df

transformed_df = transform_attendance_data(df, working_days)

# Show Full Attendance Record
st.subheader("📛 Full Attendance Record")
st.dataframe(transformed_df)

# Generate summary
total_employees = len([emp for emp in employees[1:] if emp in df["Employee"].values])
summary_data = []
for employee in employees[1:]:
    emp_data = df[df["Employee"] == employee]
    if not emp_data.empty and isinstance(emp_data["Dates"].values[0], str):
        attended_dates = emp_data["Dates"].values[0].split(', ')
        office_days = len(attended_dates)
        percentage = 100 if "N/A" in attended_dates else min((office_days / 8) * 100, 100)
    else:
        office_days = 0
        percentage = 0
    summary_data.append({
        "Employee": employee,
        "Office Days": str(office_days),  # FIXED: Convert to string to avoid Arrow error
        "Attendance %": f"{percentage:.2f}%"
    })

# Fix the overall summary row
company_attendance_percentage = sum(float(entry["Attendance %"].strip('%')) for entry in summary_data) / total_employees if total_employees > 0 else 0
overall_summary = pd.DataFrame([{
    "Employee": "Overall Attendance %",
    "Office Days": "N/A",  # FIXED: Use "N/A" instead of "-"
    "Attendance %": f"{company_attendance_percentage:.2f}%"
}])

summary_df = pd.concat([pd.DataFrame(summary_data), overall_summary], ignore_index=True)

# Display updated summary table
st.subheader("📊 QET-1 Attendance Summary")
st.table(summary_df)

# Download attendance report
st.subheader("📅 Download Attendance Report")
csv = transformed_df.to_csv(index=False)
st.download_button("📂 Download CSV", csv, "attendance_report.csv", "text/csv")
