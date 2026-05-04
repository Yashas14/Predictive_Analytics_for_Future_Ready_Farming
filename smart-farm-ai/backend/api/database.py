"""SQLite persistence for prediction history."""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.utils.config import settings

Base = declarative_base()


class PredictionRecord(Base):
    """One row per prediction — stores inputs, outputs, and SHAP data."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Inputs
    farm_area = Column(Float)
    temp_obs = Column(Float)
    wind_direction = Column(Float)
    dew_temp = Column(Float)
    pressure_sea_level = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    unix_sec = Column(Integer)
    ingredient_type = Column(Integer)
    farming_company = Column(Integer)
    deidentified_location = Column(Integer)
    num_processing_plants = Column(Integer)
    
    # Outputs
    predicted_yield = Column(Float)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    yield_category = Column(String)
    
    # Extra
    model_version = Column(String)
    shap_values = Column(JSON, nullable=True)
    recommendation = Column(String, nullable=True)


# Database setup
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create tables if they don't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a DB session, auto-close when done (FastAPI Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
