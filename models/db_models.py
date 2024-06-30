from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class GameStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"

class Week(Base):
    __tablename__ = 'weeks'

    week_number = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)

    stinkers = relationship("Stinker", back_populates="week")

class Stinker(Base):
    __tablename__ = 'stinkers'

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, ForeignKey('weeks.week_number'), nullable=False)  # This now references week_number
    fantasy_team = Column(String, nullable=False)
    stinker_team = Column(String, nullable=False)
    stinker_record = Column(String, nullable=False)
    game_id = Column(Integer, nullable=False)
    game_status = Column(Enum(GameStatus), nullable=False)
    home_team = Column(String, nullable=False)
    home_score = Column(Integer, nullable=False)
    away_team = Column(String, nullable=False)
    away_score = Column(Integer, nullable=False)
    kickoff = Column(String, nullable=False)
    text_line = Column(String, nullable=False)

    week = relationship("Week", back_populates="stinkers")