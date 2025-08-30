from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class Role(str, Enum):
    VILLAGER = "Villager"
    WEREWOLF = "Werewolf"
    FORTUNE_TELLER = "FortuneTeller"


class Team(str, Enum):
    VILLAGERS = "Villagers"
    WEREWOLVES = "Werewolves"


class Phase(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class ModerationAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    REDACT = "redact"
    VETO = "veto"


@dataclass
class PlayerState:
    name: str
    role: Role
    alive: bool = True
    notes: str = ""
    private_knowledge: Dict[str, Any] = field(default_factory=dict)
    llm_id: Optional[str] = None
    
    @property
    def team(self) -> Team:
        if self.role == Role.WEREWOLF:
            return Team.WEREWOLVES
        return Team.VILLAGERS


@dataclass
class ModerationResult:
    action: ModerationAction
    reason: str
    redacted_text: Optional[str] = None


@dataclass
class Message:
    speaker: str
    phase: Phase
    public_text: str
    private_thoughts: str
    moderation: ModerationResult


@dataclass
class Vote:
    voter: str
    target: Optional[str] = None  # None means abstain


@dataclass
class LeaderboardEntry:
    player: str
    suspicion: float


@dataclass
class Leaderboard:
    scores: List[LeaderboardEntry]
    top_guess: Optional[str] = None


@dataclass
class GameEvent:
    type: str  # 'message', 'vote', 'event'
    payload: Any


@dataclass
class GameLog:
    config: Any  # GameConfig
    players: List[PlayerState]
    timeline: List[GameEvent]
    leaderboard_snapshots: List[Dict[str, Any]]