"""
Configuração do SQLAlchemy com Supabase/PostgreSQL.
Fornece engine, sessão e dependência do FastAPI.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # reconecta automaticamente se a conexão cair
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os modelos."""
    pass


def get_db():
    """Dependência FastAPI que entrega e fecha a sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
