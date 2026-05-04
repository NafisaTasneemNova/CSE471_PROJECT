import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.texbid_db
    
    print("=" * 60)
    print("VERIFY PASSWORD")
    print("=" * 60)
    
    # Get email
    email = input('\n📧 Enter email: ').strip()
    
    # Find user
    user = await db.users.find_one({'email': email})
    
    if not user:
        print(f'\n❌ User not found: {email}')
        client.close()
        return
    
    print(f'\n✅ User found: {email}')
    print(f'   Admin: {"YES" if user.get("is_admin") else "NO"}')
    
    # Get password to test
    password = input('\n🔒 Enter password to verify: ').strip()
    
    # Verify password
    hashed_password = user.get('hashed_password', '')
    
    if pwd_context.verify(password, hashed_password):
        print('\n✅ PASSWORD IS CORRECT!')
        print('\n🌐 You can log in with:')
        print(f'   Email: {email}')
        print(f'   Password: {password}')
        print('\n   Go to: http://localhost:8000/login')
    else:
        print('\n❌ PASSWORD IS INCORRECT!')
        print('\n💡 To reset your password, run:')
        print('   python reset_password.py')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
