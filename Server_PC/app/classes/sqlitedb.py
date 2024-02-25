#CREDIT: Placeholders idea from https://stackoverflow.com/questions/14108162/insert-list-into-sqlite-table-python

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
        '''Constructor for the SQLiteDB class.'''
       
        #Get the path to the database file
        thisfolder = os.path.dirname(os.path.abspath(__file__))
        db_name = os.path.join(thisfolder, '..', 'db', 'database.sqlite')

        self.db_name = db_name
        self.connection = None
        self.cursor = None

    #Connect to DB file
    def connect(self): 
        self.connection = sqlite3.connect(self.db_name, timeout=5) #to prevent database is locked error
        self.cursor = self.connection.cursor()

    #Create table (str table_name, str comma separated column names)
    def create_table(self, table_name, columns):   
        self.connect()   
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(query)
        self.connection.commit()
        self.close_connection()




    #Insert data
    def insert_data(self, table_name, data):
        '''Insert data into a table.
        Args:
            table_name (str): The name of the table to insert data into.
            data (dict): A dictionary containing the data to insert. The keys should match the column names in the table.
        Returns:
            int: The ID of the inserted row.'''
        
        self.connect()
        placeholders = ", ".join("?" * len(data))

        keys = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.connection.commit()
        id = self.cursor.lastrowid
        self.close_connection()
        return id




    #Query data
    def query_data(self, table_name, condition=None):
        '''Query data from a table.
        Args:
            table_name (str): The name of the table to query.
            condition (str): The condition to use in the query. Optional.
        Returns:
            list: A list of tuples containing the query results. Each tuple contains the data for a row in the table.'''

        self.connect()
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}" #optional

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.close_connection()
        return result





    #Query data as dict
    def query_data_dict(self, table_name, condition=None):
        '''Query data from a table and return as a list of dictionaries.
        Args:
            table_name (str): The name of the table to query.
            condition (str): The condition to use in the query. Optional.
        Returns:
            list: A list of dictionaries containing the query results. Each dictionary contains the data for a row in the table.'''
        
        self.connect()
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        cursor = self.cursor

        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except:
            result = None

        finally:
            self.close_connection()
            return result
        




    #Update data
    def update_data(self, table_name, data, condition=None):
        '''Update data in a table.
        Args:
            table_name (str): The name of the table to update.
            data (dict): A dictionary containing the data to update. The keys should match the column names in the table.
            condition (str): The condition to use in the query. Optional.
        Returns:
            bool: True if the update was successful, False otherwise.'''
        
        self.connect()

        #Build the query
        query = f"UPDATE {table_name} SET "
        query += ", ".join(f"{key} = '{value}'" for key, value in data.items()) #key = 'value' items
        if condition:
            query += f" WHERE {condition}" #Add the condition if it exists

        self.cursor.execute(query)
        self.connection.commit()
        self.close_connection()
        return True





    #Delete data
    def delete_data(self, table_name, condition):
        '''Delete data from a table.
        Args:
            table_name (str): The name of the table to delete data from.
            condition (str): The condition to use in the query. Must be in the format "id=1" or "name='Camera11'".
                            Only id and name are allowed as condition. Anything else will return False.
        Returns:
            bool: True if the delete was successful, False otherwise.'''

        self.connect()

        #Allow only id and name as condition
        if condition.startswith("id=") or condition.startswith("name="): 
            query = f"DELETE FROM {table_name} WHERE {condition} LIMIT 1" #LIMIT 1 to force only one row to be deleted each call
        else:
            return False

        self.cursor.execute(query)
        self.connection.commit()

        affected_rows = self.cursor.rowcount #Should always be 1

        self.close_connection()

        if affected_rows == 0: #nothing was deleted
            return False
        else:
            return True




    #Close connection
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
