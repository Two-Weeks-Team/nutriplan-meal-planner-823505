import json
import os
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))

if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

connect_args = {}
if not DATABASE_URL.startswith("sqlite"):
    lower_url = DATABASE_URL.lower()
    if "localhost" not in lower_url and "127.0.0.1" not in lower_url:
        connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class NPProfile(Base):
    __tablename__ = "np_profiles"

    id = Integer
    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    name = __import__("sqlalchemy").Column(String(120), nullable=False)
    weight_kg = __import__("sqlalchemy").Column(Float, nullable=False)
    activity_level = __import__("sqlalchemy").Column(String(40), nullable=False)
    goal = __import__("sqlalchemy").Column(String(40), nullable=False)
    dietary_style = __import__("sqlalchemy").Column(String(80), nullable=False, default="balanced")
    restrictions_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    plans = relationship("NPPlan", back_populates="profile", cascade="all, delete-orphan")


class NPPlan(Base):
    __tablename__ = "np_plans"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    profile_id = __import__("sqlalchemy").Column(Integer, ForeignKey("np_profiles.id"), nullable=True)
    name = __import__("sqlalchemy").Column(String(160), nullable=False)
    days = __import__("sqlalchemy").Column(Integer, nullable=False, default=3)
    summary = __import__("sqlalchemy").Column(Text, nullable=False, default="")
    score = __import__("sqlalchemy").Column(Float, nullable=False, default=0.0)
    target_calories = __import__("sqlalchemy").Column(Integer, nullable=False, default=2000)
    target_protein_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=120)
    target_carbs_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=220)
    target_fats_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=67)
    explainer = __import__("sqlalchemy").Column(Text, nullable=False, default="")
    grocery_json = __import__("sqlalchemy").Column(Text, nullable=False, default="{}")
    is_template = __import__("sqlalchemy").Column(Boolean, nullable=False, default=False)
    updated_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("NPProfile", back_populates="plans")
    meals = relationship("NPMeal", back_populates="plan", cascade="all, delete-orphan")


class NPMeal(Base):
    __tablename__ = "np_meals"

    id = __import__("sqlalchemy").Column(Integer, primary_key=True, index=True)
    plan_id = __import__("sqlalchemy").Column(Integer, ForeignKey("np_plans.id"), nullable=False)
    day_index = __import__("sqlalchemy").Column(Integer, nullable=False, default=1)
    slot = __import__("sqlalchemy").Column(String(40), nullable=False)
    title = __import__("sqlalchemy").Column(String(160), nullable=False)
    prep_minutes = __import__("sqlalchemy").Column(Integer, nullable=False, default=15)
    calories = __import__("sqlalchemy").Column(Integer, nullable=False, default=400)
    protein_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=25)
    carbs_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=40)
    fats_g = __import__("sqlalchemy").Column(Integer, nullable=False, default=12)
    ingredients_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    pantry_tags_json = __import__("sqlalchemy").Column(Text, nullable=False, default="[]")
    created_at = __import__("sqlalchemy").Column(DateTime, default=datetime.utcnow, nullable=False)

    plan = relationship("NPPlan", back_populates="meals")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(NPProfile).count() > 0:
            return

        seeds = [
            {
                "name": "Ava Chen",
                "weight_kg": 68.0,
                "activity_level": "moderate",
                "goal": "fat_loss",
                "dietary_style": "high_protein",
                "restrictions": [],
            },
            {
                "name": "Marcus Reed",
                "weight_kg": 82.0,
                "activity_level": "high",
                "goal": "muscle_gain",
                "dietary_style": "balanced",
                "restrictions": ["lactose-free"],
            },
            {
                "name": "Priya Nair",
                "weight_kg": 59.0,
                "activity_level": "light",
                "goal": "maintenance",
                "dietary_style": "vegetarian",
                "restrictions": ["vegetarian"],
            },
        ]

        for s in seeds:
            db.add(
                NPProfile(
                    name=s["name"],
                    weight_kg=s["weight_kg"],
                    activity_level=s["activity_level"],
                    goal=s["goal"],
                    dietary_style=s["dietary_style"],
                    restrictions_json=json.dumps(s["restrictions"]),
                )
            )
        db.commit()

        template1 = NPPlan(
            name="7-day High Protein Cut Plan",
            days=7,
            summary="High-protein cut template with five meals/day.",
            score=92.0,
            target_calories=1950,
            target_protein_g=165,
            target_carbs_g=170,
            target_fats_g=60,
            explainer="Protein prioritized for satiety and lean-mass retention.",
            grocery_json=json.dumps({"protein": ["chicken breast", "eggs"], "produce": ["spinach", "berries"]}),
            is_template=True,
        )
        template2 = NPPlan(
            name="3-day Vegetarian Reset Plan",
            days=3,
            summary="Vegetarian reset with balanced macros and simple prep.",
            score=89.0,
            target_calories=1850,
            target_protein_g=95,
            target_carbs_g=230,
            target_fats_g=62,
            explainer="Balanced macro split with plant-forward protein sources.",
            grocery_json=json.dumps({"protein": ["tofu", "greek yogurt"], "grains": ["quinoa", "oats"]}),
            is_template=True,
        )
        db.add(template1)
        db.add(template2)
        db.commit()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    _seed_if_empty()
