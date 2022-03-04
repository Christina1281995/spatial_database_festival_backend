![image](https://user-images.githubusercontent.com/81073205/156821923-c4a8fb6d-865e-4b39-a24d-debdafb7e53e.png)

# A Spatial Database as the Backend for a Festival App

### Context

The initial motivation for this project was the final project of a 'Spatial Databses' course at the University of Salzburg. The aim is to create a spatial database that can serve as the backend to a festival, specifically it should:
- Serve as database backend to organise the booths, roller coasters, tents etc.
(Positions, opening times, ...) as well as other facilities (garbage bins, toilets
etc)
- User-specific, dynamic queries that return which events take place or facilities
that are close to the current visitor’s position.
- User-specific and dynamic queries about the festival (digital maps, lists of
events etc


### Psycopg2

To create dynamic queries into a spatial database, there must be some form of user interaction. At the outset of this project I had no previous experience with any other postgres interaction points other than PG admin and QGIS. Both of those are direct communication channels with the database, where SQL statements are directly entered. In order **to mediate, narrate, control and guide a user around the data that is in such a spatial database, there must be an additional step in between the database (or PG admin) and the user**. The user should not need to worry about the queries and data flow to and from the database. Likewise, there should be minimal risk of the user damaging the data or inserting erroneous data. For all of those reasons, I searched the internet for an adequate "in-between" tool, and found [psycopg2](https://pypi.org/project/psycopg2/). It is the main database connector for the python language. By making use of it, I was able to work with both the user and the data. The finished programme consists of 3 python files: 
1. The "main.py" file which only contains the execution logic for the programme. It calls the relevant functions. 
2. The "functions.py" file contains all the functionalities needed to set up the database and execute the queries according to the user input. It also includes the function for a [tkinter](https://docs.python.org/3/library/tkinter.html) pop-up window with a map showing some relevant spatial information of the query.
3. The "locations.py" file containing some spatial information in the format that tkinter requires it for the map (which is a very different format than the geom datatypes available with postgres). If the geometry could have been converted from the database tables' geom columns I would rather have done that, but I couldn't quite work out how to reformat it so much in an automated way.
All three code files are saved [here](https://github.com/Christina1281995/spatial_db_finalproject/tree/main/src) in the GitHub repository.

### Data Model

A first concept for the database was created through simple brainstorming on the topic of "what would be a good use for an app during a festival?" and "what would I use an app for at a festival?". Based on those notes, a few key entities were identified: tents, tent areas, stages, performers, events, food stalls, food areas. With those entities in mind a set of concrete questions was developed which queries into the database should answer. With those entities and the questions / plain-text queries in mind, a data model was sketched (see image below). This data model is intentionally kept simple. It is **only as complex as it needs to be for the intended queries. As such, it is "fit for purpose"**. The decisions for the cardinalities are, of course, debatable. They were determined by my own decision: e.g. that a performer only belongs to one stage and one event. 

<br>

![image](https://user-images.githubusercontent.com/81073205/156799213-5a0aaa30-6485-4a47-983b-4ea02b493b05.png)



<!-- ![Spatial Databases FinPro](https://user-images.githubusercontent.com/81073205/156794208-011a611f-f3fd-44e6-9709-86fbb86c5280.png) -->

### Setting up the Database, the Tables, and the Data

The only set conducted in PG admin was to create a database with the name "festival". The remainder of the set up is implemented with psychopg2. A set of functions is executed to connect with the database, check for the existence of a PostGIS extension and the database tables. Then, both are added and the tables are filled with data taken from CSV files stored online in this GitHub repository. Since the list of functions is quite long, it is placed at the bottom of this README page. Please refer to it for details on the functions. 


### User Interaction

Although not required, a central element for this project is the user interaction. In the following section I detail the logic of the available queries.
The tables below show the different interactions available to the user. Please note that the user's input is represented in the queries through the "%s" symbol. In later stages of this project, the SQL commands were re-written into preprared statements as plans. The queries shown here still display the structure of the queries.

**Decision 1 - "Who is using this app?"**

| Option | Value | 
| :-------------: | :------------- |
| 1 | Festival Staff |
| 2 | Festival Visitor |

**Decision 2 - FOR STAFF: "What would you like to do right now?"**

| Option | Value | Query |
| :-------------: | ------------- | ---------- |
| 1 | Find out if more members of staff are needed at any food stalls | ![image](https://user-images.githubusercontent.com/81073205/156790666-31cb3ccb-bdb7-4e8c-8efb-ea9023b6bf16.png) |
| 2 | Update the number of staff members at a food stall | ![image-removebg-preview (1)](https://user-images.githubusercontent.com/81073205/156790743-16948c6a-3698-4db2-a37b-bb01e9e6d557.png) |
| 3 | Update the number of visitors in a food area | ![image](https://user-images.githubusercontent.com/81073205/156790595-e7688883-ebab-4599-bfb1-52ea054f676f.png) |
| 4 | Find out if more staff is needed at a stage for an event today | ![image-removebg-preview](https://user-images.githubusercontent.com/81073205/156790539-3f17d5a9-9db5-4001-a34f-f262b2845c6b.png) | 
| 5 | Update the number of staff members at a stage | ![image](https://user-images.githubusercontent.com/81073205/156790300-18de63ea-d46e-4c69-b0ec-5363a1c698a2.png) |

**Decision 2 - FOR VISITORS: "What would you like to do right now?"**

| Option | Value | Query |
| :-------------: | ------------- | ------------- |
| 6 | Find out which food areas are not busy | ![image](https://user-images.githubusercontent.com/81073205/156789804-cfe19241-db67-43a4-91d9-8cdc44956428.png) |
| 7 | Find the closest food stall | ![156789949-3e7d88b3-f4c4-426f-b298-5c345c2eed4e-removebg-preview](https://user-images.githubusercontent.com/81073205/156790194-65ca6522-febd-40ef-abfd-3149e3a08fbd.png) |
| 8 | Find the closest not busy food stall |  ![image](https://user-images.githubusercontent.com/81073205/156789624-63e4d1cd-a7f4-4f35-a3de-ad6f1fd5737e.png) |
| 9 | Find out which events are on today | ![image-removebg-preview (2)](https://user-images.githubusercontent.com/81073205/156790940-79270d08-5500-4bf4-b985-6a109b597cd5.png) |
| 10 | Find out when and where my favourite artist is playing | ![image](https://user-images.githubusercontent.com/81073205/156790998-e50b20b3-538c-49f4-9ca0-b922d0c19df5.png) |
| 11 | Find out what events are happening near me today |  |
| 12 | Find the closest stage | ![image](https://user-images.githubusercontent.com/81073205/156791104-3ba5b23d-0a61-418c-a994-29954b61231a.png) |
| 13 | In which zone can I put my tent? I.e. where is still space? | ![image-removebg-preview (3)](https://user-images.githubusercontent.com/81073205/156791211-c562a96e-3180-4b4d-baaa-1a9cbf869890.png) |
| 14 | How far am I from my tent? | ![image](https://user-images.githubusercontent.com/81073205/156791248-58f4f706-735b-45df-883f-a6dfa8342e1f.png) |





### Map

The tkinter map pop-up window is a very simple spatial visualisation of the query. Here are some examples:

An output of task 12 ("Find the closest stage"):

<img src="https://user-images.githubusercontent.com/81073205/156769144-5f461047-2312-4183-9e23-0a441d805b92.png" width="75%">

An output of task 1 ("Find out if more staff are needed at any food stalls"):

<img src="https://user-images.githubusercontent.com/81073205/156769713-edbec7bc-5a10-4547-9bdb-fbe51dd9a05c.png" width="75%">

Again an output of task 1, but after executing task 2 to upate the current staff of "Brunch Bites":

<img src="https://user-images.githubusercontent.com/81073205/156772000-d8d6d92c-0f86-43df-a5e7-8f21dad1e2ca.png" width="75%">


## Functions

| Function | Purpose | Returns |
| ------------- | ------------- | ------------ |
| def **connect**(host, database, user, password) | Establishes the connection to the database via psycopg2  | **con** - a psycopg2 connection |
| def **check_exists**(con, table)  | Checks for exisitng tables in the database.  | **exists** - the database's boolean return value from the query (TRUE or FALSE) |
| def **sql_in**(con, sql_statement) | Inserts a statement into a given table. | / |
| def **sql_return**(con, sql_statement) | Queries a return value from the database. | **result** - the database's return values |
| def **df_inserts**(con, df, table) | Used to insert the existing data into the database tables in the beginning. It iteratively inserts data from a github CSV into the a specified table. | / |
| def **setup**(con) | Connects to database, checks for PostGIS extension (otherwise creates one), uses the above function "check_exists" to see if tables already exist and if not it creates them with the "df_inserts". | / |
| def **get_dataframe**(link) | A simple function to get a pandas dataframe from an online CSV. | **result** - a pandas dataframe |
| def **preprare_plans**(con) | A function that is called once before the user chooses which task to perform to set up the execution plans in the database. | / |
| def **perform_task**(con, task) | A pretty lengthy function that handles each task number entered by the user. It calls the different execution plans in the database and performs simple interaction with the user, while checking for valid inputs. | **map** - a boolean value to indicate whether or not a map should be loaded at the end, **args** - arguments for the map, e.g. which item to show |
| def **map**(userY, userX, show) | Creates a pop up map via tkinter and loads markers or paths into the map according to the arguments (="shows") and the user's position. This function is only called if the boolean variable "map" is set to True. | / |
| def **decide**() | User interaction logic to find out what task the user wants to do. This function also asks for the user's location if the chosen task requires it. If none is required the user's position is set to 0,0. | **userX** - user's x position, **userY** - user's y position, **task** - the chosen task number |




