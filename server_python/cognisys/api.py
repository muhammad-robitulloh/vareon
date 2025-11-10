import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user, PermissionChecker
from . import crud, schemas, llm_interaction
from .llm_interaction import process_chat_request

router = APIRouter()

### LLM Provider Management ###

@router.post("/providers/", response_model=schemas.LLMProviderResponse, status_code=status.HTTP_201_CREATED)
def create_llm_provider(provider: schemas.LLMProviderCreate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_provider = crud.create_llm_provider(db=db, provider=provider)
    return db_provider

@router.get("/providers/", response_model=List[schemas.LLMProviderResponse])
def read_llm_providers(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    providers = crud.get_llm_providers(db, skip=skip, limit=limit)
    return providers

@router.get("/providers/{provider_id}", response_model=schemas.LLMProviderResponse)
def read_llm_provider(provider_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_provider = crud.get_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    return db_provider

@router.put("/providers/{provider_id}", response_model=schemas.LLMProviderResponse)
def update_llm_provider(provider_id: str, provider: schemas.LLMProviderUpdate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_provider = crud.update_llm_provider(db, provider_id=provider_id, provider=provider)
    if db_provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    return db_provider

@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_provider(provider_id: str, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_provider = crud.delete_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")
    return {"ok": True}

@router.post("/providers/{provider_id}/test-connection", status_code=status.HTTP_200_OK)
async def test_llm_provider_connection(provider_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_provider = crud.get_llm_provider(db, provider_id=provider_id)
    if db_provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Provider not found")

    api_key = crud.decrypt_api_key(db_provider.api_key_encrypted)
    
    print(f"Attempting to test connection for provider {db_provider.name} at {db_provider.base_url}...")

    try:
        # This is a generic test. Real LLM providers might need specific endpoints or headers.
        # For now, we just try to reach the base_url.
        async with httpx.AsyncClient() as client:
            response = await client.get(db_provider.base_url, timeout=5)
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses

        return {
            "message": f"Connection to provider {db_provider.name} successful.",
            "status": "success"
        }
    except httpx.RequestError as e:
        print(f"Connection test failed for {db_provider.name}: {e}")
        return {
            "message": f"Connection to provider {db_provider.name} failed: {e}",
            "status": "failure"
        }
    except httpx.HTTPStatusError as e:
        print(f"Connection test failed for {db_provider.name} with HTTP error: {e.response.status_code} - {e.response.text}")
        return {
            "message": f"Connection to provider {db_provider.name} failed with HTTP error: {e.response.status_code} - {e.response.text}",
            "status": "failure"
        }
    except Exception as e:
        print(f"An unexpected error occurred during connection test for {db_provider.name}: {e}")
        return {
            "message": f"An unexpected error occurred during connection test for {db_provider.name}: {e}",
            "status": "failure"
        }

### LLM Model Mapping ###

@router.post("/models/", response_model=schemas.LLMModelResponse, status_code=status.HTTP_201_CREATED)
def create_llm_model(model: schemas.LLMModelCreate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_model = crud.create_llm_model(db=db, model=model)
    return db_model

@router.get("/models/", response_model=List[schemas.LLMModelResponse])
def read_llm_models(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    models = crud.get_llm_models(db, skip=skip, limit=limit)
    return models

@router.get("/models/{model_id}", response_model=schemas.LLMModelResponse)
def read_llm_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_model = crud.get_llm_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    return db_model

@router.put("/models/{model_id}", response_model=schemas.LLMModelResponse)
def update_llm_model(model_id: str, model: schemas.LLMModelUpdate, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_model = crud.update_llm_model(db, model_id=model_id, model=model)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    return db_model

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_llm_model(model_id: str, current_user: DBUser = Depends(PermissionChecker(["admin_access"])), db: Session = Depends(get_db)):
    db_model = crud.delete_llm_model(db, model_id=model_id)
    if db_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM Model not found")
    return {"ok": True}

### Routing Rules Management ###

@router.post("/routing-rules/", response_model=schemas.RoutingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_routing_rule(rule: schemas.RoutingRuleCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = crud.create_routing_rule(db=db, rule=rule, owner_id=str(current_user.id))
    return db_rule

@router.get("/routing-rules/", response_model=List[schemas.RoutingRuleResponse])
def read_routing_rules(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rules = crud.get_routing_rules(db, skip=skip, limit=limit)
    return rules

@router.get("/routing-rules/{rule_id}", response_model=schemas.RoutingRuleResponse)
def read_routing_rule(rule_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = crud.get_routing_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    return db_rule

@router.put("/routing-rules/{rule_id}", response_model=schemas.RoutingRuleResponse)
def update_routing_rule(rule_id: str, rule: schemas.RoutingRuleUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = crud.update_routing_rule(db, rule_id=rule_id, rule=rule, owner_id=str(current_user.id))
    if db_rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    return db_rule

@router.delete("/routing-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routing_rule(rule_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = crud.delete_routing_rule(db, rule_id=rule_id)
    if db_rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing Rule not found")
    return {"ok": True}

### Test Console & AI Interaction ###

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_cognisys(chat_request: schemas.ChatRequest, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    response_data = await llm_interaction.process_chat_request(db, current_user, chat_request.prompt, session_data={})
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
    return await llm_interaction.detect_intent(db, current_user, request.prompt)
