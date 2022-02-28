import sys
import psycopg2
import time
import tkinter as tk
from tkintermapview import TkinterMapView
import pandas as pd
import os
import locations


# ------------------------------------------------ DATA AND DB -------------------------------------------------------

def connect(host, database, user, password):
    """Connect to the db"""
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
    """Check if a table already exists. Returns TRUE or FALSE."""
    cur = con.cursor()
    query = f"SELECT CASE WHEN (EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'public' AND  TABLE_NAME = '{str(table)}')) THEN 'TRUE' ELSE 'FALSE' END;"
    try:
        cur.execute(query)
        result = cur.fetchone()
        exists = str(result)
    except (Exception, psycopg2.Error) as error:
        exists = "no"

    con.commit()
    cur.close()
    return exists


def sql_in(con, sql_statement):
    """Tries to execute a statement without any return in the database. Catches errors if something goes wrong. """
    cur = con.cursor()
    try:
        cur.execute(sql_statement)
        con.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing the statement {str(sql_statement)}.")
        print("Error: %s" % error)
    cur.close()
    return


def sql_return(con, sql_statement):
    """ Tries to execute a statement in the database with a return value. """
    cur = con.cursor()
    try:
        cur.execute(sql_statement)
        con.commit()
        result = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing the statement {str(sql_statement)}.")
        print("Error: %s" % error)
    cur.close()
    return result


def df_inserts(con, df, table):
    """Performs iterative insert statement into the databsae with given dataframes to set up the tables with existing data."""
    cur = con.cursor()
    columns = len(df.columns)
    rows = len(df)
    for i in range(rows):
        cols = ', '.join(list(df.columns))
        vals = [df.at[i, col] for col in list(df.columns)]
        if table == "festival_area":
            query = "INSERT INTO %s(%s) VALUES(%s, ST_GeomFromText('%s', 4326));" % (
                table, cols, vals[0], vals[1])
            cur.execute(query)
            con.commit()
        elif table == "food_areas":
            query = "INSERT INTO %s(%s) VALUES(%s, %s, %s, '%s', ST_GeomFromText('%s', 4326));" % (
            table, cols, vals[0], vals[1], vals[2], vals[3], vals[4])
            cur.execute(query)
            con.commit()
        elif table == "food_stalls":
            query = "INSERT INTO %s(%s) VALUES(%s,'%s', ST_GeomFromText('%s', 4326), %s, %s);" % (
            table, cols, vals[0], vals[1], vals[2], vals[3], vals[4])
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
            query = "INSERT INTO %s(%s) VALUES(%s, %s, ST_GeomFromText('%s', 4326));" % (
            table, cols, vals[0], vals[1], vals[2])
            cur.execute(query)
            con.commit()
        elif table == "tents":
            query = "INSERT INTO %s(%s) VALUES(%s, ST_GeomFromText('%s', 4326));" % (table, cols, vals[0], vals[1])
            cur.execute(query)
            con.commit()


def setup(con):
    """ Creates the required tables in the database if they don't already exist. Checks if PostGIS extension is created. Loads dataframes and inserts them via the df_inserts() function."""
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
        "food_stalls": "CREATE TABLE IF NOT EXISTS food_stalls (id serial NOT NULL PRIMARY KEY, name varchar(30) NOT NULL, geom GEOMETRY(MultiPolygon, 4326), cur_staff integer NOT NULL, max_staff integer NOT NULL);",
        "food_areas": "CREATE TABLE IF NOT EXISTS food_areas (id serial NOT NULL PRIMARY KEY, avg_count integer, cur_count integer, busy_label varchar(15), geom GEOMETRY(MultiPolygon, 4326));",
        "user_location": "CREATE TABLE IF NOT EXISTS user_location (id serial NOT NULL, geom GEOMETRY(Point, 4326));",
        "performers": "CREATE TABLE IF NOT EXISTS performers (id serial NOT NULL PRIMARY KEY, name varchar(30), genre varchar(20));",
        "stages": "CREATE TABLE IF NOT EXISTS stages (id serial NOT NULL PRIMARY KEY, stage_name varchar(20), cur_staff integer, max_staff integer, geom GEOMETRY(Point, 4326));",
        "events": "CREATE TABLE IF NOT EXISTS events (id serial NOT NULL PRIMARY KEY, day integer, stage_id integer references stages (id) NOT NULL, performer_id integer references performers (id) NOT NULL);",
        "tent_zones": "CREATE TABLE IF NOT EXISTS tent_zones (id serial NOT NULL PRIMARY KEY, capacity integer, geom GEOMETRY(MultiPolygon, 4326));",
        "tents": "CREATE TABLE IF NOT EXISTS tents (id serial NOT NULL PRIMARY KEY, geom GEOMETRY(Point, 4326));"
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
    """From link to online CSV to dataframe."""
    result = pd.read_csv(link, header=0, index_col=None)
    return result


def perform_task(con, task):
    """ Handles the chosen task logic. """

    cur = con.cursor()

    # Set default map to false -> don't load map in the end.
    map = False
    args = {}

    if task == "1" or task == "1.":
        # Find out if more members of staff are needed at any food stalls
        # Average -> keep an eye out
        not_max_staff_average_busy = "SELECT name, max_staff - cur_staff FROM food_stalls WHERE id IN (SELECT id FROM food_stalls WHERE cur_staff < max_staff) AND id IN (SELECT s.id FROM food_stalls AS s, (SELECT geom FROM food_areas WHERE busy_label = 'average') AS a WHERE ST_Intersects(s.geom, a.geom));"
        cur.execute(not_max_staff_average_busy)
        average = cur.fetchall()
        print("\nKeep An Eye On stalls that are averagely busy but whose team is not at full capactiy:\n")
        for stall in average:
            print(f"- {str(stall[0])}: Send {str(stall[1])} more staff to reach maximum staffing.")
        # busy -> send more staff
        not_max_staff_high_busy = "SELECT name, max_staff - cur_staff FROM food_stalls WHERE id IN (SELECT id FROM food_stalls WHERE cur_staff < max_staff) AND id IN (SELECT s.id FROM food_stalls AS s, (SELECT geom FROM food_areas WHERE busy_label = 'high') AS a WHERE ST_Intersects(s.geom, a.geom));"
        cur.execute(not_max_staff_high_busy)
        busy = cur.fetchall()
        print("\nMore Staff are definitely needed: \n(Thesee stalls are very busy right now and their team is not at full capacity)\n")
        for stall in busy:
            print(f"- {str(stall[0])}: {str(stall[1])} more staff to reach maximum staffing.")
            args[str(stall[0])] = f"{str(stall[0])}: {str(stall[1])} more staff"
        print("\n")
        map = True

    if task == "2" or task == "2.":
        # Update the number of staff members at a food stall
        print("Food Stalls: \n")
        cur.execute("SELECT id, name, cur_staff FROM food_stalls ORDER BY id ASC;")
        stalls = cur.fetchall()
        print("ID | Stall Name | Current Staff")
        for row in stalls:
            print(f"{str(row[0])} | {str(row[1])} | {str(row[2])}")
        id = input(
            "\nFor which food stall do you want to update the numbers of staff? Enter the relevant id and hit enter.")
        cur.execute("SELECT name, cur_staff, max_staff FROM food_stalls WHERE id = %s;" % (id))
        name = cur.fetchone()
        new_count = input(f"\n{str(name[0])} currently has {str(name[1])} staff members. The maximum is {str(name[2])}. What is the new staff count: ")
        sql_in(con, "UPDATE food_stalls SET cur_staff = %s WHERE id = %s;" % (new_count, id))
        args[str(name[0])] = f"{str(name[0])} staff: {str(new_count)}"
        map = True

    if task == "3" or task == "3.":
        # Update the number of visitors in a food area.
        print("Food Areas: \n")
        cur.execute("SELECT id, cur_count, avg_count, busy_label FROM food_areas ORDER BY id ASC;")
        stalls = cur.fetchall()
        print("Area ID | Current Visitors | Average Nr of Visitors | Label")
        for row in stalls:
            print(f"{str(row[0])} | {str(row[1])} | {str(row[2])} | {str(row[3])}")
        id = input(
            "\nFor which area do you want to update the visitors? Enter the relevant id and hit enter.")
        new_count = input(f"\nNew visitor count for area {str(id)}: ")
        sql_in(con, "UPDATE food_areas SET cur_count = %s WHERE id = %s;" % (new_count, id))
        sql_in(con,
               "UPDATE food_areas SET busy_label = CASE WHEN cur_count - avg_count > 5 THEN 'high' WHEN avg_count - cur_count > 5 THEN 'low' ELSE 'average' END WHERE id = %s;" % id)
        cur.execute("SELECT busy_label FROM food_areas WHERE id = %s;" % id)
        new_label = cur.fetchone()
        print(f"\nUpdate has been completed. The new label for the area is {str(new_label[0])}.")

    if task == "4" or task == "4.":
        # Find out if more staff is needed at a stage for an event today
        day = input("\nWhich day of the festival is it today? Days range from 1 - 4. Enter the day number and hit enter.")
        cur.execute("SELECT events.id, performers.name, stages.stage_name, stages.max_staff - stages.cur_staff, stages.max_staff FROM events INNER JOIN performers ON performers.id = events.performer_id INNER JOIN stages ON stages.id = events.stage_id WHERE day = %s AND stages.max_staff - stages.cur_staff > 0;" % day)
        result = cur.fetchall()
        print("\nThese events are on today, which need more staff!\n\nEvent ID | Performer | Stage | Nr of Staff Needed | Current Staff")
        for row in result:
            print(f"{str(row[0])} | {str(row[1])} | {str(row[2])} | {str(row[3])} | {str(row[4])}")
            args[str(row[2])] = f"{str(row[2])}. {str(row[1])} on today. \nSend {str(row[3])} more staff."
        map = True

    if task == "5" or task == "5.":
        # Update the number of staff members at a stage.
        cur.execute("SELECT id, stage_name, cur_staff, max_staff FROM stages ORDER BY id ASC;")
        stages = cur.fetchall()
        print("\nID | Stage Name | Current Staff | Maximum Staff")
        for row in stages:
            print(f"{str(row[0])} | {str(row[1])} | {str(row[2])} | {str(row[3])}")
        id = input("\nFor which stage do you want to update the staff? Please enter the id.")
        staff = input("What is the new staff count?")
        sql_in(con, "UPDATE stages SET cur_staff = %s WHERE id = %s;" % (staff, id))
        cur.execute("SELECT stage_name FROM stages WHERE id = %s;" % id)
        name = cur.fetchone()
        args[str(name[0])] = f"{str(name[0])} staff: {str(staff)}"
        map = True
        #  args = {"festival_area" : "festival_area", "main_stage": "101"}

    if task == "6" or task == "6.":
        # Find out which food areas are not busy
        cur.execute("SELECT name FROM food_stalls WHERE id IN (SELECT s.id FROM food_stalls AS s, (SELECT geom FROM food_areas WHERE busy_label = 'low') AS a WHERE ST_Intersects(s.geom, a.geom));")
        result = cur.fetchall()
        print("\nThese food stall are available in areas that are currently not busy.")
        for row in result:
            print(f"{str(row[0])}")
            args[str(row[0])] = f"{str(row[0])}"
        map = True

    if task == "7" or task == "7.":
        # Find the closest food stall
        cur.execute("SELECT name, (ST_Distance(s.geom::geography, u.geom::geography)::integer) AS distance FROM food_stalls AS s, user_location AS u ORDER BY distance ASC LIMIT 1;")
        result = cur.fetchone()
        args["user"] = "Your Position"
        args["Festival Area"] = " "
        args["path"] = str(result[0])
        print(f"\nThe nearest food stall is {str(result[0])}. It's {str(result[1])} meters away from you.\n")
        args[str(result[0])] = f"{str(result[0])} - {str(result[1])} meters away"
        map = True

    if task == "8" or task == "8.":
        # Find the closest not busy food stall.
        cur.execute("SELECT s.name, (ST_Distance(s.geom::geography, u.geom::geography)::integer) AS distance FROM food_stalls AS s, user_location as u WHERE s.id IN (SELECT a.id FROM food_stalls AS a, food_areas AS b WHERE ST_Intersects(a.geom, b.geom) AND b.busy_label = 'low') ORDER BY distance ASC LIMIT 1;")
        result = cur.fetchone()
        print(f"\nThe nearest food stall which isn't busy is {str(result[0])}. It's {str(result[1])} meters away from you.\n")
        args["user"] = "Your Position"
        args["Festival Area"] = " "
        args["path"] = str(result[0])
        args[str(result[0])] = f"{str(result[0])} - {str(result[1])} meters away"
        map = True

    if task == "9" or task == "9.":
        # Find out which events are on today
        day = input("\nWhich day of the festival is it today? Days range from 1 - 4. Enter the day number and hit enter.")
        cur.execute("SELECT events.id, performers.name, stages.stage_name FROM events INNER JOIN performers ON performers.id = events.performer_id INNER JOIN stages ON stages.id = events.stage_id WHERE day = %s;" % day)
        result = cur.fetchall()
        print("\nEvents on Today:")
        print("\nEvent ID | Performer | Stage ")
        for row in result:
            print(f"{str(row[0])} | {str(row[1])} | {str(row[2])}")
            args[str(row[2])] = f"{str(row[2])}: {str(row[1])}"
        args["Festival Area"] = " "
        map = True

    if task == "10" or task == "10.":
        # Find out when and where my favourite artist is playing
        cur.execute("SELECT id, name, genre FROM performers ORDER BY id ASC;")
        perf = cur.fetchall()
        print("\nID | Performer | Genre")
        for act in perf:
            print(f"{str(act[0])} | {str(act[1])} | {str(act[2])}")
        id = input("\nWhich artist do you want to inquire about? Please enter their id: ")
        cur.execute("SELECT events.day, stages.stage_name, performers.name FROM events INNER JOIN performers ON performers.id = events.performer_id INNER JOIN stages ON stages.id = events.stage_id WHERE performers.id = %s;" % id)
        result = cur.fetchone()
        print(f"\nYour favourite artist {str(result[2])} is playing on day {str(result[0])} on the {str(result[1])}! Enjoy the show!")
        args[str(result[1])] = f"{str(result[2])}: Day {str(result[0])}"
        args["Festival Area"] = " "
        map = True

    #if task == "11" or task == "11.":
        # Find out what events are happening near me today.
        # day = input("\nWhich day of the festival is it today? Days range from 1 - 4. Enter the day number and hit enter.")

    if task == "12" or task == "12.":
        # Find the closest stage
        cur.execute("SELECT s.stage_name, (ST_Distance(s.geom::geography, u.geom::geography)::integer) AS distance FROM stages AS s, user_location AS u ORDER BY distance ASC LIMIT 1;")
        result = cur.fetchone()
        print(f"\nThis is the closest stages to you: {str(result[0])}. It's {str(result[1])} meters away.")
        args["path"] = str(result[0])
        args[str(result[0])] = f"{str(result[1])} meters away"
        args["Festival Area"] = " "
        args["user"] = "Your Position"
        map = True




    cur.close()

    return map, args

    """
        if task == "13" or task == "13.":
        if task == "14" or task == "14.":
    """


# ============================================= USER INTERACTION ======================================================

def map(userY, userX, show):
    """ Opens map at the end showing stuff. """
    print("\n__________________________________________\n")
    time.sleep(1)

    # create pop-up window
    popup = tk.Tk()
    popup.geometry('1000x600')
    popup.title('Crete Festival Overview')
    popup.eval('tk::PlaceWindow . center')

    # create map widget (code from https://github.com/TomSchimansky/TkinterMapView)
    map_widget = TkinterMapView(popup, width=1000, height=600, corner_radius=0)
    map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # Set coordinate position
    map_widget.set_position(35.495567, 23.682282)
    map_widget.set_zoom(15)

    for key in show:
        for place in locations.places:
            if key == place:
                map_widget.set_marker(locations.places[place][0], locations.places[place][1], text=f"{str(show[key])}", text_color="black",
                                        marker_color_circle="grey50", marker_color_outside="grey60",
                                        font=("Calibri Light", 14))
            elif key == "Festival Area":
                map_widget.set_path([(35.49837698770717509, 23.66898440416236582),
                                     (35.50029819558625377, 23.68607719148529966),
                                     (35.49878575918922508, 23.686514732411311),
                                     (35.49754191950018622, 23.68789191040795217),
                                     (35.49371684579321595, 23.68850877138562439),
                                     (35.49258388824107868, 23.68863788182280672),
                                     (35.48907979470185836, 23.67975795286528395),
                                     (35.48888122482639318, 23.6754686172299067),
                                     (35.49034128597957505, 23.66958691953589877),
                                     (35.49249044772982842, 23.6688696393293192),
                                     (35.49475634949335046, 23.66861141845495098),
                                     (35.49837698770717509, 23.66898440416236582),
                                     (35.49837698770717509, 23.66898440416236582)])
            elif key == "path":
                map_widget.set_path([(userY, userX), locations.places[show[key]]])
            elif key == "user":
                map_widget.set_marker(userY, userX, text=f"{str(show[key])}", text_color="darkred",
                                      marker_color_circle="red", marker_color_outside="darkred",
                                      font=("Calibri Light", 14))

    def on_closing():
        popup.quit()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", on_closing)
    popup.mainloop()
    return


def decide():
    print("\nWelcome to this little festival in Crete. \n__________________________________________\n")
    user = input("Who is using this app?\n\n\t"
                 "1. Festival Staff\n\t"
                 "2. Festival Visitor\n\n"
                 "Please enter the appropriate number and hit enter: ")
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
                     "Please enter the appropriate number and hit enter: ")
        print("\n__________________________________________\n")
    elif user == "2" or user == "2.":
        task = input("What would you like to do right now?\n\n\t"
                     "---- FOOD ----\n\t"
                     "6. Find out which food areas are not busy.\n\t"
                     "7. Find the closest food stall.\n\t"
                     "8. Find the closest not busy food stall.\n\n\t"
                     "---- EVENTS ----\n\t"
                     "9. Find out which events are on today.\n\t"
                     "10. Find out when and where my favourite artist is playing.\n\t"
                     "11. Find out what events are happening near me today.\n\t"
                     "12. Find the closest stage.\n\n\t"
                     "---- TENTS ----\n\t"
                     "13. In which zone can I put my tent? I.e. where is still space?\n\t"
                     "14. How far am I from my tent?\n\n"
                     "Please enter the appropriate number and hit enter: ")
        print("\n__________________________________________\n")
    else:
        print("The entered value wasn't recognised. Please try again.")
        sys.exit(0)

    if task == "7" or task == "7." or task == "8" or task == "8." or task == "11" or task == "11." or task == "12" or task == "12." or task == "14" or task == "14.":
        print("For this task you need to provide your position.\n\n"
              "Here are some example positions within the festival area:\n\t"
              "A) 35.489809, 23.675539\n\t"
              "B) 35.499055, 23.685873\n\t"
              "C) 35.495038, 23.670254\n\n")
        print(
            "If you want to simply use one of those, then enter the letter A, B, or C. Otherwise first enter your Latitude position, hit enter, and then your Longitude position.\n")
        user_pos = input("Your position (letter from examples or latitude in format 35.495649): ")
        if user_pos.upper() == "A" or user_pos == "A)":
            userY = 35.489809
            userX = 23.675539
        elif user_pos.upper() == "B" or user_pos == "B)":
            userY = 35.499055
            userX = 23.685873
        elif user_pos.upper() == "C" or user_pos == "C)":
            userY = 35.495038
            userX = 23.670254
        else:
            userY = float(user_pos)
            userX = float(input("Your position (longitude in format 23.673355): "))
    else:
        userY = 0
        userX = 0

    return userY, userX, task
