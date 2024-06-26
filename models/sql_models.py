from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class FantasyTeam(Base):
    __tablename__ = 'fantasy_teams'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    weekly_picks = relationship("WeeklyPick", back_populates="fantasy_team")

class WeeklyPick(Base):
    __tablename__ = 'weekly_picks'

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, index=True)
    fantasy_team_id = Column(Integer, ForeignKey('fantasy_teams.id'))
    fantasy_team = relationship("FantasyTeam", back_populates="weekly_picks")
    stinker = relationship("Stinker", uselist=False, back_populates="weekly_pick")
    game_info = relationship("GameInfo", uselist=False, back_populates="weekly_pick")
    text_line = Column(String)
    result_line = Column(String)

class Stinker(Base):
    __tablename__ = 'stinkers'

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String)
    record = Column(String)
    weekly_pick_id = Column(Integer, ForeignKey('weekly_picks.id'))
    weekly_pick = relationship("WeeklyPick", back_populates="stinker")

class GameInfo(Base):
    __tablename__ = 'game_info'

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer)
    home_team = Column(String)
    home_score = Column(Integer)
    away_team = Column(String)
    away_score = Column(Integer)
    kickoff = Column(String)
    game_over = Column(Boolean, default=False)
    weekly_pick_id = Column(Integer, ForeignKey('weekly_picks.id'))
    weekly_pick = relationship("WeeklyPick", back_populates="game_info")