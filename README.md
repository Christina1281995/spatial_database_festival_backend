# Spatial Databases Final Project


... in progress ...



## User Interaction: 

**"Who is using this app?"**

| Option | Value | 
| :-------------: | :------------- |
| 1 | Festival Staff |
| 2 | Festival Visitor |

**FOR STAFF: "What would you like to do right now?"**

| Option | Value | Query |
| :-------------: | ------------- | ---------- |
| 1 | Find out if more members of staff are needed at any food stalls | ![image](https://user-images.githubusercontent.com/81073205/156786917-9d80358b-10ae-4441-95c9-f4d295f775a5.png) |
| 2 | Update the number of staff members at a food stall | ![image](https://user-images.githubusercontent.com/81073205/156787275-0b099a06-4e8a-423c-b079-3b9d23c82891.png) |
| 3 | Update the number of visitors in a food area | ![image](https://user-images.githubusercontent.com/81073205/156787480-0e7ee53b-a897-41b3-868e-ff87d4f87b07.png) |
| 4 | Find out if more staff is needed at a stage for an event today | ![image](https://user-images.githubusercontent.com/81073205/156787952-d15bdc78-06c9-4071-9cc8-9fe7f0fc0b71.png) | 
| 5 | Update the number of staff members at a stage | ![image](https://user-images.githubusercontent.com/81073205/156788422-335777ec-9f33-47fc-a041-9eb4f291db27.png) |

**FOR VISITORS: "What would you like to do right now?"**

| Option | Value | Query |
| :-------------: | ------------- | ------------- |
| 6 | Find out which food areas are not busy |  |
| 7 | Find the closest food stall | |
| 8 | Find the closest not busy food stall |   |
| 9 | Find out which events are on today |  |
| 10 | Find out when and where my favourite artist is playing |  |
| 11 | Find out what events are happening near me today |  |
| 12 | Find the closest stage |  |
| 13 | In which zone can I put my tent? I.e. where is still space? |  |
| 14 | How far am I from my tent? |  |




![tasks](https://user-images.githubusercontent.com/81073205/156784541-4299532d-17b7-4666-b135-bdecc873e146.png)

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




