import httpx
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import os

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user, PermissionChecker
from . import crud, schemas, llm_interaction
from .llm_interaction import process_chat_request
from server_python.terminal.service import TerminalService

# Initialize a logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

### LLM Provider Management ###

@router.post("/providers/", response_model=schemas.LLMProviderResponse, status_code=status.HTTP_201_CREATED)
def create_llm_provider(provider: schemas.LLMProviderCreate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} creating new LLM provider '{provider.name}'.")
    db_provider = crud.create_llm_provider(db=db, provider=provider)
    logger.info(f"LLM provider '{db_provider.name}' created with ID {db_provider.id}.")
    return db_provider

@router.get("/providers/", response_model=List[schemas.LLMProviderResponse])
def read_llm_providers(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading LLM providers.")
    providers = crud.get_llm_providers(db, skip=skip, limit=limit)
    return providers

@router.get("/providers/{provider_id}", response_model=schemas.LLMProviderResponse)
def read_llm_provider(provider_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading LLM provider {provider_id}.")
    db_provider = crud.get_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        logger.warning(f"User {current_user.id} failed to find LLM provider {provider_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    return db_provider

@router.put("/providers/{provider_id}", response_model=schemas.LLMProviderResponse)
def update_llm_provider(provider_id: str, provider: schemas.LLMProviderUpdate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Attempting to update LLM provider {provider_id} by user {current_user.id}.")
    logger.info(f"User {current_user.id} roles: {[role.name for role in current_user.roles]}")
    from server_python.auth import has_permission # Import has_permission for direct check
    logger.info(f"User {current_user.id} has 'admin_access' permission: {has_permission(current_user, 'admin_access')}")
    logger.info(f"Admin user {current_user.id} updating LLM provider {provider_id}.")
    db_provider = crud.update_llm_provider(db, provider_id=provider_id, provider=provider)
    if db_provider is None:
        logger.warning(f"Admin user {current_user.id} failed to update non-existent LLM provider {provider_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    logger.info(f"LLM provider {provider_id} updated successfully.")
    return db_provider

@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_provider(provider_id: str, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} deleting LLM provider {provider_id}.")
    db_provider = crud.delete_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        logger.warning(f"Admin user {current_user.id} failed to delete non-existent LLM provider {provider_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    logger.info(f"LLM provider {provider_id} deleted successfully.")
    return {"ok": True}

@router.post("/providers/{provider_id}/test-connection", status_code=status.HTTP_200_OK)
async def test_llm_provider_connection(provider_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} testing connection for provider {provider_id}.")
    db_provider = crud.get_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        logger.warning(f"Connection test failed: Provider {provider_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")

    if not db_provider.api_key_encrypted:
        logger.warning(f"Connection test failed for provider {provider_id}: API key is not set.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is not set for this provider. Please edit the provider to set a valid API key before testing the connection."
        )

    api_key = crud.decrypt_api_key(db_provider.api_key_encrypted)
    logger.info(f"Attempting to test connection for provider {db_provider.name} at {db_provider.base_url}...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(db_provider.base_url, timeout=5)
            response.raise_for_status()
        logger.info(f"Connection test successful for provider {db_provider.name}.")
        return {
            "message": f"Connection to provider {db_provider.name} successful.",
            "status": "success"
        }
    except httpx.RequestError as e:
        logger.error(f"Connection test failed for {db_provider.name}: {e}", exc_info=True)
        return {
            "message": f"Connection to provider {db_provider.name} failed: {e}",
            "status": "failure"
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"Connection test for {db_provider.name} failed with HTTP error: {e.response.status_code} - {e.response.text}", exc_info=True)
        return {
            "message": f"Connection to provider {db_provider.name} failed with HTTP error: {e.response.status_code} - {e.response.text}",
            "status": "failure"
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred during connection test for {db_provider.name}: {e}", exc_info=True)
        return {
            "message": f"An unexpected error occurred during connection test for {db_provider.name}: {e}",
            "status": "failure"
        }

### LLM Model Mapping ###

@router.post("/models/", response_model=schemas.LLMModelResponse, status_code=status.HTTP_201_CREATED)
def create_llm_model(model: schemas.LLMModelCreate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} creating new LLM model '{model.model_name}'.")
    db_model = crud.create_llm_model(db=db, model=model)
    logger.info(f"LLM model '{db_model.model_name}' created with ID {db_model.id}.")
    return db_model

@router.get("/models/", response_model=List[schemas.LLMModelResponse])
def read_llm_models(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading LLM models.")
    models = crud.get_llm_models(db, skip=skip, limit=limit)
    return models

@router.get("/models/{model_id}", response_model=schemas.LLMModelResponse)
def read_llm_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading LLM model {model_id}.")
    db_model = crud.get_llm_model(db, model_id=model_id)
    if db_model is None:
        logger.warning(f"User {current_user.id} failed to find LLM model {model_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    return db_model

@router.put("/models/{model_id}", response_model=schemas.LLMModelResponse)
def update_llm_model(model_id: str, model: schemas.LLMModelUpdate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} updating LLM model {model_id}.")
    db_model = crud.update_llm_model(db, model_id=model_id, model=model)
    if db_model is None:
        logger.warning(f"Admin user {current_user.id} failed to update non-existent LLM model {model_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    logger.info(f"LLM model {model_id} updated successfully.")
    return db_model

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_model(model_id: str, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} deleting LLM model {model_id}.")
    db_model = crud.delete_llm_model(db, model_id=model_id)
    if db_model is None:
        logger.warning(f"Admin user {current_user.id} failed to delete non-existent LLM model {model_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    logger.info(f"LLM model {model_id} deleted successfully.")
    return {"ok": True}

### Routing Rules Management ###

@router.post("/routing-rules/", response_model=schemas.RoutingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_routing_rule(rule: schemas.RoutingRuleCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} creating new routing rule '{rule.name}'.")
    db_rule = crud.create_routing_rule(db=db, rule=rule, owner_id=str(current_user.id))
    logger.info(f"Routing rule '{db_rule.name}' created with ID {db_rule.id} for user {current_user.id}.")
    return db_rule

@router.get("/routing-rules/", response_model=List[schemas.RoutingRuleResponse])
def read_routing_rules(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading routing rules.")
    rules = crud.get_routing_rules(db, skip=skip, limit=limit)
    return rules

@router.get("/routing-rules/{rule_id}", response_model=schemas.RoutingRuleResponse)
def read_routing_rule(rule_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading routing rule {rule_id}.")
    db_rule = crud.get_routing_rule(db, rule_id=rule_id)
    if db_rule is None:
        logger.warning(f"User {current_user.id} failed to find routing rule {rule_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    return db_rule

@router.put("/routing-rules/{rule_id}", response_model=schemas.RoutingRuleResponse)
def update_routing_rule(rule_id: str, rule: schemas.RoutingRuleUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} updating routing rule {rule_id}.")
    db_rule = crud.update_routing_rule(db, rule_id=rule_id, rule=rule, owner_id=str(current_user.id))
    if db_rule is None:
        logger.warning(f"User {current_user.id} failed to update non-existent routing rule {rule_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    logger.info(f"Routing rule {rule_id} updated successfully for user {current_user.id}.")
    return db_rule

@router.delete("/routing-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routing_rule(rule_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} deleting routing rule {rule_id}.")
    db_rule = crud.delete_routing_rule(db, rule_id=rule_id)
    if db_rule is None:
        logger.warning(f"User {current_user.id} failed to delete non-existent routing rule {rule_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    logger.info(f"Routing rule {rule_id} deleted successfully.")
    return {"ok": True}

### Test Console & AI Interaction ###

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_cognisys(
    chat_request: schemas.ChatRequest, 
    background_tasks: BackgroundTasks, # Inject BackgroundTasks
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    logger.info(f"User {current_user.id} initiated a chat with prompt: '{chat_request.prompt[:50]}...'.")
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    project_root = os.getcwd()
    terminal_service = TerminalService(session_id=str(current_user.id), user_id=str(current_user.id))
    session_data = {"terminal": terminal_service}

    # Pass background_tasks to the processing function
    response_data = await llm_interaction.process_chat_request(
        db=db, 
        user=current_user, 
        prompt=chat_request.prompt, 
        session_data=session_data,
        background_tasks=background_tasks
    )
    logger.info(f"Chat response generated for user {current_user.id}.")
    return schemas.ChatResponse(**response_data)

@router.post("/detect-intent", response_model=schemas.IntentDetectionResponse)
async def detect_user_intent(
    request: schemas.IntentDetectionRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detects the intent of the user's prompt using an LLM.
    """
    logger.info(f"User {current_user.id} requested intent detection for prompt: '{request.prompt[:50]}...'.")
    response = await llm_interaction.detect_intent(db, current_user, request.prompt)
    logger.info(f"Intent detected for user {current_user.id}: {response.intent}")
    return response

### System Prompt Management ###

@router.post("/system-prompts/", response_model=schemas.SystemPromptResponse, status_code=status.HTTP_201_CREATED)
def create_system_prompt(prompt: schemas.SystemPromptCreate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} creating new system prompt '{prompt.name}'.")
    db_prompt = crud.create_system_prompt(db=db, prompt=prompt)
    logger.info(f"System prompt '{db_prompt.name}' created with ID {db_prompt.id}.")
    return db_prompt

@router.get("/system-prompts/", response_model=List[schemas.SystemPromptResponse])
def read_system_prompts(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading system prompts.")
    prompts = crud.get_system_prompts(db, skip=skip, limit=limit)
    return prompts

@router.get("/system-prompts/{prompt_id}", response_model=schemas.SystemPromptResponse)
def read_system_prompt(prompt_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} reading system prompt {prompt_id}.")
    db_prompt = crud.get_system_prompt(db, prompt_id=prompt_id)
    if db_prompt is None:
        logger.warning(f"User {current_user.id} failed to find system prompt {prompt_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System Prompt not found")
    return db_prompt

@router.put("/system-prompts/{prompt_id}", response_model=schemas.SystemPromptResponse)
def update_system_prompt(prompt_id: str, prompt: schemas.SystemPromptUpdate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} updating system prompt {prompt_id}.")
    db_prompt = crud.update_system_prompt(db, prompt_id=prompt_id, prompt=prompt)
    if db_prompt is None:
        logger.warning(f"Admin user {current_user.id} failed to update non-existent system prompt {prompt_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System Prompt not found")
    logger.info(f"System prompt {prompt_id} updated successfully.")
    return db_prompt

@router.delete("/system-prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_prompt(prompt_id: str, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    logger.info(f"Admin user {current_user.id} deleting system prompt {prompt_id}.")
    db_prompt = crud.delete_system_prompt(db, prompt_id=prompt_id)
    if db_prompt is None:
        logger.warning(f"Admin user {current_user.id} failed to delete non-existent system prompt {prompt_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System Prompt not found")
    logger.info(f"System prompt {prompt_id} deleted successfully.")
    return {"ok": True}

@router.get("/cli/model-details", response_model=schemas.CliModelDetailsResponse)
def get_cli_model_details(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves details of the user's preferred LLM model for CLI usage.
    """
    logger.info(f"User {current_user.id} requested CLI model details.")
    model_details = crud.get_user_preferred_model_details(db, str(current_user.id))
    if model_details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active LLM model found for user or system.")
    return schemas.CliModelDetailsResponse(**model_details)

