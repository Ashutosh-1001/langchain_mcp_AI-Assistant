import asyncio, os, json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters import mcp_use
from langchain.agents import initialize_agent, AgentType

load_dotenv()

with open("servers.json") as f:
    config = json.load(f)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def main():
    tools = []
    
    contexts = [
        mcp_use(server["command"] + server.get("args", []),
                env={**os.environ, **server.get("env", {})})
        for server in config["servers"]
    ]
    async with asyncio.TaskGroup() as tg:
        running = [tg.create_task(ctx.__aenter__()) for ctx in contexts]
    for toolkit in [t.result() for t in running]:
        tools.extend(toolkit.get_tools())

    agent = initialize_agent(tools, llm, AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True)

  

asyncio.run(main())
