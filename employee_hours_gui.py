import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Function to calculate the worked hours
def calculate_hours(data):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day_name()

    df['Sunday/Public Holiday Hours'] = df.apply(
        lambda row: row['Hours Worked'] * 2 if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Hours Worked'],
        axis=1
    )

    df['Saturday/Overtime Hours'] = df.apply(
        lambda row: row['Hours Worked'] * 1.5 if row['Day'] == 'Saturday' or row['Overtime'] == 'Yes' else row['Hours Worked'],
        axis=1
    )

    df['Total Adjusted Hours'] = df.apply(
        lambda row: row['Sunday/Public Holiday Hours'] if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Saturday/Overtime Hours'],
        axis=1
    )

    return df

# Function to open a file dialog and load the data
def load_data():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            data = pd.read_csv(file_path)
            if set(['Employee', 'Date', 'Hours Worked', 'Public Holiday', 'Overtime']).issubset(data.columns):
                df_result = calculate_hours(data)
                result_text.delete('1.0', tk.END)
                result_text.insert(tk.END, df_result.to_string(index=False))
            else:
                messagebox.showerror("Error", "CSV file must contain 'Employee', 'Date', 'Hours Worked', 'Public Holiday', and 'Overtime' columns.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

# Function to save the results to a CSV file
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            data = result_text.get('1.0', tk.END)
            df_result = pd.read_csv(pd.compat.StringIO(data))
            df_result.to_csv(file_path, index=False)
            messagebox.showinfo("Success", "Results saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

# Create the main application window
root = tk.Tk()
root.title("Employee Worked Hours Calculator")

# Create and place the GUI components
load_button = tk.Button(root, text="Load CSV", command=load_data)
load_button.pack(pady=10)

result_label = tk.Label(root, text="Results:")
result_label.pack()

result_text = tk.Text(root, wrap=tk.NONE, height=20, width=80)
result_text.pack(pady=10)

save_button = tk.Button(root, text="Save Results", command=save_results)
save_button.pack(pady=10)

# Run the application
root.mainloop()
