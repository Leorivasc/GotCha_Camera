import sqlite3
import requests
import datetime
import cv2

class SQLiteDB:
    """##Generic## SQLite database class.
    Attributes:
        db_name (str): The name of the database file.
        connection (sqlite3.Connection): The database connection object.
        cursor (sqlite3.Cursor): The database cursor object.
    """
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


    #Query data as dict
    def query_data_dict(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        cursor = self.cursor

        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            self.connection.close()
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




def read_config(camera_name):
    """Read the cameras configuration from database by using SQLiteDB class.
    Args:
        camera_name (str): The name of the camera to be read.
    Returns:
        Camera information row as dict.
    """
    connection = SQLiteDB()
    connection.connect()
    camera = connection.query_data_dict("cameras","name='"+camera_name+"'")
    connection.close_connection()
    return camera


def add_datetime(frame):
    #Get date
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    #Configurar el texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, frame.shape[0] - 10)
    font_scale = 0.5
    font_color = (0, 255, 0)  # Verde
    line_type = 1

    #Put text
    cv2.putText(frame, time, bottom_left_corner, font, font_scale, font_color, line_type)
    return frame

