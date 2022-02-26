# if not installed: pip install psycopg2
import sys
import psycopg2
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkintermapview import TkinterMapView
import pandas as pd
import os

def connect(host, database, user, password):
    # Connect to the db
    try:
        con = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password)
    except:
        print(f"Unable to connect to the database.")
    return con

def check_exists(con, table):

    cur = con.cursor()
    query = f"SELECT CASE WHEN (EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public' AND  TABLE_NAME = '{str(table)}')) THEN 'TRUE' ELSE 'FALSE' END;"
    try:
        cur.execute(query)
        result = cur.fetchone()
        exists = str(result)

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        exists = "no"

    con.commit()
    cur.close()
    print(table, exists)

    return exists


def sql_in(con, sql_statement):
    """
    Tries to execute a statement in the database
    """
    cur = con.cursor()
    try:
        cur.execute(sql_statement)
        con.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing the statement {str(sql_statement)}.")
        print("Error: %s" % error)

    cur.close()
    return

def df_inserts(con, df, table):
    cur = con.cursor()
    columns = len(df.columns)
    rows = len(df)
    for i in range(rows):
        cols = ', '.join(list(df.columns))
        vals = [df.at[i,col] for col in list(df.columns)]
        if table == "festival_area":
            query = "INSERT INTO %s(%s) VALUES(%s, ST_GeomFromText('%s', 4326));" % (
            table, cols, vals[0], vals[1])
            cur.execute(query)
            con.commit()
        elif table == "food_areas":
            query = "INSERT INTO %s(%s) VALUES(%s, %s, %s, '%s', ST_GeomFromText('%s', 4326));" % (table, cols, vals[0], vals[1], vals[2], vals[3], vals[4])
            cur.execute(query)
            con.commit()
        elif table == "food_stalls":
            query = "INSERT INTO %s(%s) VALUES(%s,'%s', ST_GeomFromText('%s', 4326), %s, %s);" % (table, cols, vals[0], vals[1], vals[2], vals[3], vals[4])
            cur.execute(query)
            con.commit()
        elif table == "events":
            query = "INSERT INTO %s(%s) VALUES(%s, %s, %s, %s);" % (table, cols, vals[0], vals[1], vals[2], vals[3])
            cur.execute(query)
            con.commit()
        elif table == "performers":
            query = "INSERT INTO %s(%s) VALUES(%s,'%s','%s');" % (table, cols, vals[0], vals[1], vals[2])
            cur.execute(query)
            con.commit()
        elif table == "stages":
            query = "INSERT INTO %s(%s) VALUES(%s, '%s', %s, %s, ST_GeomFromText('%s', 4326));" % (
            table, cols, vals[0], vals[1], vals[2], vals[3], vals[4])
            cur.execute(query)
            con.commit()
        elif table == "tent_zones":
            query = "INSERT INTO %s(%s) VALUES(%s, %s, ST_GeomFromText('%s', 4326));" % (table, cols, vals[0], vals[1], vals[2])
            cur.execute(query)
            con.commit()
        elif table == "tents":
            query = "INSERT INTO %s(%s) VALUES(%s, ST_GeomFromText('%s', 4326));" % (table, cols, vals[0], vals[1])
            cur.execute(query)
            con.commit()

def setup(con):
    """
    Creates the required tables in the database if they don't already exist.
    Checks if PostGIS extension is created.
    """
    # ---------------- POSTGIS EXTENSION ----------------
    try:
        cur = con.cursor()
        cur.execute('CREATE EXTENSION postgis;')
    except Exception as e:
            print(e)
    cur.close()

    # ---------------- CREATE TABLE STATEMENTS ----------------
    tables = {
        "festival_area": "CREATE TABLE IF NOT EXISTS festival_area (id serial NOT NULL PRIMARY KEY, geom GEOMETRY(MultiPolygon, 4326));",
        "food_stalls" : "CREATE TABLE IF NOT EXISTS food_stalls (id serial NOT NULL PRIMARY KEY, name varchar(30) NOT NULL, geom GEOMETRY(MultiPolygon, 4326), cur_staff integer NOT NULL, max_staff integer NOT NULL);",
        "food_areas" : "CREATE TABLE IF NOT EXISTS food_areas (id serial NOT NULL PRIMARY KEY, avg_count integer, cur_count integer, busy_label varchar(15), geom GEOMETRY(MultiPolygon, 4326));",
        "user_location" : "CREATE TABLE IF NOT EXISTS user_location (id serial NOT NULL, geom GEOMETRY(Point, 4326));",
        "performers" : "CREATE TABLE IF NOT EXISTS performers (id serial NOT NULL PRIMARY KEY, name varchar(30), genre varchar(20));",
        "stages" : "CREATE TABLE IF NOT EXISTS stages (id serial NOT NULL PRIMARY KEY, stage_name varchar(20), cur_staff integer, max_staff integer, geom GEOMETRY(Point, 4326));",
        "events" : "CREATE TABLE IF NOT EXISTS events (id serial NOT NULL PRIMARY KEY, day integer, stage_id integer references stages (id) NOT NULL, performer_id integer references performers (id) NOT NULL);",
        "tent_zones" : "CREATE TABLE IF NOT EXISTS tent_zones (id serial NOT NULL PRIMARY KEY, capacity integer, geom GEOMETRY(MultiPolygon, 4326));",
        "tents" : "CREATE TABLE IF NOT EXISTS tents (id serial NOT NULL PRIMARY KEY, geom GEOMETRY(Point, 4326));"
    }

    # Get True or False if table exists
    exist = {}
    for key in tables:
        exist[key] = check_exists(con, key)

    # Execute Create Statements
    for key in tables:
            if exist[key] == "('FALSE',)":
                # print(key, '->', tables[key])
                sql_in(con, tables[key])

    # ---------------- INSERT DATA INTO TABLES ----------------

    # Data was created either in QGIS (the data with a geom column) or in Excel (data without geom column)
    # and stored on GitHub. Pleae note: all data is made up
    links = [
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/festival_area.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/food_areas.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/food_stalls.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/performers.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/stages.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/events.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/tent_zones.csv",
        "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/tents.csv"
    ]

    dataframes = {}
    for link in links:
        head, tail = os.path.split(link)
        split = tail.split('.')
        name = str(split[0])
        df = pd.read_csv(link, header=0, index_col=None)
        # add new name and df to dictionary "dataframes"
        dataframes[name] = df

    # Insert data into database
    for key in dataframes:
        if exist[key] == "('FALSE',)":
            df_inserts(con, dataframes[key], key)

    return

def get_dataframe(link):
    result = pd.read_csv(link, header=0, index_col=None)
    return result

def welcome():
    print("\nWelcome to this little festival in Crete. \n__________________________________________\n")
    new = input("Are you new here? If so type yes or y. If not press any other key and hit enter.")
    print("\n__________________________________________\n")
    if new == "y" or new == "Y" or new == "yes" or new == "Yes":
        return "yes"
    else:
        return "no"

def intro():
    time.sleep(1)
    print("\nNice to have you here! First off, a quick introduction to the festival grounds.\nIn a few seconds a pop-up"
          "window will appear and show you an overview of the festival.")
    print("\n__________________________________________\n")
    time.sleep(3)

    festival_area = get_dataframe("https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/festival_area.csv")

    # create pop-up window
    popup = tk.Tk()
    # style elements
    s = ttk.Style()
    s.theme_use('classic')
    popup.geometry('800x600')
    popup.title('Crete Festival Overview')
    popup.eval('tk::PlaceWindow . center')

    # create map widget (code from https://github.com/TomSchimansky/TkinterMapView)
    map_widget = TkinterMapView(popup, width=800, height=600, corner_radius=0)
    map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # Set coordinate position
    map_widget.set_position(35.536128, 23.797889)
    map_widget.set_zoom(12)

    # Wait for the toplevel window to be closed
    # popup.wait_window()

    popup.mainloop()


def decide():
    user = input("Who is using this app?\n\n\t"
                 "1. Festival Staff\n\t"
                 "2. Festival Visitor\n\n"
                 "Please enter the appropriate number and hit enter.")
    print("\n__________________________________________\n")
    if user == "1" or user == "1.":
        task = input("What would you like to do right now?\n\n\t"
                     "---- FOOD ----\n\t"
                     "1. Find out if more members of staff are needed at any food stalls.\n\t"
                     "2. Update the number of staff members at a food stall.\n\t"
                     "3. Update the number of visitors in a food area.\n\n\t"
                     "---- EVENTS ----\n\t"
                     "4. Find out if more staff is needed at a stage for an event today.\n\t"
                     "5. Update the number of staff members at a stage.\n\n"
                     "Please enter the appropriate number and hit enter.")
        print("\n__________________________________________\n")
        return task
    elif user == "2" or user == "2.":
        task = input("What would you like to do right now?\n\n\t"
                     "---- FOOD ----\n\t"
                     "6. Find out which food areas are not busy.\n\t"
                     "7. Find the closest food area.\n\t"
                     "8. Find the closest not busy food area.\n\n\t"
                     "---- EVENTS ----\n\t"
                     "9. Find out which events are on today.\n\t"
                     "10. Find out when and where my favourite artist is playing.\n\t"
                     "11. Find out what events are happening near me today.\n\t"
                     "12. Find the closest stage.\n\n\t"
                     "---- TENTS ----\n\t"
                     "13. In which zone can I put my tent? I.e. where is still space?\n\t"
                     "14. How far am I from my tent?\n\n"
                     "Please enter the appropriate number and hit enter.")
        print("\n__________________________________________\n")
        return task
    else:
        print("The entered value wasn't recognised. Please try again.")
        sys.exit(0)


if __name__ == '__main__':

    # Connect to DB and set up tables and PostGIS
    con = connect("localhost", "festival", "postgres", "Peribff128!")
    setup(con)
    print("DB setup complete.")
    con.close()

    if welcome() == "yes":
        intro()

    task = decide()
    print(f"Task number: {str(task)}")



    """


    cur.execute(# "" #INSERT INTO testing_stuff (id, name) VALUES 
            #(%s, %s);"", (1, "Christina"))

    cur.execute('SELECT * FROM testing_stuff;')

    # Get all entries
    rows = cur.fetchall()
    # result will be tuples e.g. (id, name)
    for r in rows:
        print(f"id {r[0]} name {r[1]}")

    """
    # Close the connection to the db
