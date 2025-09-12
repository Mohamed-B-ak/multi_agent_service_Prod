import os
import requests
from typing import Optional
from crewai.tools import BaseTool


class CallTool(BaseTool):
    name: str = "Call Tool"
    description: str = (
        "Use for placing a short voice call. Args: to_number(str), script(str). "
        "Currently stubbed; returns simulated confirmation."
    )

    def _run(self, to_number: str, script: str) -> str:
        return f"☎️ Call (stub) to {to_number} with script: {script[:80]}"
 