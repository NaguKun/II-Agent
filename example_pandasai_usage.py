#!/usr/bin/env python3
"""
Example script demonstrating how to use the enhanced CSVService with PandasAI
"""

import pandas as pd
import os
import asyncio
from services.csv_service import CSVService

async def main():
    # Set your OpenAI API key (or set OPENAI_API_KEY environment variable)
    # os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
    
    # Initialize the CSV service with custom settings
    csv_service = CSVService(
        max_tokens=500,
        timeout=30
    )
    
    # Create a sample dataset
    sample_data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry'],
        'age': [25, 30, 35, 28, 32, 27, 29, 31],
        'salary': [50000, 60000, 70000, 55000, 65000, 52000, 58000, 62000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT'],
        'experience_years': [2, 5, 8, 3, 6, 2, 4, 7]
    }
    df = pd.DataFrame(sample_data)
    
    print("=== Sample Dataset ===")
    print(df)
    print()
    
    # Check if PandasAI is available
    print(f"PandasAI Available: {csv_service.pandasai_available}")
    print(f"Cache Info: {csv_service.get_cache_info()}")
    print()
    
    # Test session reuse with URL loading (if you have a CSV URL)
    # async with csv_service:
    #     df_from_url = await csv_service.load_csv_from_url("https://example.com/data.csv")
    
    # Get comprehensive analysis
    print("=== Comprehensive Analysis ===")
    analysis = csv_service.get_comprehensive_analysis(df, conversation_id="demo_session")
    print(f"Basic Info: {analysis['basic_info']}")
    print(f"Summary Stats: {analysis['summary_stats']}")
    print()
    
    # Example queries with different complexity levels
    queries = [
        # Simple queries (will use rule-based)
        "Show me the first 5 rows",
        "What are the column names?",
        "How many rows are there?",
        
        # Complex queries (will use PandasAI if available)
        "What is the correlation between age and salary?",
        "Which department has the highest average salary?",
        "Are there any outliers in the salary data?",
        "What patterns can you find in this dataset?",
        "How does experience relate to salary by department?"
    ]
    
    print("=== Query Examples ===")
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        result = csv_service.analyze_query(df, query, conversation_id="demo_session")
        
        print(f"Type: {result['type']}")
        print(f"Success: {result['success']}")
        print(f"Timestamp: {result['timestamp']}")
        
        if result['success']:
            if result['type'] == 'pandasai_query':
                print(f"AI Response: {result['result']}")
                print(f"Metadata: {result.get('metadata', {})}")
            else:
                print(f"Result: {result['result']}")
                print(f"Method: {result['metadata'].get('method', 'unknown')}")
        else:
            print(f"Error: {result['message']}")
    
    # Get AI insights if available
    if csv_service.pandasai_available:
        print("\n=== AI Insights ===")
        insights_result = csv_service.get_pandasai_insights(df, conversation_id="demo_session")
        if insights_result['success']:
            insights = insights_result['result']['insights']
            for insight in insights:
                print(f"\nQ: {insight['question']}")
                print(f"A: {insight['answer']}")
        else:
            print(f"Error getting insights: {insights_result['message']}")
    else:
        print("\n=== AI Insights ===")
        print("PandasAI not available. Please install pandasai and set OPENAI_API_KEY environment variable.")
    
    # Show cache info
    print(f"\n=== Cache Info ===")
    print(f"Cache Info: {csv_service.get_cache_info()}")
    
    # Clean up
    csv_service.clear_cache("demo_session")
    await csv_service.close_session()
    print("\nSession closed and cache cleared.")

if __name__ == "__main__":
    asyncio.run(main())
