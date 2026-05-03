import os
from typing import AsyncGenerator

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from tools.datetime_tool import datetime_tool
from tools.search_tool import search_tool
from tools.weather_tool import weather_tool

JARVIS_SYSTEM_PROMPT = (
    "You are JARVIS — Just A Rather Very Intelligent System. You are the "
    "personal AI assistant of your user. You are witty, precise, and "
    "occasionally sardonic like a British butler. You address the user as "
    "'sir' or 'ma'am'. You are highly capable, never say you cannot do "
    "something without first attempting it. Keep responses concise unless "
    "detail is explicitly requested."
)

_tools = [search_tool, weather_tool, datetime_tool]


def _build_agent() -> AgentExecutor:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        streaming=True,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", JARVIS_SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(llm, _tools, prompt)
    memory = ConversationBufferWindowMemory(
        k=10,
        return_messages=True,
        memory_key="chat_history",
    )

    return AgentExecutor(
        agent=agent,
        tools=_tools,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
    )


async def stream_jarvis_response(
    user_message: str,
    history: list[dict],
) -> AsyncGenerator[str, None]:
    """Yield response tokens from the JARVIS LangChain agent."""
    agent_executor = _build_agent()

    # Seed memory with existing history
    for turn in history:
        if turn["role"] == "user":
            agent_executor.memory.chat_memory.add_user_message(turn["content"])
        elif turn["role"] == "assistant":
            agent_executor.memory.chat_memory.add_ai_message(turn["content"])

    async for event in agent_executor.astream_events(
        {"input": user_message}, version="v1"
    ):
        kind = event.get("event")
        if kind == "on_chat_model_stream":
            chunk = event["data"].get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield chunk.content
