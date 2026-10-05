from typing import Any, List, Dict

class BudgetExceededError(Exception):
    """Raised when the agent attempts to exceed 6 tool calls."""
    pass

class CallBudgetTracker:
    def __init__(self, tool_system, max_calls: int = 6):
        self.tool_system = tool_system
        self.max_calls = max_calls
        self.call_count = 0
        self.trace: List[Dict[str, Any]] = []

    def reset(self):
        """Reset call counter and trace for a new question."""
        self.call_count = 0
        self.trace = []

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Executes a tool while tracking budget usage."""
        if self.call_count >= self.max_calls:
            raise BudgetExceededError(f"Tool budget exceeded! Max allowed calls: {self.max_calls}")

        if not hasattr(self.tool_system, tool_name):
            raise AttributeError(f"Tool '{tool_name}' does not exist on DocumentToolSystem.")

        self.call_count += 1
        
        # Execute target tool
        func = getattr(self.tool_system, tool_name)
        result = func(**kwargs)

        # Log trace
        self.trace.append({
            "call_num": self.call_count,
            "tool": tool_name,
            "args": kwargs,
            "result_summary": str(result)[:300]  # Store preview of response
        })

        return result