import sys
import psycopg2
import time
import tkinter as tk
from tkintermapview import TkinterMapView
import pandas as pd
import os
import functions

if __name__ == '__main__':

    # Connect to DB
    con = functions.connect("localhost", "festival", "postgres", "Peribff128!")
    # Check for PostGIS extension, check if tables exist -> if not then set up tables and add data from GitHub
    functions.setup(con)

    # Chill for a second
    time.sleep(1)
    # Get user coordinates and the task number from user
    userY, userX, task = functions.decide()

    # If there is no user location given -> pass
    # Else update user_location table in postgres
    if userY == 0:
        pass
    else:
        # clear old position
        remove = "DELETE FROM user_location;"
        functions.sql_in(con, remove)
        # add new position
        add_user_pos = "INSERT INTO user_location(id, geom) VALUES(1, ST_GeomFromText('Point(%s %s)', 4326));" % (userX, userY)
        functions.sql_in(con, add_user_pos)

    # Perform queries, updates, etc. according the given task number and with all necessary user input
    map, args = functions.perform_task(con, task)

    # Close the connection to the db
    con.close()

    print("\nTask complete. See you next time!")
    # args = {"festival_area" : "festival_area", "main_stage": "101"}
    if map == True:
        time.sleep(2)
        functions.map(userY, userX, args)
