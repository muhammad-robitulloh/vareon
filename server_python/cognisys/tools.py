from typing import Dict, Any, Callable, List
import asyncio

# This is a placeholder for the real TerminalService instance,
# which will be passed in during the actual call.
from terminal.service import TerminalService

# 1. Tool Definition
# A tool is a dictionary with a schema for the LLM and a function to call.

async def execute_shell_command(terminal_service: TerminalService, command: str) -> str:
    """
    Executes a shell command in the user's sandboxed environment and returns the output.
    
    :param terminal_service: The instance of the TerminalService for the user's session.
    :param command: The shell command to execute.
    :return: A string containing the stdout and stderr of the command.
    """
    print(f"Executing shell command: '{command}'")
    stdout, stderr = await terminal_service.execute_command(command)
    
    output = ""
    if stdout:
        output += f"STDOUT:\n{stdout}\n"
    if stderr:
        output += f"STDERR:\n{stderr}\n"
    
    if not output:
        return "Command executed with no output."
        
    return output

# 2. Tool Schema for the LLM
# This tells the LLM how to call our function.

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "execute_shell_command",
            "description": "Executes a shell command in the user's sandboxed environment and returns the output. Use this for any file system operations, running scripts, or checking system status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g., 'ls -l', 'cat my_file.txt').",
                    }
                },
                "required": ["command"],
            },
        },
    }
]

# 3. Tool Registry
# This maps the function name from the schema to the actual Python function.

tool_registry: Dict[str, Callable] = {
    "execute_shell_command": execute_shell_command,
}
