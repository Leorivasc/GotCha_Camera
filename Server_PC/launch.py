import subprocess
from classes import SQLiteDB
import os


connection = SQLiteDB()
connection.connect()
cameras = connection.query_data("cameras")
connection.close_connection()
script = "movement_framesubtraction_threeframes.py"
server = "gunicorn -c ./app/gunicorn_config.py app:app"

# Run the script for each camera
def run_scripts():
    processes = []
    for camera in cameras:
        #camera_id = camera[0]
        camera_name = camera[1]
        camera_url = camera[2]

        try:
            env= os.environ.copy()
            proc = subprocess.Popen(["python", script]+[camera_name, camera_url], env=env)
            processes.append(proc)
            print(f"Process {camera_name} started")
        except Exception as e:
            print(f"Error al ejecutar los scripts: {e}")

    #proc = subprocess.Popen(["gunicorn", "-c", "app/gunicorn_config.py", "app/app:app"])
    #processes.append(proc)

    # Wait for all processes to finish
    for proc in processes:
        proc.wait()
        pass

if __name__ == "__main__":
    run_scripts()
