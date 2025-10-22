import pandas as pd
import io
import aiohttp
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from contextlib import asynccontextmanager

# Try to import PandasAI, but make it optional
try:
    from pandasai import SmartDataframe
    from pandasai.llm import OpenAI
    PANDASAI_AVAILABLE = True
except ImportError:
    PANDASAI_AVAILABLE = False


class CSVService:
    """Service for handling CSV uploads and analysis"""
    
    def __init__(self, openai_api_key: Optional[str] = None, max_tokens: int = 500, timeout: int = 30):
        """Initialize CSVService with optional OpenAI API key for PandasAI"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.pandasai_available = PANDASAI_AVAILABLE and self.openai_api_key
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._smart_dfs: Dict[str, Any] = {}  # Cache for SmartDataframes by conversation_id
        self._max_dataframe_size = 10000  # Max rows for PandasAI processing
        
        # Configure logging
        logging.getLogger("pandasai").setLevel(logging.WARNING)
        
        # Simple patterns that don't need PandasAI
        self.simple_patterns = [
            'show', 'preview', 'display', 'head', 'first', 'rows', 'columns',
            'count', 'length', 'size', 'shape', 'info', 'describe', 'stats'
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
            )
        return self._session

    async def close_session(self):
        """Close the aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def load_csv_from_url(self, url: str) -> pd.DataFrame:
        """Load CSV from a URL using session reuse"""
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme in ['http', 'https']:
                raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are supported")

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch CSV: HTTP {response.status}")

                content = await response.read()
                df = pd.read_csv(io.BytesIO(content))
                return df

        except Exception as e:
            raise Exception(f"Error loading CSV from URL: {str(e)}")

    @staticmethod
    def load_csv_from_bytes(data: bytes) -> pd.DataFrame:
        """Load CSV from bytes"""
        try:
            df = pd.read_csv(io.BytesIO(data))
            return df
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")

    @staticmethod
    def get_basic_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }

    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for numeric columns"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_cols:
            return {"message": "No numeric columns found"}

        stats = df[numeric_cols].describe().to_dict()

        return {
            "numeric_columns": numeric_cols,
            "statistics": stats
        }

    @staticmethod
    def get_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
        """Get missing value information"""
        missing = df.isnull().sum()
        missing_percent = (missing / len(df) * 100).round(2)

        missing_data = {
            col: {
                "count": int(missing[col]),
                "percentage": float(missing_percent[col])
            }
            for col in df.columns if missing[col] > 0
        }

        return {
            "total_missing": int(missing.sum()),
            "columns_with_missing": len(missing_data),
            "details": missing_data
        }

    @staticmethod
    def get_column_info(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific column"""
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found")

        col = df[column_name]

        info = {
            "name": column_name,
            "dtype": str(col.dtype),
            "non_null_count": int(col.count()),
            "null_count": int(col.isnull().sum()),
            "unique_values": int(col.nunique())
        }

        if pd.api.types.is_numeric_dtype(col):
            info.update({
                "min": float(col.min()) if not pd.isna(col.min()) else None,
                "max": float(col.max()) if not pd.isna(col.max()) else None,
                "mean": float(col.mean()) if not pd.isna(col.mean()) else None,
                "median": float(col.median()) if not pd.isna(col.median()) else None,
                "std": float(col.std()) if not pd.isna(col.std()) else None
            })
        else:
            # For non-numeric columns, show top values
            top_values = col.value_counts().head(10).to_dict()
            info["top_values"] = {str(k): int(v) for k, v in top_values.items()}

        return info

    @staticmethod
    def get_histogram_data(df: pd.DataFrame, column_name: str, bins: int = 10) -> Dict[str, Any]:
        """Get histogram data for a numeric column"""
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found")

        col = df[column_name].dropna()

        if not pd.api.types.is_numeric_dtype(col):
            raise ValueError(f"Column '{column_name}' is not numeric")

        counts, bin_edges = pd.cut(col, bins=bins, retbins=True, include_lowest=True)
        value_counts = counts.value_counts().sort_index()

        histogram_data = []
        for interval, count in value_counts.items():
            histogram_data.append({
                "range": f"{interval.left:.2f} - {interval.right:.2f}",
                "count": int(count)
            })

        return {
            "column": column_name,
            "bins": bins,
            "data": histogram_data,
            "min": float(col.min()),
            "max": float(col.max())
        }

    @staticmethod
    def get_data_preview(df: pd.DataFrame, n_rows: int = 10) -> Dict[str, Any]:
        """Get a preview of the data"""
        preview = df.head(n_rows).to_dict('records')

        return {
            "rows": len(preview),
            "data": preview
        }

    def _sample_dataframe_if_large(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sample dataframe if it's too large for PandasAI processing"""
        if len(df) > self._max_dataframe_size:
            sampled_df = df.sample(n=self._max_dataframe_size, random_state=42)
            logging.info(f"DataFrame sampled from {len(df)} to {len(sampled_df)} rows for PandasAI processing")
            return sampled_df
        return df

    def create_smart_dataframe(self, df: pd.DataFrame, conversation_id: Optional[str] = None) -> Optional[Any]:
        """Create a SmartDataframe instance for PandasAI queries with caching"""
        if not self.pandasai_available:
            return None
        
        # Use cached SmartDataframe if available
        if conversation_id and conversation_id in self._smart_dfs:
            return self._smart_dfs[conversation_id]
        
        try:
            # Sample dataframe if too large
            processed_df = self._sample_dataframe_if_large(df)
            
            llm = OpenAI(api_token=self.openai_api_key)
            smart_df = SmartDataframe(
                processed_df,
                config={
                    "llm": llm,
                    "max_output_tokens": self.max_tokens,
                    "timeout": self.timeout,
                    "enable_cache": True,
                    "verbose": False
                }
            )
            
            # Cache the SmartDataframe if conversation_id provided
            if conversation_id:
                self._smart_dfs[conversation_id] = smart_df
            
            return smart_df
        except Exception as e:
            logging.error(f"Error creating SmartDataframe: {str(e)}")
            return None

    def _should_use_pandasai(self, query: str) -> bool:
        """Determine if query should use PandasAI based on intent detection"""
        query_lower = query.lower()
        
        # Skip PandasAI for simple patterns
        if any(pattern in query_lower for pattern in self.simple_patterns):
            return False
        
        # Use PandasAI for complex analytical queries
        complex_patterns = [
            'correlation', 'relationship', 'pattern', 'trend', 'outlier',
            'insight', 'analysis', 'why', 'how', 'what if', 'predict',
            'group by', 'aggregate', 'compare', 'difference'
        ]
        
        return any(pattern in query_lower for pattern in complex_patterns)

    def _create_response(self, response_type: str, success: bool, result: Any = None, 
                        message: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized response structure"""
        response = {
            "type": response_type,
            "success": success,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        if result is not None:
            response["result"] = result
        if message:
            response["message"] = message
        if metadata:
            response["metadata"] = metadata
            
        return response

    def query_with_pandasai(self, df: pd.DataFrame, query: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a natural language query using PandasAI"""
        if not self.pandasai_available:
            return self._create_response(
                "error", False, 
                message="PandasAI not available. Please install pandasai and set OPENAI_API_KEY environment variable."
            )
        
        try:
            smart_df = self.create_smart_dataframe(df, conversation_id)
            if smart_df is None:
                return self._create_response(
                    "error", False,
                    message="Failed to create SmartDataframe"
                )
            
            # Execute the query with timeout
            result = asyncio.run(asyncio.wait_for(
                asyncio.to_thread(smart_df.chat, query),
                timeout=self.timeout
            ))
            
            return self._create_response(
                "pandasai_query", True,
                result=str(result),
                metadata={
                    "query": query,
                    "conversation_id": conversation_id,
                    "dataframe_size": len(df),
                    "sampled": len(df) > self._max_dataframe_size
                }
            )
            
        except asyncio.TimeoutError:
            return self._create_response(
                "error", False,
                message=f"Query timeout after {self.timeout} seconds"
            )
        except Exception as e:
            logging.error(f"PandasAI query failed: {str(e)}")
            return self._create_response(
                "error", False,
                message=f"PandasAI query failed: {str(e)}"
            )

    def get_pandasai_insights(self, df: pd.DataFrame, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get AI-powered insights about the dataset"""
        if not self.pandasai_available:
            return self._create_response(
                "error", False,
                message="PandasAI not available. Please install pandasai and set OPENAI_API_KEY environment variable."
            )
        
        insights = []
        
        # Generate various insights
        insight_queries = [
            "What are the main patterns or trends in this dataset?",
            "Are there any outliers or unusual values?",
            "What are the key relationships between columns?",
            "What insights can you provide about the data distribution?",
            "Are there any data quality issues I should be aware of?"
        ]
        
        smart_df = self.create_smart_dataframe(df, conversation_id)
        if not smart_df:
            return self._create_response(
                "error", False,
                message="Failed to create SmartDataframe for insights"
            )
        
        for query in insight_queries:
            try:
                result = asyncio.run(asyncio.wait_for(
                    asyncio.to_thread(smart_df.chat, query),
                    timeout=self.timeout
                ))
                insights.append({
                    "question": query,
                    "answer": str(result)
                })
            except asyncio.TimeoutError:
                insights.append({
                    "question": query,
                    "answer": f"Timeout after {self.timeout} seconds"
                })
            except Exception as e:
                insights.append({
                    "question": query,
                    "answer": f"Error: {str(e)}"
                })
        
        return self._create_response(
            "pandasai_insights", True,
            result={"insights": insights},
            metadata={
                "conversation_id": conversation_id,
                "dataframe_size": len(df),
                "sampled": len(df) > self._max_dataframe_size,
                "total_queries": len(insight_queries)
            }
        )

    def analyze_query(self, df: pd.DataFrame, query: str, use_pandasai: bool = True, 
                     conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a natural language query and return appropriate results
        Uses PandasAI when available and appropriate, falls back to rule-based approach
        """
        # Determine if we should use PandasAI based on intent detection
        should_use_pandasai = use_pandasai and self.pandasai_available and self._should_use_pandasai(query)
        
        # Try PandasAI first if appropriate
        if should_use_pandasai:
            pandasai_result = self.query_with_pandasai(df, query, conversation_id)
            if pandasai_result.get("success", False):
                return pandasai_result
        
        # Fall back to rule-based approach
        query_lower = query.lower()

        # Summarize dataset
        if any(word in query_lower for word in ['summarize', 'summary', 'overview', 'describe']):
            return self._create_response(
                "summary", True,
                result={
                    "basic_info": CSVService.get_basic_info(df),
                    "stats": CSVService.get_summary_stats(df),
                    "missing": CSVService.get_missing_values(df)
                },
                metadata={"method": "rule_based", "query": query}
            )

        # Basic stats
        if any(word in query_lower for word in ['stats', 'statistics', 'statistical']):
            return self._create_response(
                "statistics", True,
                result=CSVService.get_summary_stats(df),
                metadata={"method": "rule_based", "query": query}
            )

        # Missing values
        if any(word in query_lower for word in ['missing', 'null', 'nan', 'empty']):
            return self._create_response(
                "missing_values", True,
                result=CSVService.get_missing_values(df),
                metadata={"method": "rule_based", "query": query}
            )

        # Histogram/distribution
        if any(word in query_lower for word in ['histogram', 'distribution', 'plot']):
            # Try to extract column name
            for col in df.columns:
                if col.lower() in query_lower:
                    try:
                        return self._create_response(
                            "histogram", True,
                            result=CSVService.get_histogram_data(df, col),
                            metadata={"method": "rule_based", "query": query, "column": col}
                        )
                    except ValueError:
                        pass

            return self._create_response(
                "error", False,
                message="Please specify a numeric column for histogram",
                metadata={"method": "rule_based", "query": query}
            )

        # Column info
        for col in df.columns:
            if col.lower() in query_lower:
                return self._create_response(
                    "column_info", True,
                    result=CSVService.get_column_info(df, col),
                    metadata={"method": "rule_based", "query": query, "column": col}
                )

        # Preview data
        if any(word in query_lower for word in ['show', 'preview', 'display', 'head', 'first']):
            return self._create_response(
                "preview", True,
                result=CSVService.get_data_preview(df),
                metadata={"method": "rule_based", "query": query}
            )

        # Default: basic info
        return self._create_response(
            "basic_info", True,
            result=CSVService.get_basic_info(df),
            metadata={"method": "rule_based", "query": query}
        )

    def get_comprehensive_analysis(self, df: pd.DataFrame, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive analysis including both traditional stats and AI insights"""
        analysis = {
            "basic_info": CSVService.get_basic_info(df),
            "summary_stats": CSVService.get_summary_stats(df),
            "missing_values": CSVService.get_missing_values(df),
            "pandasai_available": self.pandasai_available
        }
        
        # Add AI insights if available
        if self.pandasai_available:
            insights_result = self.get_pandasai_insights(df, conversation_id)
            if insights_result.get("success", False):
                analysis["ai_insights"] = insights_result["result"]["insights"]
            else:
                analysis["ai_insights_error"] = insights_result.get("message", "Unknown error")
        
        return analysis

    def clear_cache(self, conversation_id: Optional[str] = None):
        """Clear SmartDataframe cache"""
        if conversation_id:
            if conversation_id in self._smart_dfs:
                del self._smart_dfs[conversation_id]
        else:
            self._smart_dfs.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache state"""
        return {
            "cached_conversations": list(self._smart_dfs.keys()),
            "cache_size": len(self._smart_dfs),
            "max_dataframe_size": self._max_dataframe_size,
            "pandasai_available": self.pandasai_available
        }
