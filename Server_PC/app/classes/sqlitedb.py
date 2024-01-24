import sqlite3
import os

class SQLiteDB:
    """##Generic## SQLite database class.
    Attributes:
        db_name (str): The name of the database file.
        connection (sqlite3.Connection): The database connection object.
        cursor (sqlite3.Cursor): The database cursor object.
    """
    def __init__(self):
       
        #Get the path to the database file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        db_name = os.path.join(thisfolder, '..', 'db', 'database.sqlite')

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

    #Update data
    def update_data(self, table_name, data, condition=None):
        query = f"UPDATE {table_name} SET "
        query += ", ".join(f"{key} = '{value}'" for key, value in data.items()) #key = 'value' items
        if condition:
            query += f" WHERE {condition}"

        self.cursor.execute(query)
        self.connection.commit()
        return True




    #Close connection
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
