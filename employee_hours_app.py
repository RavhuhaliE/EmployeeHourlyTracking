import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import schedule
import time
import threading
from datetime import datetime

# Initialize the data store
employee_data = []
employees = []

# Function to calculate worked hours
def calculate_hours():
    global employee_data
    if not employee_data:
        messagebox.showerror("Error", "No employee data available.")
        return

    df = pd.DataFrame(employee_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day_name()

    df['Sunday/Public Holiday Hours'] = df.apply(
        lambda row: (row['Regular Hours'] + row['Overtime Hours']) * 2 if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Regular Hours'] + row['Overtime Hours'],
        axis=1
    )

    df['Saturday/Overtime Hours'] = df.apply(
        lambda row: row['Regular Hours'] + row['Overtime Hours'] * 1.5 if row['Day'] == 'Saturday' else row['Regular Hours'] + row['Overtime Hours'],
        axis=1
    )

    df['Total Adjusted Hours'] = df.apply(
        lambda row: row['Sunday/Public Holiday Hours'] if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Saturday/Overtime Hours'],
        axis=1
    )

    return df

# Function to calculate monthly total hours per employee
def calculate_monthly_totals():
    df = calculate_hours()
    if df is not None:
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_totals = df.groupby(['Employee', 'Month'])['Total Adjusted Hours'].sum().reset_index()
        return monthly_totals
    return None

# Function to save results to a CSV file
def export_results():
    df = calculate_hours()
    if df is not None:
        current_week = datetime.now().isocalendar()[1]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f'worked_hours_week_{current_week}.csv', filetypes=[("CSV files", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "Results saved successfully.")

# Function to schedule export every Monday at 5 AM SAST
def schedule_weekly_export():
    df = calculate_hours()
    if df is not None:
        current_week = datetime.now().isocalendar()[1]
        df.to_csv(f'worked_hours_week_{current_week}.csv', index=False)
        print("Weekly results exported successfully.")  # Logging instead of messagebox

def schedule_task():
    schedule.every().monday.at("05:00").do(schedule_weekly_export)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to add employee hours
def add_employee_hours():
    global employee_data
    employee = employee_combobox.get()
    date = date_entry.get_date().strftime('%Y-%m-%d')
    regular_hours = regular_hours_entry.get()
    overtime_hours = overtime_hours_entry.get()
    public_holiday = public_holiday_var.get()
    absence = absence_var.get()
    absence_reason = absence_reason_entry.get()

    if absence and not absence_reason:
        messagebox.showerror("Error", "Please provide a reason for absence.")
        return

    try:
        regular_hours = float(regular_hours)
        overtime_hours = float(overtime_hours)
    except ValueError:
        messagebox.showerror("Error", "Hours must be a number.")
        return

    employee_data.append({
        'Employee': employee,
        'Date': date,
        'Regular Hours': 0 if absence else regular_hours,
        'Overtime Hours': 0 if absence else overtime_hours,
        'Public Holiday': 'Yes' if public_holiday else 'No',
        'Absence': 'Yes' if absence else 'No',
        'Absence Reason': absence_reason if absence else ''
    })

    regular_hours_entry.delete(0, tk.END)
    overtime_hours_entry.delete(0, tk.END)
    public_holiday_var.set(False)
    absence_var.set(False)
    absence_reason_entry.delete(0, tk.END)

    update_treeview()

def update_treeview():
    for row in tree.get_children():
        tree.delete(row)
    for row in employee_data:
        tree.insert("", tk.END, values=list(row.values()))

# Function to add employee to the list
def add_employee():
    global employees
    employee = employee_name_entry.get()
    if employee and employee not in employees:
        employees.append(employee)
        update_employee_combobox()
        employee_name_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Invalid or duplicate employee name.")

def update_employee_combobox():
    employee_combobox['values'] = employees

# Function to show monthly totals
def show_monthly_totals():
    monthly_totals = calculate_monthly_totals()
    if monthly_totals is not None:
        totals_window = tk.Toplevel(root)
        totals_window.title("Monthly Total Hours per Employee")
        columns = ['Employee', 'Month', 'Total Adjusted Hours']
        totals_tree = ttk.Treeview(totals_window, columns=columns, show='headings')
        for col in columns:
            totals_tree.heading(col, text=col)
        totals_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for _, row in monthly_totals.iterrows():
            totals_tree.insert("", tk.END, values=list(row))
    else:
        messagebox.showerror("Error", "No data available for monthly totals.")

# Main application
root = tk.Tk()
root.title("Employee Worked Hours Calculator")

# Create and place the GUI components
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Employee management
ttk.Label(frame, text="Add Employee:").grid(row=0, column=0, sticky=tk.W)
employee_name_entry = ttk.Entry(frame)
employee_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
ttk.Button(frame, text="Add", command=add_employee).grid(row=0, column=2, padx=5)

# Daily entry
ttk.Label(frame, text="Employee:").grid(row=1, column=0, sticky=tk.W)
employee_combobox = ttk.Combobox(frame, state="readonly")
employee_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Date:").grid(row=2, column=0, sticky=tk.W)
date_entry = DateEntry(frame, width=19, background='darkblue', foreground='white', borderwidth=2)
date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Regular Hours:").grid(row=3, column=0, sticky=tk.W)
regular_hours_entry = ttk.Entry(frame)
regular_hours_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Overtime Hours:").grid(row=4, column=0, sticky=tk.W)
overtime_hours_entry = ttk.Entry(frame)
overtime_hours_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

public_holiday_var = tk.BooleanVar()
ttk.Checkbutton(frame, text="Public Holiday", variable=public_holiday_var).grid(row=5, column=0, sticky=tk.W)

absence_var = tk.BooleanVar()
ttk.Checkbutton(frame, text="Absence", variable=absence_var).grid(row=5, column=1, sticky=tk.W)

ttk.Label(frame, text="Absence Reason:").grid(row=6, column=0, sticky=tk.W)
absence_reason_entry = ttk.Entry(frame)
absence_reason_entry.grid(row=6, column=1, sticky=(tk.W, tk.E))

ttk.Button(frame, text="Add Entry", command=add_employee_hours).grid(row=7, column=0, columnspan=2, pady=10)

# Treeview for displaying data
columns = ('Employee', 'Date', 'Regular Hours', 'Overtime Hours', 'Public Holiday', 'Absence', 'Absence Reason')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('Employee', text='Employee')
tree.heading('Date', text='Date')
tree.heading('Regular Hours', text='Regular Hours')
tree.heading('Overtime Hours', text='Overtime Hours')
tree.heading('Public Holiday', text='Public Holiday')
tree.heading('Absence', text='Absence')
tree.heading('Absence Reason', text='Absence Reason')
tree.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Button(root, text="Export Results", command=export_results).grid(row=9, column=0, columnspan=3, pady=10)
ttk.Button(root, text="Show Monthly Totals", command=show_monthly_totals).grid(row=10, column=0, columnspan=3, pady=10)

# Start the scheduling thread
threading.Thread(target=schedule_task, daemon=True).start()

root.mainloop()

# Function to show monthly totals
def show_monthly_totals():
    monthly_totals = calculate_monthly_totals()
    if monthly_totals is not None:
        totals_window = tk.Toplevel(root)
        totals_window.title("Monthly Total Hours per Employee")
        columns = ['Employee', 'Month', 'Total Adjusted Hours']
        totals_tree = ttk.Treeview(totals_window, columns=columns, show='headings')
        for col in columns:
            totals_tree.heading(col, text=col)
        totals_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for _, row in monthly_totals.iterrows():
            totals_tree.insert("", tk.END, values=list(row))
    else:
        messagebox.showerror("Error", "No data available for monthly totals.")

# Main application
root = tk.Tk()
root.title("Employee Worked Hours Calculator")

# Create and place the GUI components
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Employee management
ttk.Label(frame, text="Add Employee:").grid(row=0, column=0, sticky=tk.W)
employee_name_entry = ttk.Entry(frame)
employee_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
ttk.Button(frame, text="Add", command=add_employee).grid(row=0, column=2, padx=5)

# Daily entry
ttk.Label(frame, text="Employee:").grid(row=1, column=0, sticky=tk.W)
employee_combobox = ttk.Combobox(frame, state="readonly")
employee_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Date:").grid(row=2, column=0, sticky=tk.W)
date_entry = DateEntry(frame, width=19, background='darkblue', foreground='white', borderwidth=2)
date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Regular Hours:").grid(row=3, column=0, sticky=tk.W)
regular_hours_entry = ttk.Entry(frame)
regular_hours_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Overtime Hours:").grid(row=4, column=0, sticky=tk.W)
overtime_hours_entry = ttk.Entry(frame)
overtime_hours_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

public_holiday_var = tk.BooleanVar()
ttk.Checkbutton(frame, text="Public Holiday", variable=public_holiday_var).grid(row=5, column=0, sticky=tk.W)

absence_var = tk.BooleanVar()
ttk.Checkbutton(frame, text="Absence", variable=absence_var, command=toggle_absence_fields).grid(row=5, column=1, sticky=tk.W)

ttk.Label(frame, text="Absence Reason:").grid(row=6, column=0, sticky=tk.W)
absence_reason_entry = ttk.Entry(frame)
absence_reason_entry.grid(row=6, column=1, sticky=(tk.W, tk.E))

ttk.Button(frame, text="Add Entry", command=add_employee_hours).grid(row=7, column=0, columnspan=2, pady=10)

# Treeview for displaying data
columns = ('Employee', 'Date', 'Regular Hours', 'Overtime Hours', 'Public Holiday', 'Absence', 'Absence Reason')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('Employee', text='Employee')
tree.heading('Date', text='Date')
tree.heading('Regular Hours', text='Regular Hours')
tree.heading('Overtime Hours', text='Overtime Hours')
tree.heading('Public Holiday', text='Public Holiday')
tree.heading('Absence', text='Absence')
tree.heading('Absence Reason', text='Absence Reason')
tree.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Button(root, text="Export Results", command=export_results).grid(row=9, column=0, columnspan=3, pady=10)
ttk.Button(root, text="Show Monthly Totals", command=show_monthly_totals).grid(row=10, column=0, columnspan=3, pady=10)

# Start the scheduling thread
threading.Thread(target=schedule_task, daemon=True).start()

root.mainloop()
