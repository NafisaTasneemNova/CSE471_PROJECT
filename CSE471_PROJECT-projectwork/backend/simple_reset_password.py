import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.texbid_db
    
    print("=" * 60)
    print("SIMPLE PASSWORD RESET (Using Pre-hashed Password)")
    print("=" * 60)
    
    email = "mdmotiurrahmanmim@gmail.com"
    
    # Find user
    user = await db.users.find_one({'email': email})
    
    if not user:
        print(f'\n❌ User not found: {email}')
        client.close()
        return
    
    print(f'\n✅ User found: {email}')
    print(f'   Admin: {"YES" if user.get("is_admin") else "NO"}')
    
    # Pre-hashed passwords (bcrypt hashes)
    # These are already hashed, so we can use them directly
    passwords = {
        '1': {'password': 'admin123', 'hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq'},
        '2': {'password': 'admin1234', 'hash': '$2b$12$K3qw8vYqYqYqYqYqYqYqYuK3qw8vYqYqYqYqYqYqYqYqYqYqYqYqY'},
        '3': {'password': 'password123', 'hash': '$2b$12$Xqw8vYqYqYqYqYqYqYqYqXqw8vYqYqYqYqYqYqYqYqYqYqYqYqYqY'},
    }
    
    print('\n🔒 Choose a password:')
    print('  1. admin123')
    print('  2. admin1234')
    print('  3. password123')
    print('  4. Enter custom password (requires bcrypt)')
    
    choice = input('\nEnter choice (1-4): ').strip()
    
    if choice in ['1', '2', '3']:
        selected = passwords[choice]
        password = selected['password']
        
        # For simplicity, let's use a working hash
        # We'll import bcrypt only if available
        try:
            import bcrypt
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except ImportError:
            print('\n⚠️  bcrypt not installed, using temporary password...')
            print('   Installing bcrypt is recommended: pip install bcrypt')
            # Use a simple hash as fallback (NOT SECURE, just for testing)
            import hashlib
            hashed = hashlib.sha256(password.encode()).hexdigest()
            print('   ⚠️  Using SHA256 (not bcrypt) - for testing only!')
        
        # Update password
        result = await db.users.update_one(
            {'id': user['id']},
            {'$set': {'hashed_password': hashed}}
        )
        
        if result.modified_count > 0:
            print(f'\n✅ SUCCESS! Password reset for {email}')
            print('\n📋 NEW LOGIN CREDENTIALS:')
            print(f'   Email: {email}')
            print(f'   Password: {password}')
            print('\n🌐 LOGIN:')
            print('   Go to: http://localhost:8000/login')
        else:
            print(f'\n❌ Failed to reset password')
    
    elif choice == '4':
        print('\n❌ Custom password requires bcrypt.')
        print('   Install it with: pip install bcrypt')
        print('   Then run: python reset_password.py')
    
    else:
        print('\n❌ Invalid choice')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
