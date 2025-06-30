from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
from google.adk.tools.tool_context import ToolContext

import litellm
litellm._turn_on_debug()

query_tool = MCPToolset(
        connection_params=StdioConnectionParams(
            timeout=60,
            server_params=StdioServerParameters(
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
    description="Understand the user's intent and decide whether to run a SQL query or exit the loop.",
    instruction='''
Your job is to understand the user's intent and decide whether to run a SQL query or exit the loop.

- If the user's request requires any SQL/database action, DO NOT call any tool. Clearly state what you intend to do (e.g., "I will run a SQL query to show the tables in the database.") and stop. The system will transfer control to the MySQL agent.
- Only call the exit_loop tool if:
    1. The user's request has been fully answered or satisfied.
    2. The user's question is unrelated to the database.
    3. The user greets you (e.g., "Hi", "Hello")—in this case, greet them back, briefly state your purpose, and immediately call exit_loop.
    4. The user's question is unclear or confusing and you cannot proceed—ask a clarifying question and then call exit_loop.

Never assume table or column names—let the MySQL agent handle all SQL/database actions.

Do not mention the tools available to you. Only call exit_loop when appropriate, otherwise just state your intent and stop.
''',
    model="gemini-2.0-flash",  # model=LiteLlm(model="openai/gpt-4o") # TODO: Upgrade to a more intelligent reasoning model
    tools=[exit_loop]
)

mysql_agent = Agent(
    name="mysql_agent",
    model=LiteLlm(model="openai/o4-mini-2025-04-16"),
    description="Execute read-only SQL queries against the MySQL database. Usage: Pass a valid SQL statement to retrieve schema info or data.",
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
