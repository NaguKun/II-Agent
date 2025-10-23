"""
Test script to verify CSV URL loading functionality
"""
import asyncio
import sys
from services.csv_service import CSVService

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test_csv_url():
    """Test loading CSV from a GitHub raw URL"""

    # Example GitHub raw CSV URL (Iris dataset)
    test_url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"

    print(f"Testing CSV URL loading with: {test_url}\n")

    csv_service = CSVService()

    try:
        # Load CSV from URL
        print("Loading CSV from URL...")
        df = await csv_service.load_csv_from_url(test_url)

        print(f"[SUCCESS] Successfully loaded CSV!")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Column names: {list(df.columns)}\n")

        # Get basic info
        print("Getting basic info...")
        basic_info = CSVService.get_basic_info(df)
        print(f"[SUCCESS] Basic info:")
        print(f"  Rows: {basic_info['rows']}")
        print(f"  Columns: {basic_info['columns']}\n")

        # Get data preview
        print("Getting data preview...")
        preview = CSVService.get_data_preview(df)
        print(f"[SUCCESS] First 5 rows:")
        if 'data' in preview:
            print(preview['data'][:2])  # Print first 2 rows
            print("  ...\n")
        else:
            print(f"  Preview: {preview}\n")

        print("[PASS] All tests passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await csv_service.close_session()

if __name__ == "__main__":
    asyncio.run(test_csv_url())
