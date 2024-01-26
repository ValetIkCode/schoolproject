from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from connect import connection

app = Flask(__name__)

def read_events_file(file_path):
    return pd.read_excel(file_path)

def check_status_column(df):
    if 'Статус' not in df.columns:
        raise ValueError("Стобец 'Статус' отсутствует")

def read_students_file(file_path):
    return pd.read_excel(file_path)

def select_events_without_entry(df):
    return df[~((df['Статус'] == 'Обучающиеся') & (df['Событие'] == 'вход по карте'))]

def check_required_columns_in_students(df, required_columns):
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Ошибка")

def filter_students(df_students, df_events, columns):
    filtered_events = select_events_without_entry(df_events)
    check_required_columns_in_students(df_students, columns)

    filtered_students = df_students[~df_students['ФИО'].isin(filtered_events['ФИО'])]
    filtered_students = filtered_students[columns]

    return filtered_students

def save_uploaded_file(file, upload_directory):
    upload_path = os.path.join(upload_directory, file.filename)
    file.save(upload_path)
    return upload_path

def generate_output_path(output_directory, file_name):
    return os.path.join(output_directory, file_name)

def insert_filtered_students_to_database(df_students):
    conn = connection()
    cursor = conn.cursor()

    for index, row in df_students.iterrows():
        add_student_query = "INSERT INTO ExcelStudents (group_name, full_name) VALUES (%s, %s)"
        data = (row['Группа'], row['ФИО'])
        try:
            cursor.execute(add_student_query, data)
        except Exception as e:
            print(f"Error inserting row {row}: {str(e)}")

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return render_template('index.html', message='No file selected')

        upload_directory = 'uploads'
        all_students_path = os.path.join(os.path.dirname(__file__), 'all_students.xlsx')

        uploaded_file_path = save_uploaded_file(uploaded_file, upload_directory)
        df_events = read_events_file(uploaded_file_path)
        check_status_column(df_events)

        df_students = read_students_file(all_students_path)
        filtered_students = filter_students(df_students, df_events, ['Группа', 'ФИО'])

        insert_filtered_students_to_database(filtered_students)

        output_file_path = generate_output_path(upload_directory, 'filtered_students.xlsx')
        filtered_students.to_excel(output_file_path, index=False)

        return send_file(output_file_path, as_attachment=True, download_name='filtered_students.xlsx')

    except Exception as e:
        return render_template('index.html', message=f'An error occurred: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)