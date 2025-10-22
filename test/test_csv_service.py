"""
Test script to verify CSV service fixes
"""
import asyncio
import pandas as pd
from services.csv_service import CSVService


async def test_csv_service():
    """Test the CSVService with basic operations"""
    print("Testing CSV Service...")
    print("-" * 50)

    # Create test dataframe
    test_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David'],
        'age': [25, 30, 35, 28],
        'salary': [50000, 60000, 75000, 55000],
        'department': ['HR', 'IT', 'IT', 'Sales']
    }
    df = pd.DataFrame(test_data)

    print("Test DataFrame created:")
    print(df)
    print("\n")

    # Test 1: Static methods (should work without instance)
    print("Test 1: Static methods")
    print("-" * 50)
    basic_info = CSVService.get_basic_info(df)
    print(f"Basic Info: {basic_info}")
    print("\n")

    # Test 2: Instance method with query
    print("Test 2: Instance method - analyze_query")
    print("-" * 50)
    csv_service = CSVService()

    # Test simple query
    result = await csv_service.analyze_query(df, "show me the data")
    print(f"Query Result Type: {result.get('type')}")
    print(f"Success: {result.get('success')}")
    print(f"Method: {result.get('metadata', {}).get('method')}")
    print("\n")

    # Test summary query
    result2 = await csv_service.analyze_query(df, "summarize the dataset")
    print(f"Summary Result Type: {result2.get('type')}")
    print(f"Success: {result2.get('success')}")
    print("\n")

    # Test 3: Load from bytes
    print("Test 3: Load CSV from bytes")
    print("-" * 50)
    csv_string = df.to_csv(index=False)
    csv_bytes = csv_string.encode('utf-8')
    df_loaded = CSVService.load_csv_from_bytes(csv_bytes)
    print(f"Loaded DataFrame shape: {df_loaded.shape}")
    print(f"Columns: {df_loaded.columns.tolist()}")
    print("\n")

    # Test 4: Close session properly
    print("Test 4: Session cleanup")
    print("-" * 50)
    await csv_service.close_session()
    print("Session closed successfully")
    print("\n")

    # Test 5: Context manager usage
    print("Test 5: Context manager usage")
    print("-" * 50)
    async with CSVService() as csv_service2:
        result3 = await csv_service2.analyze_query(df, "show statistics")
        print(f"Context Manager Result Type: {result3.get('type')}")
        print(f"Success: {result3.get('success')}")
    print("Context manager exited successfully")
    print("\n")

    print("=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_csv_service())
