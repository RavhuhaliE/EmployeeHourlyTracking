import pandas as pd

# Sample data
data = {
    'Employee': ['John', 'Jane', 'Bob', 'Alice'],
    'Date': ['2024-06-01', '2024-06-02', '2024-06-03', '2024-06-04'],
    'Hours Worked': [8, 7, 6, 5],
    'Public Holiday': ['No', 'No', 'Yes', 'No'],
    'Overtime': ['Yes', 'No', 'No', 'Yes']
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Determine the day of the week
df['Day'] = df['Date'].dt.day_name()

# Calculate adjusted hours for Sundays and public holidays
df['Sunday/Public Holiday Hours'] = df.apply(
    lambda row: row['Hours Worked'] * 2 if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Hours Worked'],
    axis=1
)

# Calculate adjusted hours for Saturdays and overtime
df['Saturday/Overtime Hours'] = df.apply(
    lambda row: row['Hours Worked'] * 1.5 if row['Day'] == 'Saturday' or row['Overtime'] == 'Yes' else row['Hours Worked'],
    axis=1
)

# Determine total adjusted hours
df['Total Adjusted Hours'] = df.apply(
    lambda row: row['Sunday/Public Holiday Hours'] if row['Day'] == 'Sunday' or row['Public Holiday'] == 'Yes' else row['Saturday/Overtime Hours'],
    axis=1
)

# Display the DataFrame
print(df)
