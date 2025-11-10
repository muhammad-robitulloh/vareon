from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
import uuid

# --- Arcana Agent Schemas ---

class ArcanaAgentBase(BaseModel):
    name: str = Field(..., description="The name of the Arcana agent.")
    persona: str = Field("default", description="The persona or personality of the agent (e.g., 'developer', 'analyst').")
    mode: str = Field("chat", description="The operational mode of the agent (e.g., 'chat', 'autonomous', 'tool_user').")
    objective: Optional[str] = Field(None, description="The primary objective or goal for the agent, especially in autonomous mode.")
    status: str = Field("idle", description="The current status of the agent (e.g., 'idle', 'running', 'stopped').")
    configuration: Optional[Dict[str, Any]] = Field(None, description="JSON field for agent-specific configuration.")

class ArcanaAgentCreate(ArcanaAgentBase):
    pass

class ArcanaAgentUpdate(BaseModel):
    name: Optional[str] = None
    persona: Optional[str] = None
    mode: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class ArcanaAgentResponse(ArcanaAgentBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Code Generation Schemas ---
class CodeGenerationRequest(BaseModel):
    prompt: str = Field(..., description="The natural language prompt for code generation.")
    language: str = Field("python", description="The programming language for the generated code (e.g., 'python', 'javascript', 'java').")
    context: Optional[str] = Field(None, description="Additional context or existing code to inform the generation.")
    model_name: Optional[str] = Field(None, description="Specific LLM model to use for code generation. If None, a default will be selected.")

class CodeGenerationResponse(BaseModel):
    generated_code: str = Field(..., description="The generated code.")
    language: str = Field(..., description="The programming language of the generated code.")
    model_used: str = Field(..., description="The LLM model used for generation.")
    reasoning: Optional[str] = Field(None, description="Optional explanation or reasoning behind the generated code.")
    success: bool = Field(True, description="Indicates if the code generation was successful.")
    error_message: Optional[str] = Field(None, description="Error message if generation failed.")

# --- Shell Command Translation Schemas ---
class ShellCommandTranslationRequest(BaseModel):
    prompt: str = Field(..., description="The natural language instruction to translate into a shell command.")
    current_directory: Optional[str] = Field(None, description="The current working directory for context.")
    shell_type: str = Field("bash", description="The type of shell (e.g., 'bash', 'zsh', 'powershell').")
    model_name: Optional[str] = Field(None, description="Specific LLM model to use for translation. If None, a default will be selected.")

class ShellCommandTranslationResponse(BaseModel):
    translated_command: str = Field(..., description="The translated shell command.")
    reasoning: Optional[str] = Field(None, description="Optional explanation or reasoning behind the translated command.")
    model_used: str = Field(..., description="The LLM model used for translation.")
    is_safe: bool = Field(False, description="Indicates if the translated command is considered safe for execution.")
    safety_warning: Optional[str] = Field(None, description="Warning message if the command is potentially unsafe.")
    success: bool = Field(True, description="Indicates if the translation was successful.")
    error_message: Optional[str] = Field(None, description="Error message if translation failed.")

# --- Reasoning System Schemas ---
class ReasoningRequest(BaseModel):
    prompt: str = Field(..., description="The user's prompt or task for which reasoning is required.")
    context: Optional[str] = Field(None, description="Additional context (e.g., chat history, code snippets, file contents) for reasoning.")
    task_type: str = Field("general", description="The type of task for which reasoning is being generated (e.g., 'general', 'code_generation', 'shell_command').")
    model_name: Optional[str] = Field(None, description="Specific LLM model to use for reasoning. If None, a default will be selected.")

class ReasoningStep(BaseModel):
    step_number: int = Field(..., description="The order of the reasoning step.")
    description: str = Field(..., description="Description of the reasoning step.")
    action: Optional[str] = Field(None, description="The action planned or taken for this step.")
    outcome: Optional[str] = Field(None, description="The expected or actual outcome of the action.")

class ReasoningResponse(BaseModel):
    reasoning_trace: List[ReasoningStep] = Field(..., description="A detailed trace of the AI's thought process.")
    summary: Optional[str] = Field(None, description="A high-level summary of the reasoning.")
    model_used: str = Field(..., description="The LLM model used for generating reasoning.")
    success: bool = Field(True, description="Indicates if reasoning generation was successful.")
    error_message: Optional[str] = Field(None, description="Error message if reasoning generation failed.")

# --- File Operations Schemas ---
class FileOperationRequest(BaseModel):
    action: Literal["read", "write", "delete", "list", "create_directory"] = Field(..., description="The file operation to perform.")
    path: str = Field(..., description="The path to the file or directory.")
    content: Optional[str] = Field(None, description="Content to write for 'write' operation.")
    recursive: bool = Field(False, description="For 'list' or 'delete' operations, whether to operate recursively.")

class FileInfo(BaseModel):
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    last_modified: Optional[datetime] = None

class FileOperationResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the file operation was successful.")
    message: str = Field(..., description="A message describing the outcome of the operation.")
    content: Optional[str] = Field(None, description="Content of the file for 'read' operation.")
    file_list: Optional[List[FileInfo]] = Field(None, description="List of files/directories for 'list' operation.")
    error_message: Optional[str] = Field(None, description="Error message if the operation failed.")

# --- Agent Orchestration Schemas ---
class AgentExecuteRequest(BaseModel):
    task_prompt: str = Field(..., description="The natural language prompt describing the task for the agent.")
    agent_id: str = Field(..., description="The ID of the Arcana Agent to execute the task.")
    context: Optional[str] = Field(None, description="Additional context for the agent's task.")

class AgentExecuteResponse(BaseModel):
    agent_id: str = Field(..., description="The ID of the Arcana Agent that executed the task.")
    status: str = Field(..., description="The status of the agent's execution (e.g., 'success', 'failed', 'in_progress').")
    output: Optional[str] = Field(None, description="The output or result of the agent's task.")
    actions_taken: Optional[List[str]] = Field(None, description="A list of actions the agent performed.")
    error_message: Optional[str] = Field(None, description="Error message if the execution failed.")