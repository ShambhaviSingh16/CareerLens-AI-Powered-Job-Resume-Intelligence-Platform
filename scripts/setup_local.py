"""Generate local Compose secrets without printing them or overwriting existing files."""
from pathlib import Path
import secrets

target = Path(__file__).resolve().parents[1] / ".env"
if target.exists():
    raise SystemExit("Root .env already exists; preserved. Check its settings against .env.example.")
target.write_text(
    f"POSTGRES_PASSWORD={secrets.token_urlsafe(24)}\nJWT_SECRET={secrets.token_urlsafe(48)}\n"
    "GROQ_API_KEY=\nGROQ_MODEL=qwen/qwen3.8-27b\nANALYSES_PER_DAY=5\nGLOBAL_ANALYSES_PER_DAY=20\n",
    encoding="utf-8",
)
print("Created ignored root .env. Add a Groq Free-plan key only when you want live analysis.")
