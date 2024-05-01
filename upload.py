import numpy as np


def read_dictionary_from_npy(file_path):
    try:
        data = np.load(file_path, allow_pickle=True)
        if isinstance(data, np.ndarray):
            dictionary = data.item()
            return dictionary
        else:
            print("Error: The npy file does not contain a dictionary.")
    except FileNotFoundError:
        print("Error: File not found.")


import mysql.connector


def create_conn():
    # Connect to the database
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="aditya@11",
        database="exercise",
    )

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()
    return cursor, connection


def upload_file_to_server(dictionary, cursor, connection):

    if not dictionary:
        return

    table_name = "Fitness_Info"

    # Insert rows into the table
    Exercise_Name = dictionary["exercise_selected"]
    Correct_Count = dictionary["correct"]
    Incorrect_Count = dictionary["incorrect"]
    Start_Time = dictionary["start_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    End_Time = dictionary["end_timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    # print(values)
    insert_query = f'INSERT INTO Fitness_Info (Exercise_Name,Correct_Count,Incorrect_Count,Start_Time,End_Time) VALUES("{Exercise_Name}",{Correct_Count},{Incorrect_Count},"{Start_Time}","{End_Time}");'

    try:
        cursor.execute(insert_query)
    except Exception as e:
        print(e)

    # Commit the changes and close the connection
    connection.commit()

def read_all_records(cursor):
    select_query = "SELECT * FROM Fitness_Info;"
    cursor.execute(select_query)
    records = cursor.fetchall()
    for record in records:
        print("FROM DATABASE -> ",record)

'''
# Example usage
file_path = "dataset.npy"
dictionary = read_dictionary_from_npy(file_path)

cursor, connection = create_conn()

upload_file_to_server(dictionary["Curls"], cursor)
upload_file_to_server(dictionary["Squats Beginner"], cursor)
upload_file_to_server(dictionary["Squats Pro"], cursor)

connection.commit()
connection.close()

'''