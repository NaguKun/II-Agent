"""
Visualization Service for generating plots from CSV data
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Dict, Any, Optional, List
import numpy as np


class VisualizationService:
    """Service for creating data visualizations"""

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10

    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"

    @staticmethod
    def create_histogram(df: pd.DataFrame, column: str, bins: int = 10,
                        title: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a histogram for a numeric column

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            if column not in df.columns:
                return {
                    "success": False,
                    "message": f"Column '{column}' not found in dataset"
                }

            if not pd.api.types.is_numeric_dtype(df[column]):
                return {
                    "success": False,
                    "message": f"Column '{column}' is not numeric"
                }

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot histogram
            data = df[column].dropna()
            n, bins_edges, patches = ax.hist(data, bins=bins, edgecolor='black',
                                             color='steelblue', alpha=0.7)

            # Add labels and title
            ax.set_xlabel(column, fontsize=12, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
            ax.set_title(title or f'Distribution of {column}', fontsize=14, fontweight='bold')

            # Add statistics text
            stats_text = f'Mean: {data.mean():.2f}\nMedian: {data.median():.2f}\nStd: {data.std():.2f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=10)

            # Add grid
            ax.grid(axis='y', alpha=0.3)

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Histogram created for {column}",
                "type": "histogram",
                "column": column
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating histogram: {str(e)}"
            }

    @staticmethod
    def create_bar_chart(df: pd.DataFrame, column: str,
                        title: Optional[str] = None, top_n: int = 20) -> Dict[str, Any]:
        """
        Create a bar chart for categorical column

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            if column not in df.columns:
                return {
                    "success": False,
                    "message": f"Column '{column}' not found in dataset"
                }

            # Get value counts
            value_counts = df[column].value_counts().head(top_n)

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))

            # Plot bar chart
            bars = ax.bar(range(len(value_counts)), value_counts.values,
                          color='steelblue', alpha=0.7, edgecolor='black')

            # Customize
            ax.set_xticks(range(len(value_counts)))
            ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
            ax.set_xlabel(column, fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=12, fontweight='bold')
            ax.set_title(title or f'Distribution of {column}', fontsize=14, fontweight='bold')

            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)

            # Add grid
            ax.grid(axis='y', alpha=0.3)

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Bar chart created for {column}",
                "type": "bar_chart",
                "column": column
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating bar chart: {str(e)}"
            }

    @staticmethod
    def create_scatter_plot(df: pd.DataFrame, x_column: str, y_column: str,
                           title: Optional[str] = None, hue_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a scatter plot between two numeric columns

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            if x_column not in df.columns or y_column not in df.columns:
                return {
                    "success": False,
                    "message": f"Column not found in dataset"
                }

            if not pd.api.types.is_numeric_dtype(df[x_column]) or not pd.api.types.is_numeric_dtype(df[y_column]):
                return {
                    "success": False,
                    "message": "Both columns must be numeric"
                }

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot scatter
            if hue_column and hue_column in df.columns:
                for category in df[hue_column].unique():
                    mask = df[hue_column] == category
                    ax.scatter(df[mask][x_column], df[mask][y_column],
                             label=str(category), alpha=0.6, s=50)
                ax.legend()
            else:
                ax.scatter(df[x_column], df[y_column], color='steelblue',
                          alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

            # Labels and title
            ax.set_xlabel(x_column, fontsize=12, fontweight='bold')
            ax.set_ylabel(y_column, fontsize=12, fontweight='bold')
            ax.set_title(title or f'{y_column} vs {x_column}', fontsize=14, fontweight='bold')

            # Add correlation coefficient
            corr = df[[x_column, y_column]].corr().iloc[0, 1]
            ax.text(0.02, 0.98, f'Correlation: {corr:.3f}', transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            # Grid
            ax.grid(True, alpha=0.3)

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Scatter plot created for {x_column} vs {y_column}",
                "type": "scatter_plot",
                "x_column": x_column,
                "y_column": y_column
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating scatter plot: {str(e)}"
            }

    @staticmethod
    def create_box_plot(df: pd.DataFrame, columns: List[str],
                       title: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a box plot for numeric columns

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            # Validate columns
            numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

            if not numeric_cols:
                return {
                    "success": False,
                    "message": "No valid numeric columns found"
                }

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))

            # Plot box plot
            data_to_plot = [df[col].dropna() for col in numeric_cols]
            bp = ax.boxplot(data_to_plot, labels=numeric_cols, patch_artist=True)

            # Customize colors
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
                patch.set_alpha(0.7)

            # Labels and title
            ax.set_xlabel('Columns', fontsize=12, fontweight='bold')
            ax.set_ylabel('Values', fontsize=12, fontweight='bold')
            ax.set_title(title or 'Box Plot of Numeric Columns', fontsize=14, fontweight='bold')
            ax.set_xticklabels(numeric_cols, rotation=45, ha='right')

            # Grid
            ax.grid(axis='y', alpha=0.3)

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Box plot created for {len(numeric_cols)} columns",
                "type": "box_plot",
                "columns": numeric_cols
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating box plot: {str(e)}"
            }

    @staticmethod
    def create_correlation_heatmap(df: pd.DataFrame,
                                   title: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a correlation heatmap for numeric columns

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            # Get numeric columns
            numeric_df = df.select_dtypes(include=['number'])

            if numeric_df.empty or len(numeric_df.columns) < 2:
                return {
                    "success": False,
                    "message": "Need at least 2 numeric columns for correlation heatmap"
                }

            # Calculate correlation
            corr = numeric_df.corr()

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))

            # Plot heatmap
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                       center=0, square=True, linewidths=1,
                       cbar_kws={"shrink": 0.8}, ax=ax)

            # Title
            ax.set_title(title or 'Correlation Heatmap', fontsize=14, fontweight='bold')

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Correlation heatmap created for {len(numeric_df.columns)} columns",
                "type": "correlation_heatmap",
                "columns": numeric_df.columns.tolist()
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating correlation heatmap: {str(e)}"
            }

    @staticmethod
    def create_line_plot(df: pd.DataFrame, x_column: str, y_columns: List[str],
                        title: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a line plot

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        try:
            if x_column not in df.columns:
                return {
                    "success": False,
                    "message": f"Column '{x_column}' not found"
                }

            # Validate y columns
            valid_y_cols = [col for col in y_columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

            if not valid_y_cols:
                return {
                    "success": False,
                    "message": "No valid numeric y-columns found"
                }

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))

            # Plot lines
            for col in valid_y_cols:
                ax.plot(df[x_column], df[col], marker='o', label=col, linewidth=2)

            # Labels and title
            ax.set_xlabel(x_column, fontsize=12, fontweight='bold')
            ax.set_ylabel('Values', fontsize=12, fontweight='bold')
            ax.set_title(title or f'Line Plot', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Rotate x labels if they're text
            if not pd.api.types.is_numeric_dtype(df[x_column]):
                plt.xticks(rotation=45, ha='right')

            # Convert to base64
            image_data = VisualizationService._fig_to_base64(fig)

            return {
                "success": True,
                "image_data": image_data,
                "message": f"Line plot created",
                "type": "line_plot",
                "x_column": x_column,
                "y_columns": valid_y_cols
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating line plot: {str(e)}"
            }

    @staticmethod
    def auto_visualize(df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """
        Automatically determine the best visualization based on the query and data

        Returns:
            dict with 'success', 'image_data', 'message'
        """
        query_lower = query.lower()

        # Detect visualization type from query
        if any(word in query_lower for word in ['histogram', 'distribution', 'frequency']):
            # Find numeric columns in query
            for col in df.columns:
                if col.lower() in query_lower and pd.api.types.is_numeric_dtype(df[col]):
                    return VisualizationService.create_histogram(df, col)

            # Default to first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                return VisualizationService.create_histogram(df, numeric_cols[0])

        elif any(word in query_lower for word in ['bar', 'count', 'category']):
            # Find categorical columns in query
            for col in df.columns:
                if col.lower() in query_lower:
                    return VisualizationService.create_bar_chart(df, col)

            # Default to first non-numeric column
            categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
            if categorical_cols:
                return VisualizationService.create_bar_chart(df, categorical_cols[0])

        elif any(word in query_lower for word in ['scatter', 'correlation', 'relationship', 'vs', 'versus']):
            # Try to extract column names from query
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            found_cols = []

            for col in numeric_cols:
                if col.lower() in query_lower:
                    found_cols.append(col)

            # If we found 2 columns in the query, use them
            if len(found_cols) >= 2:
                return VisualizationService.create_scatter_plot(df, found_cols[0], found_cols[1])
            # If we found 1 column, use it with the first other numeric column
            elif len(found_cols) == 1 and len(numeric_cols) >= 2:
                other_cols = [c for c in numeric_cols if c != found_cols[0]]
                return VisualizationService.create_scatter_plot(df, found_cols[0], other_cols[0])
            # Default: use first two numeric columns
            elif len(numeric_cols) >= 2:
                return VisualizationService.create_scatter_plot(df, numeric_cols[0], numeric_cols[1])

        elif any(word in query_lower for word in ['box', 'outlier', 'quartile']):
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                return VisualizationService.create_box_plot(df, numeric_cols[:5])  # Max 5 columns

        elif any(word in query_lower for word in ['heatmap', 'correlations']):
            return VisualizationService.create_correlation_heatmap(df)

        # Default: create histogram of first numeric column
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            return VisualizationService.create_histogram(df, numeric_cols[0])

        return {
            "success": False,
            "message": "Could not determine appropriate visualization for the data"
        }
