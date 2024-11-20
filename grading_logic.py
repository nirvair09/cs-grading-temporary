import pandas as pd
import numpy as np

def process_grading(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path, header=None)  # Load without a header for flexible column identification

    # Extract the assessment components, max marks, and weightage
    assessment_columns = df.iloc[0, 2:].values  # Assuming first row has column names like MidSem, Endsem, etc.
    max_marks = df.iloc[1, 2:].values  # The second row contains max marks
    weightage = df.iloc[2, 2:].values  # The third row contains weightage

    # Prepare the dataframe containing student details (excluding first 3 rows)
    student_data = df.iloc[3:, :].reset_index(drop=True)

    # Assign column names to the student data (Roll, Name, and Assessment Columns)
    student_data.columns = ['Roll', 'Name'] + list(assessment_columns)

    # Convert numeric columns (assessments) to float for calculations
    for col in assessment_columns:
        student_data[col] = pd.to_numeric(student_data[col], errors='coerce')

    # Dynamically calculate scaled marks based on weightage and max marks
    for idx, component in enumerate(assessment_columns):
        max_mark = max_marks[idx]  # Max mark for the component
        weight = weightage[idx]    # Weightage for the component
        student_data[f'Scaled_{component}'] = (student_data[component] / max_mark) * weight

    # Calculate Grand Total (scaled sum)
    student_data['Grand Total'] = student_data[[f'Scaled_{component}' for component in assessment_columns]].sum(axis=1)

    # Function to assign grades dynamically based on sorted total scores
    def assign_grades(df):
        total_students = len(df)
        sorted_df = df.sort_values(by='Grand Total', ascending=False).reset_index(drop=True)

        # Calculate the number of students per grade dynamically based on the total number of students
        GRADE_QUOTA = {
            "AA": 5,  # Top 5% get AA
            "AB": 10,
            "BB": 20,
            "BC": 25,
            "CC": 20,
            "CD": 10,
            "DD": 10
        }

        grade_counts = {grade: round(total_students * (percent / 100)) for grade, percent in GRADE_QUOTA.items()}

        grades = []
        for grade, count in grade_counts.items():
            grades.extend([grade] * count)

        grades = grades[:total_students] + ['F'] * (total_students - len(grades))  # Fill the remaining with F

        sorted_df['Grade'] = grades
        return sorted_df

    # Apply grading and create output DataFrames sorted by grade and roll number
    graded_df = assign_grades(student_data)
    graded_df_roll_sorted = graded_df.sort_values(by='Roll', ascending=True)

    # Save results to an Excel file with two sheets
    output_file = "graded_output_Chandradeep.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        graded_df.to_excel(writer, sheet_name="Sorted by Grade", index=False)
        graded_df_roll_sorted.to_excel(writer, sheet_name="Sorted by Roll Number", index=False)

    return output_file
