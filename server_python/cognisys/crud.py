import logging
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import json
from server_python.encryption_utils import encrypt_api_key, decrypt_api_key, InvalidToken

from . import schemas # Add this import

from server_python.database import LLMProvider, LLMModel, RoutingRule, RoutingRule as DBRoutingRule, SystemPrompt # Changed from ..database
from .schemas import LLMProviderCreate, LLMProviderUpdate, LLMModelCreate, LLMModelUpdate, RoutingRuleCreate, RoutingRuleUpdate, SystemPromptCreate, SystemPromptUpdate

logger = logging.getLogger(__name__)

# ... (existing code) ...

### System Prompt CRUD Operations ###

def get_system_prompt(db: Session, prompt_id: str):
    return db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()

def get_system_prompt_by_name(db: Session, name: str):
    return db.query(SystemPrompt).filter(SystemPrompt.name == name).first()

def get_system_prompts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SystemPrompt).offset(skip).limit(limit).all()

def create_system_prompt(db: Session, prompt: SystemPromptCreate):
    db_prompt = SystemPrompt(
        id=str(uuid.uuid4()),
        name=prompt.name,
        content=prompt.content,
        description=prompt.description
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def update_system_prompt(db: Session, prompt_id: str, prompt: SystemPromptUpdate):
    db_prompt = get_system_prompt(db, prompt_id)
    if db_prompt:
        if prompt.name is not None:
            db_prompt.name = prompt.name
        if prompt.content is not None:
            db_prompt.content = prompt.content
        if prompt.description is not None:
            db_prompt.description = prompt.description
        db_prompt.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_prompt)
    return db_prompt

def delete_system_prompt(db: Session, prompt_id: str):
    db_prompt = get_system_prompt(db, prompt_id)
    if db_prompt:
        db.delete(db_prompt)
        db.commit()
    return db_prompt

### LLM Provider CRUD Operations ###

def mask_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "********"
    return api_key[:4] + "..." + api_key[-4:]

def get_llm_provider(db: Session, provider_id: str):
    db_provider = db.query(LLMProvider).filter(LLMProvider.id == provider_id).first()
    if db_provider:
        try:
            decrypted_key = decrypt_api_key(db_provider.api_key_encrypted)
            db_provider.masked_api_key = mask_api_key(decrypted_key)
        except InvalidToken:
            db_provider.masked_api_key = "Invalid/Expired Key"
        except Exception:
            db_provider.masked_api_key = "Error Masking Key"
    return db_provider

def get_llm_providers(db: Session, skip: int = 0, limit: int = 100):
    providers = db.query(LLMProvider).offset(skip).limit(limit).all()
    for provider in providers:
        try:
            decrypted_key = decrypt_api_key(provider.api_key_encrypted)
            provider.masked_api_key = mask_api_key(decrypted_key)
        except InvalidToken:
            provider.masked_api_key = "Invalid/Expired Key"
        except Exception:
            provider.masked_api_key = "Error Masking Key"
    return providers

def create_llm_provider(db: Session, provider: LLMProviderCreate):
    encrypted_api_key = encrypt_api_key(provider.api_key)
    logger.info(f"Creating LLM provider '{provider.name}'. API key encrypted: {bool(encrypted_api_key)}")
    db_provider = LLMProvider(
        id=str(uuid.uuid4()),
        name=provider.name,
        api_key_encrypted=encrypted_api_key,
        base_url=provider.base_url,
        enabled=provider.enabled, # New field
        organization_id=provider.organization_id # New field
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def update_llm_provider(db: Session, provider_id: str, provider: LLMProviderUpdate):
    db_provider = get_llm_provider(db, provider_id)
    if db_provider:
        if provider.name is not None:
            db_provider.name = provider.name
        if provider.base_url is not None:
            db_provider.base_url = provider.base_url
        if provider.enabled is not None: # New field
            db_provider.enabled = provider.enabled
        if provider.organization_id is not None: # New field
            db_provider.organization_id = provider.organization_id
        if provider.api_key is not None:
            db_provider.api_key_encrypted = encrypt_api_key(provider.api_key)
            logger.info(f"Updating LLM provider '{db_provider.name}'. API key encrypted: {bool(db_provider.api_key_encrypted)}")
        db_provider.updated_at = datetime.utcnow()
        db.commit()
    return db_provider

def delete_llm_provider(db: Session, provider_id: str):
    db_provider = get_llm_provider(db, provider_id)
    if db_provider:
        db.delete(db_provider)
        db.commit()
    return db_provider

### LLM Model CRUD Operations ###

def get_llm_model(db: Session, model_id: str):
    return db.query(LLMModel).filter(LLMModel.id == model_id).first()

def get_llm_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LLMModel).offset(skip).limit(limit).all()

def create_llm_model(db: Session, model: LLMModelCreate):
    db_model = LLMModel(
        id=str(uuid.uuid4()),
        provider_id=model.provider_id,
        model_name=model.model_name,
        type=model.type, # New field
        is_active=model.is_active, # New field
        reasoning=model.reasoning, # New field
        role=model.role, # New field
        max_tokens=model.max_tokens,
        cost_per_token=model.cost_per_token
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def update_llm_model(db: Session, model_id: str, model: LLMModelUpdate):
    db_model = get_llm_model(db, model_id)
    if db_model:
        if model.provider_id is not None:
            db_model.provider_id = model.provider_id
        if model.model_name is not None:
            db_model.model_name = model.model_name
        if model.type is not None: # New field
            db_model.type = model.type
        if model.is_active is not None: # New field
            db_model.is_active = model.is_active
        if model.reasoning is not None: # New field
            db_model.reasoning = model.reasoning
        if model.role is not None: # New field
            db_model.role = model.role
        if model.max_tokens is not None:
            db_model.max_tokens = model.max_tokens
        if model.cost_per_token is not None:
            db_model.cost_per_token = model.cost_per_token
        db_model.updated_at = datetime.utcnow()
        db.commit()
    return db_model

def delete_llm_model(db: Session, model_id: str):
    db_model = get_llm_model(db, model_id)
    if db_model:
        db.delete(db_model)
        db.commit()
    return db_model

### Routing Rule CRUD Operations ###

def get_routing_rule(db: Session, rule_id: str):
    return db.query(DBRoutingRule).filter(DBRoutingRule.id == rule_id).first()

def get_routing_rules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DBRoutingRule).offset(skip).limit(limit).all()

def create_routing_rule(db: Session, rule: schemas.RoutingRuleCreate, owner_id: str):
    db_rule = DBRoutingRule(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=rule.name,
        condition=rule.condition,
        target_model=rule.target_model,
        priority=rule.priority
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_routing_rule(db: Session, rule_id: str, rule: schemas.RoutingRuleUpdate, owner_id: str):
    db_rule = get_routing_rule(db, rule_id)
    if db_rule:
        if rule.name is not None:
            db_rule.name = rule.name
        if rule.condition is not None:
            db_rule.condition = rule.condition
        if rule.target_model is not None:
            db_rule.target_model = rule.target_model
        if rule.priority is not None:
            db_rule.priority = rule.priority
        db.commit()
        db.refresh(db_rule)
    return db_rule

def delete_routing_rule(db: Session, rule_id: str):
    db_rule = get_routing_rule(db, rule_id)
    if db_rule:
        db.delete(db_rule)
        db.commit()
    return db_rule
