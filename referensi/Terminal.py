@app.websocket("/ws/shell/{chat_id}")
async def websocket_shell(websocket: WebSocket, chat_id: int):
    await websocket.accept()

    # Create a pseudo-terminal (pty)
    master_fd, slave_fd = pty.openpty()

    # Start a shell process (e.g., bash) in the pty
    shell_process = await asyncio.create_subprocess_exec(
        os.environ.get("SHELL", "/bin/bash"),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=config.PROJECT_ROOT # Use config.PROJECT_ROOT
    )

    # Get a non-blocking file-like object for the master end of the pty
    master_reader = os.fdopen(master_fd, 'rb', 0)

    async def forward_shell_to_client():
        """Reads from the shell's output and sends it to the WebSocket client."""
        try:
            while True:
                output = await asyncio.to_thread(master_reader.read, 1024)
                if not output:
                    logger.info(f"[WebSocket] Shell output stream for client {chat_id} ended.")
                    break
                await websocket.send_text(output.decode(errors='ignore'))
        except (IOError, WebSocketDisconnect) as e:
            logger.info(f"[WebSocket] Shell output stream for client {chat_id} closed due to: {e}")
        except Exception as e:
            logger.error(f"[WebSocket] Unexpected error in forward_shell_to_client for client {chat_id}: {e}", exc_info=True)
        finally:
            # This task is only for forwarding. The main loop handles all cleanup.
            logger.info(f"[WebSocket] forward_shell_to_client task for client {chat_id} finishing.")

    client_task = asyncio.create_task(forward_shell_to_client(), name=f"shell_forwarder_{chat_id}")

    try:
        while True:
            # Wait for data from the client
            data = await websocket.receive_text()
            logger.debug(f"[WebSocket] Received data from client {chat_id}: {data[:100]}...") # Log first 100 chars
            # Check for resize command (sent as JSON from frontend)
            try:
                data_json = json.loads(data)
                if 'resize' in data_json:
                    import fcntl, termios, struct
                    cols, rows = data_json['resize']['cols'], data_json['resize']['rows']
                    logger.info(f"[WebSocket] Resizing PTY for client {chat_id} to {cols}x{rows}")
                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                    continue # Skip writing resize command to shell
            except json.JSONDecodeError:
                pass # It's regular user input, not a resize command

            # Forward user input to the shell
            os.write(master_fd, data.encode())

    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client {chat_id} disconnected.")
    except Exception as e:
        logger.error(f"[WebSocket] Unexpected error in main WebSocket loop for client {chat_id}: {e}", exc_info=True)
    finally:
        logger.info(f"[WebSocket] Cleaning up resources for client {chat_id}.")
        # Clean up: terminate the shell process and cancel the reading task
        client_task.cancel()
        if shell_process.returncode is None:
            logger.info(f"[WebSocket] Terminating shell process for client {chat_id}.")
            shell_process.terminate()

        try:
            await shell_process.wait()
        except asyncio.CancelledError:
            logger.info(f"Shell process cleanup for client {chat_id} was interrupted by server shutdown.")

        master_reader.close()
        try:
            os.close(master_fd) # Explicitly close the master file descriptor
        except OSError as e:
            logger.error(f"Error closing master_fd for client {chat_id}: {e}")
        try:
            os.close(slave_fd) # Explicitly close the slave file descriptor
        except OSError as e:
            logger.error(f"Error closing slave_fd for client {chat_id}: {e}")
        logger.info(f"[WebSocket] Resources cleaned up for client {chat_id}.")
