from rosa_reliability.prompt_contract import BoundedPromptROSA
from experiments.macro_transfer_v1.inference import LiveROSA


class RepairedROSA(BoundedPromptROSA, LiveROSA):
    """Change prompt construction only; retain existing gates and termination."""
