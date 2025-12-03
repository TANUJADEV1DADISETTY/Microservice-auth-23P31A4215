from totp_utils import generate_totp_code, verify_totp_code

# Put only the raw 64-char hex seed here
hex_seed = "c8ccefa14d0f6b8420c705ff70eaf3cc3d1b75b815b9e1bf82c6232196dfeb99"

# Generate TOTP
current_code = generate_totp_code(hex_seed)
print("Generated TOTP Code:", current_code)

# Verify TOTP
is_valid = verify_totp_code(hex_seed, current_code)
print("Is code valid?", is_valid)
