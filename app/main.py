from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from pathlib import Path

from .decrypt_seed import decrypt_seed, load_private_key
from .totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

# Correct unified seed path
SEED_PATH = Path("/data/seed.txt")


# ---------------------------
# Endpoint 1: POST /decrypt-seed
# ---------------------------
class SeedRequest(BaseModel):
    encrypted_seed: str


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: SeedRequest):
    try:
        private_key = load_private_key()
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)

        # Ensure /data directory exists
        SEED_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save seed
        SEED_PATH.write_text(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Endpoint 2: GET /generate-2fa
# ---------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        hex_seed = SEED_PATH.read_text().strip()

        # Generate TOTP code
        code = generate_totp_code(hex_seed)

        # Remaining seconds in current 30-sec period
        current_time = int(time.time())
        valid_for = 30 - (current_time % 30)

        return {"code": code, "valid_for": valid_for}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Endpoint 3: POST /verify-2fa
# ---------------------------
class VerifyRequest(BaseModel):
    code: str


@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):

    if not req.code:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})

    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})

    try:
        seed_hex = SEED_PATH.read_text().strip()
        is_valid = verify_totp_code(seed_hex, req.code, valid_window=1)

        return {"valid": is_valid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
