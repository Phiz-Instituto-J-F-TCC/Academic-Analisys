from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

PERSONA_PROMPT = (PROMPTS_DIR / "Persona.md").read_text(encoding="utf-8")
