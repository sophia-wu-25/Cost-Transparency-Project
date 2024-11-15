import mysql.connector
import requests
from bs4 import BeautifulSoup
from db_config import db_config
from getSheetID import getSheetID

class GoogleSheetsAPI:
    def __init__(self, spreadsheet_id, api_key):
        self.spreadsheet_id = spreadsheet_id
        self.api_key = api_key
        self.base_url = 'https://sheets.googleapis.com/v4/spreadsheets/'

    def fetch_data(self):
        url = f'{self.base_url}{self.spreadsheet_id}?key={self.api_key}&includeGridData=true&fields=sheets.data.rowData.values(hyperlink,userEnteredValue)'
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Request failed with status code {response.status_code}')
            return None

# Modify the import_data_to_mysql function
import mysql.connector
from mysql.connector import errorcode

def import_data_to_mysql(db_config, json_data, name):
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        sheets = json_data.get("sheets", [])

        # Create the table if it doesn't exist
        create_table_query = f"CREATE TABLE IF NOT EXISTS {name} (id INT AUTO_INCREMENT PRIMARY KEY"
        count = 1

        # Iterate over the data to dynamically add columns
        for sheet in sheets:
            data = sheet.get("data", [])
            if data:
                for row in data:
                    rowData = row.get("rowData", [])
                    if rowData:
                        header_row = rowData[2].get("values", [])
                        if header_row:
                            for header in header_row:
                                if header.get("userEnteredValue", {}).get("stringValue", ""):
                                    column_name = header["userEnteredValue"]["stringValue"].replace(" ", "_")
                                    create_table_query += f", {column_name} VARCHAR(255)"
                                    count += 1

        create_table_query += ")"
        cursor.execute(create_table_query)

        # Truncate the table to remove existing data
        truncate_query = f"TRUNCATE TABLE {name}"
        cursor.execute(truncate_query)

        for sheet in sheets:
            data = sheet.get("data", [])

            for rowData in data:
                rows = rowData.get("rowData", [])[3:]

                for row in rows:
                    values = []

                    for cell in row.get("values", []):
                        if cell.get("hyperlink", "") != "":
                            stringValue = str(cell.get("hyperlink", ""))
                            header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36", "Accept-Language": "en-GB, en-US; q=0.9, en;q=0.8"}
                            if "amazon" in stringValue:
                                response = requests.get(stringValue, headers=header)
                                soup = BeautifulSoup(response.content, "lxml")
                                price = soup.find(class_="a-offscreen").get_text()
                                print(stringValue + " " + price)
                                values.append(stringValue)
                                values.append(price)
                            else:
                                print(stringValue + " is not an amazon link")
                        else:
                            userEnteredValue = cell.get("userEnteredValue", {})
                            stringValue = userEnteredValue.get("stringValue", "")
                            values.append(stringValue)
                    
                    if not all(value == "" for value in values):
                        # Ensure that each row has at least one value
                        values += [''] * (count - len(values)) 

                        values_tuple = tuple(values)

                        #changes based on row length
                        placeholders = ', '.join(['%s'] * len(values))

                        #debugging
                        print("Insert Query:", f"INSERT INTO {name} VALUES ({placeholders})")
                        print("Values Tuple:", values_tuple)
                        print("Number of Columns:", len(values))
                        print("Number of Placeholders:", placeholders.count('%s'))
                        insert_query = f"INSERT INTO {name} VALUES ({placeholders})"

                        # Extract the primary key value from the row data
                        id_value = values[0]  # Assuming the primary key is the first column

                        # Before inserting, check if the primary key already exists in the table
                        cursor.execute(f"SELECT id FROM {name} WHERE id = %s", (id_value,))
                        if cursor.fetchone() is None:
                            # Primary key doesn't exist, proceed with the insertion
                            cursor.execute(insert_query, values)
                            connection.commit()
                        else:
                            print(f"Primary key {id_value} already exists in the table.")


        print("Data imported successfully into MySQL.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Closes connection
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

#ADMIN TOOLS
def get_row_ID(cursor, table_name, teacher_name, title):
    try:
        # convert to lowercase
        teacher_name = teacher_name.lower()
        
        # convert to lowercase/no italics
        soup = BeautifulSoup(title, 'html.parser')
        clean_title = soup.get_text().strip().lower()

        select_query = f"SELECT id FROM {table_name} WHERE LOWER(Teacher) = %s AND LOWER(Title) = %s"
        cursor.execute(select_query, (teacher_name, clean_title))
        row = cursor.fetchone()
        if row:
            print(row[0])
            return row[0] 
        else:
            return None
    except Exception as e:
        print(f"Error finding row ID: {e}")

# Example usage:
# row_id = get_row_ID(cursor, "fall_textbooks", "Onion", "White Teeth")
# if row_id is not None:
#     print(f"Row ID for teacher 'Onion' and title 'White Teeth' is: {row_id}")
# else:
#     print("Combination of teacher and title not found.")

def edit_row(cursor, table_name, row_id, new_values):
    try:
        update_query = f"UPDATE {table_name} SET Course_Name = %s, Teacher = %s, Title = %s, Author = %s, " \
                       f"ISBN = %s, best_link = %s WHERE id = %s"
        cursor.execute(update_query, (*new_values, row_id))
        print(f"Row with ID {row_id} updated successfully.")
    except Exception as e:
        print(f"Error updating row: {e}")

def insert_row(cursor, table_name, values):
    try:
        insert_query = f"INSERT INTO {table_name} (Course_Name, Teacher, Title, Author, ISBN, best_link) " \
                       f"VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, values)
        print("New row inserted successfully.")
    except Exception as e:
        print(f"Error inserting row: {e}")

def delete_row(cursor, table_name, row_id):
    try:
        delete_query = f"DELETE FROM {table_name} WHERE id = %s"
        cursor.execute(delete_query, (row_id,))
        print(f"Row with ID {row_id} deleted successfully.")
        connection.commit()
    except Exception as e:
        print(f"Error deleting row: {e}")
        connection.rollback()
# Example usage:
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# To edit a row with ID 1 (can replace with get_row_ID):
# edit_row(cursor, "textbooks", get_row_ID(cursor, "winter_textbooks", "Teacher", "Title"), ("New Course", "New Teacher", "New Title", "New Author", "New Copyright",
                                #    "New ISBN", "New Link"))

# To insert a new row:
# insert_row(cursor, "winter_textbooks", ("Course", "Teacher", "Title", "Author", "ISBN", "Link"))

# To delete a row with ID 1:
# delete_row(cursor, "textbooks", get_row_ID(cursor, "winter_textbooks", "Teacher", "Title"))

# # Don't forget to commit the changes and close the connection afterwards
# connection.commit()
# connection.close()    


def get_table_name(json_data):
    # Access the first row of the first sheet
    first_sheet = json_data.get("sheets", [])[0]  # Get the first sheet
    first_row_values = first_sheet.get("data", [])[0].get("rowData", [])[0].get("values", [])

    for cell in first_row_values:
        cell_value = cell.get("userEnteredValue", {}).get("stringValue", "").lower()
        if "fall" in cell_value:
            return "fall_textbooks"
        elif "winter" in cell_value:
            return "winter_textbooks"
        elif "spring" in cell_value:
            return "spring_textbooks"
    #default table name 
    return "textbooks"
    
# gets links automatically
sheets = getSheetID("https://peddie.bywatersolutions.com/")
api_key = '[REDACTED]'

for spreadsheet_id in sheets.scraper():
    sheets_api = GoogleSheetsAPI(spreadsheet_id, api_key)
    json_data = sheets_api.fetch_data()
    
    table_name = get_table_name(json_data)
    print(table_name)
    
    import_data_to_mysql(db_config, json_data, table_name)

import_data_to_mysql(db_config, json_data, "winter_textbooks")
import_data_to_mysql(db_config, json_data, "fall_textbooks")

