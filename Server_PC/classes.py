import sqlite3
import requests


class SQLiteDB:
    def __init__(self, db_name="app/database.sqlite"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    #Connect to DB file
    def connect(self): 
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    #Create table (str table_name, str comma separated column names)
    def create_table(self, table_name, columns):      
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(query)
        self.connection.commit()

    #Insert data
    def insert_data(self, table_name, data):
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(query, data)
        self.connection.commit()

    #Query data
    def query_data(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}" #optional

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    #Close connection
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()


def do_get(url):
    """Perform a GET request to the specified URL.
    Args:
        url (str): The URL to which the request will be performed.
        Returns:
        str: The response text if the request was successful, an error message otherwise.
    """

    try:
        #Perform GET
        print("Connecting to "+url)
        ans = requests.get(url)

        #Verify status ok or else
        if ans.status_code == 200:
            print(f"Response: {ans.text}")
            return(f"{ans.text}")
            pass
        else:
            print(f"Connection error: {ans.status_code}")
            return(f"Connection error: {ans.status_code}")

    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return("Error: Timeout")
    except requests.exceptions.RequestException as e:
        print(f"Bad request: {e}")
        return(f"Bad request: {e}")
