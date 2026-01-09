#!/usr/bin/env python3
"""
Generate secure admin credentials for analytics dashboard access
Run this script to create username and Argon2-hashed passphrase
"""
import secrets
import sys

try:
    from argon2 import PasswordHasher
except ImportError:
    print("❌ Error: argon2-cffi not installed")
    print("\nInstall it with:")
    print("  pip install argon2-cffi")
    sys.exit(1)


def generate_admin_credentials():
    """Generate secure admin credentials"""
    print("\n" + "="*70)
    print("🔐 Admin Credentials Generator")
    print("="*70)
    print("\nThis will generate secure admin credentials for your analytics dashboard.")
    print("You'll need to add these to your .env file on the Raspberry Pi.\n")

    # Get username
    username = input("Enter admin username (or press Enter for random): ").strip()
    if not username:
        username = f"admin_{secrets.token_hex(4)}"
        print(f"✓ Generated random username: {username}")

    # Get passphrase
    print("\n⚠️  Passphrase Requirements:")
    print("   - Minimum 20 characters")
    print("   - Mix of letters, numbers, symbols recommended")
    print("   - This will be hashed with Argon2\n")

    while True:
        passphrase = input("Enter admin passphrase (min 20 chars): ").strip()
        if len(passphrase) < 20:
            print("❌ Passphrase must be at least 20 characters! Try again.\n")
            continue

        # Confirm passphrase
        confirm = input("Confirm passphrase: ").strip()
        if passphrase != confirm:
            print("❌ Passphrases don't match! Try again.\n")
            continue

        break

    # Hash passphrase with Argon2
    print("\n⏳ Hashing passphrase with Argon2...")
    ph = PasswordHasher()
    passphrase_hash = ph.hash(passphrase)

    # Display results
    print("\n" + "="*70)
    print("✅ Admin Credentials Generated Successfully!")
    print("="*70)
    print(f"\n📌 Username: {username}")
    print(f"📌 Passphrase Hash:\n{passphrase_hash}\n")

    print("⚠️  IMPORTANT - SAVE THESE SECURELY!")
    print("="*70)
    print("\n📝 Add to .env file on Raspberry Pi:")
    print("-" * 70)
    print(f"ADMIN_USERNAME={username}")
    print(f"ADMIN_PASSPHRASE_HASH={passphrase_hash}")
    print("-" * 70)

    print("\n📝 Optional: Add IP allowlist (your home/office IP):")
    print("-" * 70)
    print("ADMIN_IP_ALLOWLIST=192.168.1.100,203.0.113.5")
    print("-" * 70)

    print("\n🔧 Deployment Steps:")
    print("1. SSH into Raspberry Pi:")
    print("   ssh malsi123@your-raspberry-pi-ip")
    print("\n2. Edit .env file:")
    print("   nano ~/PRA/.env")
    print("\n3. Add the ADMIN_USERNAME and ADMIN_PASSPHRASE_HASH lines above")
    print("\n4. Restart the app:")
    print("   docker restart pra-app")
    print("\n5. Visit: https://skincares.work/admin/login")
    print(f"   Username: {username}")
    print(f"   Passphrase: [the one you entered]")

    print("\n" + "="*70)
    print("✨ Setup complete! Keep these credentials safe.")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        generate_admin_credentials()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
