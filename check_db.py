import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import settings

async def check_database():
    # Connect to MongoDB using settings from .env
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    print("=" * 80)
    print("MongoDB CONNECTION STATUS: SUCCESSFUL")
    print("=" * 80)

    # Check conversations collection
    conversations = db["conversations"]
    conv_count = await conversations.count_documents({})

    print(f"\nCONVERSATIONS COLLECTION:")
    print(f"   Total documents: {conv_count}")
    print("-" * 80)

    async for conv in conversations.find():
        print(f"\n   Conversation ID: {conv['_id']}")
        print(f"   Title: {conv['title']}")
        print(f"   Created: {conv['created_at']}")
        print(f"   Updated: {conv['updated_at']}")
        print(f"   Message Count: {conv['message_count']}")

    # Check messages collection
    messages = db["messages"]
    msg_count = await messages.count_documents({})

    print(f"\n\nMESSAGES COLLECTION:")
    print(f"   Total documents: {msg_count}")
    print("-" * 80)

    async for msg in messages.find().sort("timestamp", 1):
        print(f"\n   Message ID: {msg['_id']}")
        print(f"   Conversation: {msg['conversation_id']}")
        print(f"   Role: {msg['role'].upper()}")
        print(f"   Timestamp: {msg['timestamp']}")
        print(f"   Content Items: {len(msg['content'])}")

        for i, content in enumerate(msg['content'], 1):
            content_type = content['type']
            print(f"      [{i}] Type: {content_type}")

            if content_type == 'text' and content.get('text'):
                text_preview = content['text'][:100] + "..." if len(content['text']) > 100 else content['text']
                print(f"          Text: {text_preview}")

            elif content_type == 'csv' and content.get('csv_data'):
                csv_info = content['csv_data'].get('basic_info', {})
                print(f"          CSV: {csv_info.get('rows', 'N/A')} rows × {csv_info.get('columns', 'N/A')} columns")
                if 'column_names' in csv_info:
                    print(f"          Columns: {', '.join(csv_info['column_names'])}")

            elif content_type == 'image':
                print(f"          Image: [Base64 data present]")

    print("\n" + "=" * 80)
    print("DATABASE CHECK COMPLETE")
    print("=" * 80)

    client.close()

if __name__ == "__main__":
    asyncio.run(check_database())
