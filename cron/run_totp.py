import time
from pathlib import Path
from app.totp_utils import generate_totp_code

seed_path = Path("/data/seed.txt")
log_path = Path("/cron/last_code.txt")

if not seed_path.exists():
    log_path.write_text("Seed file missing\n")
    exit()

hex_seed = seed_path.read_text().strip()
code = generate_totp_code(hex_seed)

timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

with open("/cron/last_code.txt", "w") as f:
    f.write(f"{timestamp} - 2FA Code: {code}\n")
