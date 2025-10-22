"""
Test script to verify visualization functionality
"""
import asyncio
import pandas as pd
from services.csv_service import CSVService
from services.visualization_service import VisualizationService
from services.ai_service import AIService
import os


async def test_visualizations():
    """Test the visualization service with various plot types"""
    print("=" * 80)
    print("Testing Visualization Service")
    print("=" * 80)

    # Create test dataframe with salary data
    test_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
        'age': [25, 30, 35, 28, 32, 45, 29, 38, 27, 41],
        'salary': [48000, 60000, 75000, 55000, 65000, 85000, 52000, 70000, 50000, 90000],
        'department': ['HR', 'IT', 'IT', 'Sales', 'HR', 'IT', 'Sales', 'IT', 'HR', 'Sales']
    }
    df = pd.DataFrame(test_data)

    print("\nTest DataFrame:")
    print(df)
    print("\n" + "=" * 80)

    # Test 1: Histogram
    print("\n[TEST 1] Creating Histogram for Salary")
    print("-" * 80)
    result = VisualizationService.create_histogram(df, 'salary', bins=10)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Image data length: {len(result['image_data'])} characters")
        print(f"Image starts with: {result['image_data'][:50]}...")
    print()

    # Test 2: Bar Chart
    print("[TEST 2] Creating Bar Chart for Department")
    print("-" * 80)
    result = VisualizationService.create_bar_chart(df, 'department')
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Image data length: {len(result['image_data'])} characters")
    print()

    # Test 3: Scatter Plot
    print("[TEST 3] Creating Scatter Plot (Age vs Salary)")
    print("-" * 80)
    result = VisualizationService.create_scatter_plot(df, 'age', 'salary', hue_column='department')
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Image data length: {len(result['image_data'])} characters")
    print()

    # Test 4: Box Plot
    print("[TEST 4] Creating Box Plot")
    print("-" * 80)
    result = VisualizationService.create_box_plot(df, ['age', 'salary'])
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Image data length: {len(result['image_data'])} characters")
    print()

    # Test 5: Correlation Heatmap
    print("[TEST 5] Creating Correlation Heatmap")
    print("-" * 80)
    result = VisualizationService.create_correlation_heatmap(df)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Image data length: {len(result['image_data'])} characters")
    print()

    # Test 6: Auto Visualize
    print("[TEST 6] Auto Visualize with Natural Language Query")
    print("-" * 80)
    queries = [
        "show me salary distribution",
        "visualize department counts",
        "plot age vs salary",
        "show me a heatmap"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        result = VisualizationService.auto_visualize(df, query)
        print(f"  Success: {result['success']}")
        print(f"  Type: {result.get('type', 'N/A')}")
        print(f"  Message: {result['message']}")

    print("\n" + "=" * 80)

    # Test 7: Integration with CSVService
    print("\n[TEST 7] Integration with CSVService")
    print("-" * 80)
    csv_service = CSVService()

    visualization_queries = [
        "show me salary histogram",
        "plot salary distribution",
        "visualize the data"
    ]

    for query in visualization_queries:
        print(f"\nQuery: '{query}'")
        result = await csv_service.analyze_query(df, query)
        print(f"  Response Type: {result.get('type')}")
        print(f"  Success: {result.get('success')}")
        if result.get('type') == 'visualization':
            print(f"  Visualization Type: {result['result'].get('type')}")
            print(f"  Has Image Data: {bool(result['result'].get('image_data'))}")

    await csv_service.close_session()
    print("\n" + "=" * 80)

    # Test 8: AI Service Formatting
    print("\n[TEST 8] AI Service Formatting of Visualization Data")
    print("-" * 80)

    # Create a visualization
    viz_result = VisualizationService.create_histogram(df, 'salary')

    # Wrap it in CSVService response format
    csv_response = {
        "type": "visualization",
        "success": True,
        "result": viz_result,
        "metadata": {
            "method": "visualization",
            "query": "show me salary distribution"
        }
    }

    # Format for AI
    formatted_text = AIService._format_csv_for_context(csv_response)
    print("Formatted text for AI:")
    print(formatted_text)

    # Check if it contains key information
    checks = [
        ("CSV Data Analysis:", "CSV Data Analysis header"),
        ("Analysis Type: visualization", "Visualization type"),
        ("image has been generated", "Image generation notice")
    ]

    print("\nValidation:")
    for check_text, description in checks:
        if check_text in formatted_text:
            print(f"  [PASS] Contains {description}")
        else:
            print(f"  [FAIL] Missing {description}")

    print("\n" + "=" * 80)
    print("All Tests Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_visualizations())
