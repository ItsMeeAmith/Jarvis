import os

from langchain.tools import Tool

_SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


def _search(query: str) -> str:
    if _SERPAPI_KEY:
        return _serpapi_search(query)
    return _ddg_search(query)


def _serpapi_search(query: str) -> str:
    try:
        from langchain_community.utilities import SerpAPIWrapper

        wrapper = SerpAPIWrapper(serpapi_api_key=_SERPAPI_KEY)
        return wrapper.run(query)
    except Exception as exc:
        return f"SerpAPI search failed: {exc}. Falling back to DuckDuckGo.\n" + _ddg_search(query)


def _ddg_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                title = r.get("title", "")
                href = r.get("href", "")
                body = r.get("body", "")
                results.append(f"**{title}**\n{body}\n{href}")
        return "\n\n".join(results) if results else "No results found."
    except Exception as exc:
        return f"Search failed: {exc}"


search_tool = Tool(
    name="web_search",
    func=_search,
    description=(
        "Search the web for current information. "
        "Use this tool when the user asks about recent events, facts, or anything "
        "that may require up-to-date information. "
        "Input should be a concise search query string."
    ),
)
