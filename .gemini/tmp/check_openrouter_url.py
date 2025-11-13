from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server_python.database import Base, LLMProvider # Import your models

SQLALCHEMY_DATABASE_URL = "sqlite:///./server_python/sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_openrouter_base_url():
    db = next(get_db())
    openrouter_provider = db.query(LLMProvider).filter(LLMProvider.name == "OpenRouter").first()

    if openrouter_provider:
        print(f"OpenRouter Provider Name: {openrouter_provider.name}")
        print(f"OpenRouter Base URL: {openrouter_provider.base_url}")
    else:
        print("OpenRouter provider not found in the database.")
    
    db.close()

if __name__ == "__main__":
    check_openrouter_base_url()
