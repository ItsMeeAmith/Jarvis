from datetime import datetime, timezone

from langchain.tools import Tool


def _get_datetime(_: str = "") -> str:
    now = datetime.now(timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo
    local_now = datetime.now(local_tz)

    return (
        f"Current date and time:\n"
        f"  UTC:   {now.strftime('%A, %d %B %Y %H:%M:%S UTC')}\n"
        f"  Local: {local_now.strftime('%A, %d %B %Y %H:%M:%S %Z')}"
    )


datetime_tool = Tool(
    name="get_datetime",
    func=_get_datetime,
    description=(
        "Get the current date and time in UTC and local time. "
        "Use this tool whenever the user asks about the current time, date, "
        "day of the week, or any time-related query. "
        "No input is required."
    ),
)
