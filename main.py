# if not installed: pip install psycopg2
import sys
import psycopg2
import time
import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd

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

    print("df_inserts() done")


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

    # ---------------- CREATE TABLES ----------------
    festival_area = "CREATE TABLE IF NOT EXISTS festival_area (id serial NOT NULL PRIMARY KEY, geom GEOMETRY(MultiPolygon, 4326));"
    food_stalls = "CREATE TABLE IF NOT EXISTS food_stalls (id serial NOT NULL PRIMARY KEY, name varchar(30) NOT NULL, geom GEOMETRY(MultiPolygon, 4326), cur_staff integer NOT NULL, max_staff integer NOT NULL);"
    food_areas = "CREATE TABLE IF NOT EXISTS food_areas (id serial NOT NULL PRIMARY KEY, avg_count integer, cur_count integer, busy_label varchar(15), geom GEOMETRY(MultiPolygon, 4326));"
    user_location = "CREATE TABLE IF NOT EXISTS user_location (id serial NOT NULL, geom GEOMETRY(Point, 4326));"
    performers = "CREATE TABLE IF NOT EXISTS performers (id serial NOT NULL PRIMARY KEY, name varchar(30), genre varchar(20));"
    stages = "CREATE TABLE IF NOT EXISTS stages (id serial NOT NULL PRIMARY KEY, stage_name varchar(20), cur_staff integer, max_staff integer, geom GEOMETRY(Point, 4326));"
    events = "CREATE TABLE IF NOT EXISTS events (id serial NOT NULL PRIMARY KEY, day integer, stage_id integer references stages (id) NOT NULL, performer_id integer references performers (id) NOT NULL);"
    tent_zones = "CREATE TABLE IF NOT EXISTS tent_zones (id serial NOT NULL PRIMARY KEY, capacity integer, geom GEOMETRY(MultiPolygon, 4326));"
    tents = "CREATE TABLE IF NOT EXISTS tents (id serial NOT NULL PRIMARY KEY, geom GEOMETRY(Point, 4326));"

    sql_in(con, festival_area)
    sql_in(con, food_stalls)
    sql_in(con, food_areas)
    sql_in(con, user_location)
    sql_in(con, performers)
    sql_in(con, stages)
    sql_in(con, events)
    sql_in(con, tent_zones)
    sql_in(con, tents)

    # ---------------- INSERT DATA INTO TABLES ----------------

    # Data was created either in QGIS (the data with a geom column) or in Excel (data without geom column)
    # and stored on GitHub. Pleae note: all data is made up
    festival_area_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/festival_area.csv"
    food_areas_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/food_areas.csv"
    food_stalls_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/food_stalls.csv"
    events_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/events.csv"
    performers_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/performers.csv"
    stages_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/stages.csv"
    tent_zones_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/tent_zones.csv"
    tents_link = "https://raw.githubusercontent.com/Christina1281995/spatial_db_finalproject/main/data/tents.csv"

    festival_area_df = pd.read_csv(festival_area_link, header=0, index_col=None)
    food_areas_df = pd.read_csv(food_areas_link, header=0, index_col=None)
    food_stalls_df = pd.read_csv(food_stalls_link, header=0, index_col=None)
    events_df = pd.read_csv(events_link, header=0, index_col=None)
    performers_df = pd.read_csv(performers_link, header=0, index_col=None)
    stages_df = pd.read_csv(stages_link, header=0, index_col=None)
    tent_zones_df = pd.read_csv(tent_zones_link, header=0, index_col=None)
    tents_df = pd.read_csv(tents_link, header=0, index_col=None)

    df_inserts(con, festival_area_df, "festival_area")
    df_inserts(con, food_areas_df, "food_areas")
    df_inserts(con, food_stalls_df, "food_stalls")
    df_inserts(con, stages_df, "stages")
    df_inserts(con, performers_df, "performers")
    df_inserts(con, events_df, "events")
    df_inserts(con, tent_zones_df, "tent_zones")
    df_inserts(con, tents_df, "tents")

    return

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
    print("\nNice to have you here! First off, a quick introduction to the festival grounds.")
    print("\n__________________________________________\n")

    # create pop-up window
    popup = tk.Tk()
    # style elements
    s = ttk.Style()
    s.theme_use('classic')
    popup.geometry('400x150')
    popup.title('Crete Festival Overview')
    popup.eval('tk::PlaceWindow . center')

    # pop up window content
    L1 = tk.Label(popup, text="Username:", font=(14)).grid(row=0, column=0, padx=15, pady=15)
    L2 = tk.Label(popup, text="Password:", font=(14)).grid(row=1, column=0, padx=5, pady=5)

    popup.mainloop()


def decide():
    user = input("Who is using this app?\n\n\t1. Festival Staff\n\t2. Festival Visitor\n\nPlease enter the appropriate number and hit enter.")
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
