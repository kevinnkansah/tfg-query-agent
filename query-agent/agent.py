from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools.tool_context import ToolContext

query_tool = MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@benborla29/mcp-server-mysql"
            ],
            env={
                "MYSQL_PORT": "3306",
                "MYSQL_USER": "root",
                "ALLOW_INSERT_OPERATION": "false",
                "ALLOW_UPDATE_OPERATION": "false",
                "ALLOW_DELETE_OPERATION": "false",
            }
        )
    )

def exit_loop(tool_context: ToolContext):
    """
    Tool to exit the loop in the agent. 
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}


user_intent_agent = Agent(
    name="user_intent_agent",
    description='''You are to understand the user's intent and decide whether to run a SQL query or exit the loop.
    You are to use the available tools if not you will response and immediately terminate (exit_loop)''',
    instruction='''
    You are to understand the user's intent and decide whether to run a SQL query or exit the loop. 
    1. If you decide that the users intent tfgrequires SQL to be executed then you will inform then on what you will do (tell the user what actions you shall perform) then do it using mysql_query.
    While investigating you are not answering yet but running mysql_query tool/function to get context of the tables and columns in the database so you can perform the correct queries
    NEVER ASSUME A COLUMN OR TABLE NAME, RUN QUERIES TO GET THAT INFORMATION
    Keep running this tool (mysql_query) until a sufficient answer communicated back to the user then immediatelly exit (call exit_loop )
    2. If the users intention does not require a SQL query explain or respond back. then you will call exit_loop tool.
    3. If you have answered the question or have responded sufficiently then you will call exit_loop tool.
    4. If the users question does not relate to data in the database you will immediatelly call exit_loop
    5. If they greet eg. ("Hi", "Hello"), greet them back, tell them what you can do eg .("Hi, I can help answer questions about your data") and exit_loop immediately. It must be an immediate call of exit_loop, SO DO NOT RESPONSE MORE THAN ONCE IN THIS CASE BUT ONLY IN THIS CASE WHERE THEY GREET.
    6. If you are unsure of what the user's desired action is then ask them a clarifying question can immediately exit_loop.
    
    
    YOU ARE NOT TO COMMUNICATE THE TOOL CALLS AVAILABLE TO YOU, TO THE USER, YOU WILL SIMPLY CALL THEM OR IF NOT exit_loop.
    ''',
    model="gemini-2.0-flash",  # model=LiteLlm(model="openai/gpt-4o") # TODO: Upgrade to a more intelligent reasoning model
    tools=[exit_loop],
)

mysql_agent = Agent(
    name="mysql_agent",
    model="gemini-2.0-flash", # model=LiteLlm(model="openai/gpt-4o")
    description="An agent that can execute SQL queries on a MySQL database.",
    instruction='''Run SQL queries first to get context (table names and columns) of tables in the database and once you've done that then run the required  query to answer the users question.
                Do not ask the user for additional information.
                NEVER ASSUME A COLUMN OR TABLE NAME, RUN QUERIES TO GET THAT INFORMATION
                1. Run inspection queries to understand the database schema before answering the user's request.
                SHOW TABLES;
                DESCRIBE <table_name>;
                2. Now that you will have context of the database schema you may run SQL queries that achieve the users objectives/answers the users question 
                ''',
    tools=[query_tool]
)

orchestrator_agent = SequentialAgent(
    name="orchestrator_agent",
    description="Orchestrates the user intent agent and the MySQL agent to handle user requests.",
    sub_agents=[user_intent_agent, mysql_agent],
)


loop_agent = LoopAgent(
    name="loop_agent",
    description="A loop agent that runs the user intent agent and MySQL agent in a loop until the user indicates they are done.",
    sub_agents=[orchestrator_agent],
    max_iterations=3
)

root_agent = loop_agent
