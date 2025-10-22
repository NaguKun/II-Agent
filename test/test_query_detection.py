"""
Test visualization query detection
"""
import asyncio
import pandas as pd
from services.csv_service import CSVService


async def test_queries():
    """Test various user queries"""
    print("=" * 80)
    print("Testing Query Detection for Visualizations")
    print("=" * 80)

    # Create test data
    test_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 75000, 55000, 65000],
        'department': ['HR', 'IT', 'IT', 'Sales', 'HR']
    }
    df = pd.DataFrame(test_data)

    print("\nTest Data:")
    print(df)
    print("\n" + "=" * 80)

    csv_service = CSVService()

    # Test queries
    test_queries = [
        "show me salary distribution",
        "plot age vs salary",
        "visualize the data",
        "create a histogram",
        "plot salary",
        "age vs salary scatter plot",
        "show me a chart",
        "graph the salaries"
    ]

    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Query: '{query}'")
        print("-" * 80)

        result = await csv_service.analyze_query(df, query)

        print(f"Response Type: {result.get('type')}")
        print(f"Success: {result.get('success')}")

        if result.get('type') == 'visualization':
            viz_result = result.get('result', {})
            print(f"Visualization Type: {viz_result.get('type')}")
            print(f"Message: {viz_result.get('message')}")
            if viz_result.get('column'):
                print(f"Column: {viz_result.get('column')}")
            if viz_result.get('x_column') and viz_result.get('y_column'):
                print(f"X Column: {viz_result.get('x_column')}")
                print(f"Y Column: {viz_result.get('y_column')}")
            print(f"Has Image: {bool(viz_result.get('image_data'))}")
        else:
            print(f"Note: Did not generate visualization")

    await csv_service.close_session()

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_queries())
