import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.texbid_db
    
    print("=" * 60)
    print("MAKE USER ADMIN")
    print("=" * 60)
    
    # Get all users
    users = await db.users.find({}).to_list(None)
    
    if not users:
        print('\n❌ No users found in database.')
        print('   Please register a user first at: http://localhost:8000/register')
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
        choice = int(input('\n🔢 Enter user number to make admin: ')) - 1
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
    
    # Check if already admin
    if selected_user.get('is_admin') == True:
        print(f'\n✅ {email} is already an admin!')
        client.close()
        return
    
    # Confirm
    confirm = input(f"\n⚠️  Make '{email}' an admin? (yes/no): ").lower()
    if confirm not in ['yes', 'y']:
        print('❌ Cancelled')
        client.close()
        return
    
    # Update user to admin
    result = await db.users.update_one(
        {'id': selected_user['id']},
        {'$set': {'is_admin': True}}
    )
    
    if result.modified_count > 0:
        print(f'\n✅ SUCCESS! {email} is now an admin!')
        print('\n🌐 Admin Panel Access:')
        print('   1. Log out and log back in as this user')
        print('   2. Go to: http://localhost:8000/admin/subscriptions')
        print('   3. Toggle your company to PREMIUM')
        print('   4. Access Reverse Auction!')
    else:
        print(f'❌ Failed to update {email}')
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
