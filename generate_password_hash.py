#!/usr/bin/env python3
"""
Password Hash Generator for Railway Deployment
Use this to generate secure password hashes for your dashboard users
"""

import hashlib
import getpass

def generate_hash(password):
    """Generate SHA256 hash for password"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("🔐 Password Hash Generator for RBC Dashboard")
    print("=" * 50)
    
    print("\n📝 Default credentials (for reference):")
    print("Admin - Username: admin, Password: admin123")
    print("Hash:", generate_hash("admin123"))
    print("\nViewer - Username: viewer, Password: viewer123") 
    print("Hash:", generate_hash("viewer123"))
    
    print("\n🔒 Generate new secure password hashes:")
    print("(Press Enter to skip a user)")
    
    # User 1 (Admin)
    print("\n👤 User 1 (Admin):")
    username1 = input("Username (default: admin): ").strip() or "admin"
    password1 = getpass.getpass("Password: ").strip()
    
    if password1:
        hash1 = generate_hash(password1)
        print(f"✅ Generated hash for {username1}")
    else:
        print("⏭️ Skipped User 1")
        username1 = hash1 = None
    
    # User 2 (Viewer)
    print("\n👤 User 2 (Viewer):")
    username2 = input("Username (default: viewer): ").strip() or "viewer"
    password2 = getpass.getpass("Password: ").strip()
    
    if password2:
        hash2 = generate_hash(password2)
        print(f"✅ Generated hash for {username2}")
    else:
        print("⏭️ Skipped User 2")
        username2 = hash2 = None
    
    # Output environment variables
    print("\n🚂 Railway Environment Variables:")
    print("=" * 40)
    
    if username1 and hash1:
        print(f"USER1_USERNAME={username1}")
        print(f"USER1_PASSWORD_HASH={hash1}")
    
    if username2 and hash2:
        print(f"USER2_USERNAME={username2}")
        print(f"USER2_PASSWORD_HASH={hash2}")
    
    print("\nENVIRONMENT=production")
    
    print("\n📋 Instructions:")
    print("1. Copy the environment variables above")
    print("2. In Railway dashboard → Variables tab")
    print("3. Add each variable with its value")
    print("4. Deploy your application")
    
    print("\n🔐 Security Notes:")
    print("• Never share these hashes publicly")
    print("• Use strong passwords (12+ characters)")
    print("• Consider using a password manager")

if __name__ == "__main__":
    main()