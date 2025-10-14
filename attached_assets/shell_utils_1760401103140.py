import asyncio
import shlex
import logging
from .. import config

logger = logging.getLogger(__name__)

def is_command_safe(command: str) -> bool:
    """Checks if a shell command is in the whitelist of safe commands."""
    try:
        main_command = shlex.split(command)[0]
    except (ValueError, IndexError):
        return False

    safe_commands = ["ls", "cd", "pwd", "echo", "cat", "grep", "find", "touch", "mkdir", "mv", "cp", "rm", "rmdir", "chmod", "git", "pip", "python", "node", "npm", "bash", "sh", "wget", "curl", "unzip", "tar", "ps", "kill", "df", "du", "uname", "history", "clear", "which", "apt", "pkg"]
    return main_command in safe_commands

async def execute_shell_command(command_to_run: str):
    """Executes a shell command and yields output line by line."""
    if not is_command_safe(command_to_run):
        yield {"type": "error", "content": f"Command not allowed: {command_to_run}"}
        yield {"type": "done", "content": ""}
        return

    try:
        process = await asyncio.create_subprocess_shell(
            command_to_run, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=config.PROJECT_ROOT
        )
        async for line in process.stdout:
            yield {"type": "shell_output", "content": line.decode().strip()}
        async for line in process.stderr:
            yield {"type": "shell_error", "content": line.decode().strip()}
        
        await process.wait()
    except Exception as e:
        yield {"type": "error", "content": f"Failed to execute command: {e}"}
    
    yield {"type": "done", "content": ""}
