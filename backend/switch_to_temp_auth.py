#!/usr/bin/env python3
"""
Script to temporarily switch authentication to in-memory storage for testing.
This allows you to test your Flutter app without Firebase configuration.
"""

import shutil
import os

# Paths
backend_dir = "/home/aditya/ai_cybersecurity_project/backend"
users_router_path = os.path.join(backend_dir, "api/routers/users.py")
users_temp_path = os.path.join(backend_dir, "api/routers/users_temp.py")
users_backup_path = os.path.join(backend_dir, "api/routers/users_firebase_backup.py")

def switch_to_temp():
    """Switch to temporary authentication"""
    
    # Backup original Firebase users router
    if os.path.exists(users_router_path):
        print("📁 Backing up original Firebase users router...")
        shutil.copy(users_router_path, users_backup_path)
        print(f"✅ Backup saved to: {users_backup_path}")
    
    # Replace with temporary router
    if os.path.exists(users_temp_path):
        print("🔄 Switching to temporary authentication...")
        shutil.copy(users_temp_path, users_router_path)
        print("✅ Switched to temporary in-memory authentication")
        
        print("\n📧 Test credentials available:")
        print("   Email: admin@cybersec.com")
        print("   Password: admin123")
        print("")
        print("   Email: test@example.com") 
        print("   Password: admin123")
        print("\n🚀 You can now test your Flutter app with these credentials!")
        print("\n⚠️  Note: This is temporary! Users won't persist between restarts.")
    else:
        print(f"❌ Error: {users_temp_path} not found!")

def switch_back():
    """Switch back to Firebase authentication"""
    
    if os.path.exists(users_backup_path):
        print("🔄 Switching back to Firebase authentication...")
        shutil.copy(users_backup_path, users_router_path)
        print("✅ Restored Firebase authentication")
        print("⚠️  Remember to set up proper Firebase credentials!")
    else:
        print(f"❌ Error: Backup file {users_backup_path} not found!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "back":
        switch_back()
    else:
        switch_to_temp()