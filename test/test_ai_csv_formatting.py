"""
Test script to verify AI CSV data formatting
"""
import asyncio
import pandas as pd
from services.csv_service import CSVService
from services.ai_service import AIService


async def test_ai_csv_formatting():
    """Test the AI formatting of CSV data"""
    print("Testing AI CSV Data Formatting...")
    print("=" * 70)

    # Create test dataframe
    test_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 75000, 55000, 65000],
        'department': ['HR', 'IT', 'IT', 'Sales', 'HR']
    }
    df = pd.DataFrame(test_data)

    print("\nTest DataFrame:")
    print(df)
    print("\n" + "=" * 70)

    csv_service = CSVService()

    # Test different query types and their formatting
    test_queries = [
        ("show me the data", "preview"),
        ("summarize the dataset", "summary"),
        ("show statistics", "statistics"),
        ("give me basic info", "basic_info"),
    ]

    for query, expected_type in test_queries:
        print(f"\n{'=' * 70}")
        print(f"Testing Query: '{query}'")
        print(f"Expected Type: {expected_type}")
        print("-" * 70)

        # Get CSV analysis
        csv_analysis = await csv_service.analyze_query(df, query)

        print(f"Response Type: {csv_analysis.get('type')}")
        print(f"Success: {csv_analysis.get('success')}")

        # Format for AI context
        formatted_text = AIService._format_csv_for_context(csv_analysis)

        print("\nFormatted Text for AI:")
        print("-" * 70)
        print(formatted_text)
        print("-" * 70)

        # Verify formatting
        if "CSV Data Analysis:" in formatted_text:
            print("[PASS] Contains CSV Data Analysis header")
        else:
            print("[FAIL] Missing CSV Data Analysis header")

        if f"Analysis Type: {csv_analysis.get('type')}" in formatted_text:
            print("[PASS] Contains Analysis Type")
        else:
            print("[FAIL] Missing Analysis Type")

        # Check for actual data
        if len(formatted_text) > 100:
            print("[PASS] Formatted text contains substantial data")
        else:
            print("[FAIL] Formatted text seems too short")

    await csv_service.close_session()

    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_ai_csv_formatting())
