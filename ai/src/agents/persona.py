from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

PERSONA_PROMPT = (PROMPTS_DIR / "persona.txt").read_text(encoding="utf-8")
