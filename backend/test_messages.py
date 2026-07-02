import asyncio
from app.agent.graph import run_agent, get_agent_graph
from app.agent.state import AgentState

async def main():
    res1 = await run_agent("test_session_1", input_type="text", text_message="hi")
    print(f"Run 1 message count: {len(res1['messages'])}")
    res2 = await run_agent("test_session_1", input_type="text", text_message="hi again")
    print(f"Run 2 message count: {len(res2['messages'])}")

asyncio.run(main())
