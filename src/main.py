import time
import functions

if __name__ == '__main__':

    # Get connection parameters
    host, database, user, password = functions.connection_params()

    # Connect to database via psycopg2
    con = functions.connect(host, database, user, password)

    # Set up database (PostGIS extension, tables, data, prepare plans)
    functions.setup(con)

    # Chill for a second
    time.sleep(1)

    # Guide user through decision process -> return task number and user position if required
    userY, userX, task = functions.decide()

    # Update user's position in the database
    functions.update_position(userY, userX, con)

    # Perform queries, updates, etc. according the given task number and with all necessary user input
    show_map, args = functions.perform_task(con, task)

    # Close the connection to the database
    con.close()

    print("\nTask complete. See you next time!")

    # Lastly, if map is set to True show the user a map with the given arguments
    if show_map:
        time.sleep(2)
        functions.show_map(userY, userX, args)
