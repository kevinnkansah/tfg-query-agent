# Setup 

Because no endpoints were given the calls are via a mysql mcp server that can run SELECT queries on the database.

Framework in use is [Google ADK](https://google.github.io/adk-docs/)
* Built in FastAPI server (instructions below on how to run the server, [view FAST API docs at localhost:8000/docs])
* Built In web interface

 
 `pip install -r requirements.txt`

 ### To setup with local db 
 
 ps: you will need to make a connection with a MySQL db

`docker pull mysql` 

`docker run --name mysql-server -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -d mysql`

`docker exec -it mysql-server mysql -u root -p` 

`docker cp sql/file.sql mysql-server:/file.sql` 

 #### In mysql run 

1. `CREATE tfg;` 
2. `USE tfg;`
3. `SOURCE file.sql;`

This is the creation of the example database that queries will be executed against

 ### To run agent:

 1. `adk web` - run with web interface
 2. `adk run` -  run with CLI
 3. `adk api_server` - run FastAPI server








