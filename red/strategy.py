from dataclasses import dataclass, field


@dataclass
class StrategyState:
    attack_categories: list
    attacker_model: str
    target_model: str
    mutation_mode: str  # "direct" | "paraphrase" | "chain"
    iteration: int = 0
    successes: list = field(default_factory=list)
    history: list = field(default_factory=list)
