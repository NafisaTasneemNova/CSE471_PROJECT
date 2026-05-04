import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (same as backend)."""
    return hashlib.sha256(password.encode()).hexdigest()

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.texbid_db
    
    print("=" * 60)
    print("RESET USER PASSWORD (SHA-256 - Correct Method)")
    print("=" * 60)
    
    # Get all users
    users = await db.users.find({}).to_list(None)
    
    if not users:
        print('\n❌ No users found in database.')
        client.close()
        return
    
    print('\n📋 Available users:')
    for i, user in enumerate(users, 1):
        email = user.get('email', 'N/A')
        is_admin = user.get('is_admin', False)
        status = '👑 ADMIN' if is_admin else '👤 Regular'
        print(f'  {i}. {email} - {status}')
    
    # Get user choice
    try:
        choice = int(input('\n🔢 Enter user number to reset password: ')) - 1
        if choice < 0 or choice >= len(users):
            print('❌ Invalid choice')
            client.close()
            return
    except ValueError:
        print('❌ Please enter a valid number')
        client.close()
        return
    
    selected_user = users[choice]
    email = selected_user.get('email', 'Unknown')
    
    # Get new password
    new_password = input(f'\n🔒 Enter NEW password for {email}: ').strip()
    
    if len(new_password) < 6:
        print('❌ Password must be at least 6 characters')
        client.close()
        return
    
    # Confirm password
    confirm_password = input('🔒 Confirm NEW password: ').strip()
    
    if new_password != confirm_password:
        print('❌ Passwords do not match!')
        client.close()
        return
    
    # Hash the password using SHA-256 (same as backend)
    password_hash = hash_password(new_password)
    
    print(f'\n🔐 Password hash: {password_hash[:20]}...')
    
    # Update password in database with correct field name
    result = await db.users.update_one(
        {'id': selected_user['id']},
        {'$set': {'password_hash': password_hash}}
    )
    
    if result.modified_count > 0:
        print(f'\n✅ SUCCESS! Password reset for {email}')
        print('\n📋 NEW LOGIN CREDENTIALS:')
        print(f'   Email: {email}')
        print(f'   Password: {new_password}')
        print('\n🌐 LOGIN:')
        print('   Go to: http://localhost:8000/login')
        print(f'   Email: {email}')
        print(f'   Password: {new_password}')
        print('\n⚠️  IMPORTANT: Use the REGULAR login page, not admin login!')
        print('   Regular login: http://localhost:8000/login')
        print('   NOT: http://localhost:8000/admin/login')
        print('\n🔧 NEXT STEPS:')
        print('   1. Go to: http://localhost:8000/login')
        print('   2. Log in with the credentials above')
        print('   3. Go to: http://localhost:8000/admin/subscriptions')
        print('   4. Toggle your company to PREMIUM')
        print('   5. Access Reverse Auction!')
    else:
        print(f'\n⚠️  No changes made. Password might already be set.')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
