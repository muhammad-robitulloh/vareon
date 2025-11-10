import asyncio
import os
import pty
import fcntl
import termios
import struct
from typing import Optional

class TerminalService:
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.master_fd: Optional[int] = None
        self.slave_fd: Optional[int] = None
        self.shell_process: Optional[asyncio.subprocess.Process] = None

    async def start_session(self, project_root: str):
        self.master_fd, self.slave_fd = pty.openpty()

        self.shell_process = await asyncio.create_subprocess_exec(
            os.environ.get("SHELL", "/bin/bash"),
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            cwd=project_root
        )
        
        # Return a non-blocking reader for the master fd
        return os.fdopen(self.master_fd, 'rb', 0)

    def write(self, data: str):
        if self.master_fd:
            os.write(self.master_fd, data.encode())

    async def execute_command(self, command: str) -> (str, str):
        """
        Executes a single non-interactive command and returns its stdout and stderr.
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode()

    def resize(self, cols: int, rows: int):
        if self.master_fd:
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))

    async def close_session(self):
        if self.shell_process and self.shell_process.returncode is None:
            self.shell_process.terminate()
            await self.shell_process.wait()
        
        if self.master_fd:
            os.close(self.master_fd)
        if self.slave_fd:
            os.close(self.slave_fd)
