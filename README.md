# Setup 

Because no endpoints were given the calls are via a mysql mcp server that can run SELECT queries on the database.

Framework in use is [Google ADK](https://google.github.io/adk-docs/)
* Built in FastAPI server (instructions below on how to run the server, [view FAST API docs at localhost:8000/docs])
* Built In web interface

 
 `pip install -r requirements.txt`

 ### To setup with local db 
 
 ps: you will need to make a connection with a MySQL db

`docker pull mysql` 

`docker exec -it mysql-server mysql -u root -p` 

`docker cp file.sql mysql-server` 

 #### In mysql run 

`CREATE tfg;` 
`USE tfg;`
`SOURCE file.sql;`

This is the creation of the example database that queries will be executed against

 ### To run agent:

 `adk web` - run with web interface
 `adk run` -  run with CLI
 `adk api_server` - run FastAPI server

 






