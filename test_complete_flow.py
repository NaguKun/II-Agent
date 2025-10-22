"""
Complete end-to-end test simulating actual API flow
"""
import asyncio
import pandas as pd
from services.csv_service import CSVService
from services.ai_service import AIService
from models import MessageContent, MessageType, MessageRole


async def test_complete_flow():
    """Simulate the complete flow from CSV upload to response"""
    print("=" * 80)
    print("Complete End-to-End Visualization Flow Test")
    print("=" * 80)

    # Create test CSV data
    test_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
        'age': [25, 30, 35, 28, 32, 45, 29, 38, 27, 41],
        'salary': [48000, 60000, 75000, 55000, 65000, 85000, 52000, 70000, 50000, 90000],
        'department': ['HR', 'IT', 'IT', 'Sales', 'HR', 'IT', 'Sales', 'IT', 'HR', 'Sales']
    }
    df = pd.DataFrame(test_data)

    print("\nDataset:")
    print(df.head())
    print(f"\nTotal rows: {len(df)}, Total columns: {len(df.columns)}")
    print("=" * 80)

    # Test Case 1: "show me salary distribution"
    print("\n\n[TEST CASE 1] User asks: 'show me salary distribution'")
    print("-" * 80)

    csv_service = CSVService()
    query1 = "show me salary distribution"

    # Step 1: Analyze query (this is what happens in the router)
    csv_analysis = await csv_service.analyze_query(df, query1, conversation_id="test_conv_1")

    print(f"CSV Analysis Type: {csv_analysis.get('type')}")
    print(f"CSV Analysis Success: {csv_analysis.get('success')}")

    # Check if visualization was generated
    visualization_image = None
    if csv_analysis.get("type") == "visualization" and csv_analysis.get("result", {}).get("image_data"):
        visualization_image = csv_analysis["result"]["image_data"]
        print(f"Visualization Generated: YES")
        print(f"Image Data Length: {len(visualization_image)} characters")
        print(f"Image Preview: {visualization_image[:60]}...")
    else:
        print(f"Visualization Generated: NO")

    # Step 2: Create user message content
    user_content = [
        MessageContent(
            type=MessageType.TEXT,
            text=query1
        ),
        MessageContent(
            type=MessageType.CSV,
            csv_data=csv_analysis
        )
    ]

    print(f"\nUser Message Content Items: {len(user_content)}")
    for i, item in enumerate(user_content):
        print(f"  {i+1}. Type: {item.type}")

    # Step 3: Format for AI (this happens in AIService)
    formatted_messages = []

    # Format user message
    message_content = []
    for content_item in user_content:
        if content_item.type == MessageType.TEXT:
            message_content.append({
                "type": "text",
                "text": content_item.text
            })
        elif content_item.type == MessageType.CSV:
            csv_text = AIService._format_csv_for_context(content_item.csv_data)
            message_content.append({
                "type": "text",
                "text": csv_text
            })

    formatted_messages.append({
        "role": "user",
        "content": message_content
    })

    print(f"\nFormatted Messages for AI: {len(formatted_messages)}")
    print(f"User message has {len(message_content)} content items")

    # Print what AI sees
    print("\n" + "=" * 80)
    print("WHAT THE AI SEES:")
    print("=" * 80)
    for item in message_content:
        print(item["text"][:500])  # First 500 chars
        if len(item["text"]) > 500:
            print("... (truncated)")
    print("=" * 80)

    # Step 4: Check assistant response structure
    print("\n[EXPECTED ASSISTANT RESPONSE]")
    print("-" * 80)
    assistant_content = [
        MessageContent(
            type=MessageType.TEXT,
            text="Based on the visualization, the salary distribution shows..."
        )
    ]

    if visualization_image:
        assistant_content.append(
            MessageContent(
                type=MessageType.IMAGE,
                image_url=visualization_image
            )
        )
        print("Assistant Response Contains:")
        print("  1. Text response")
        print("  2. Visualization image")
    else:
        print("Assistant Response Contains:")
        print("  1. Text response only")
        print("  ⚠️  WARNING: No visualization image!")

    print("\n" + "=" * 80)

    # Test Case 2: "plot age vs salary"
    print("\n\n[TEST CASE 2] User asks: 'plot age vs salary'")
    print("-" * 80)

    query2 = "plot age vs salary"
    csv_analysis2 = await csv_service.analyze_query(df, query2, conversation_id="test_conv_1")

    print(f"CSV Analysis Type: {csv_analysis2.get('type')}")
    print(f"CSV Analysis Success: {csv_analysis2.get('success')}")

    visualization_image2 = None
    if csv_analysis2.get("type") == "visualization" and csv_analysis2.get("result", {}).get("image_data"):
        visualization_image2 = csv_analysis2["result"]["image_data"]
        viz_type = csv_analysis2["result"].get("type")
        x_col = csv_analysis2["result"].get("x_column")
        y_col = csv_analysis2["result"].get("y_column")
        print(f"Visualization Generated: YES")
        print(f"Visualization Type: {viz_type}")
        print(f"X Column: {x_col}")
        print(f"Y Column: {y_col}")
        print(f"Image Data Length: {len(visualization_image2)} characters")
    else:
        print(f"Visualization Generated: NO")

    await csv_service.close_session()

    print("\n" + "=" * 80)
    print("✅ END-TO-END TEST COMPLETE")
    print("=" * 80)

    # Summary
    print("\n[SUMMARY]")
    print("-" * 80)
    if visualization_image and visualization_image2:
        print("✅ Both test cases generated visualizations successfully")
        print("✅ System is working correctly")
        print("\n⚠️  If you're not seeing images in frontend:")
        print("   1. Check that frontend is reading 'assistant_message.content' array")
        print("   2. Look for items with type='image'")
        print("   3. Display the 'image_url' property in an <img> tag")
        print("   4. Check browser console for errors")
    else:
        print("❌ One or both test cases failed to generate visualizations")
        if not visualization_image:
            print("   - Test Case 1 failed")
        if not visualization_image2:
            print("   - Test Case 2 failed")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
