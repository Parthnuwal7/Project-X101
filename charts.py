# chart_logic.py - Core business logic
import pandas as pd
from typing import Dict, Tuple, Optional
import re
import matplotlib.pyplot as plt

class ChartGenerator:
    def __init__(self):
        self.data = None
        self.column_info = {}
        
    def load_data(self, file_path: str) -> bool:
        """Load data from file path (CSV/Excel)"""
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                self.data = pd.read_excel(file_path)
            self._analyze_columns()
            return True
        except Exception as e:
            raise ValueError(f"Error loading file: {e}")
        
    def load_data_from_upload(self, uploaded_file) -> bool:
        """Load data from Streamlit file uploader object"""
        try:
            if uploaded_file.name.endswith('.csv'):
                self.data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                self.data = pd.read_excel(uploaded_file)
            self._analyze_columns()
            return True
        except Exception as e:
            raise ValueError(f"Error loading file: {e}")
    
    def _analyze_columns(self):
        """Analyze column types and sample values"""
        self.column_info = {}
        for col in self.data.columns:
            self.column_info[col] = {
                'dtype': str(self.data[col].dtype),
                'sample': self.data[col].iloc[0] if len(self.data) > 0 else None,
                'numeric': pd.api.types.is_numeric_dtype(self.data[col])
            }
    
    def get_column_info(self) -> Dict:
        """Return analyzed column information"""
        return self.column_info
    
    def get_data_preview(self, n_rows: int = 5) -> pd.DataFrame:
        """Return a preview of the data"""
        return self.data.head(n_rows)
    
    def determine_chart_type(self, request: str) -> str:
        """Identify chart type from natural language"""
        request = request.lower()
        if re.search(r'\bpie\b', request):
            return 'pie'
        elif re.search(r'\b(bar|column)\b', request):
            return 'bar'
        elif re.search(r'\b(line|trend)\b', request):
            return 'line'
        elif re.search(r'\b(scatter|point)\b', request):
            return 'scatter'
        elif re.search(r'\b(histogram|distribution)\b', request):
            return 'histogram'
        else:
            return 'bar'  # default
    
    def extract_columns(self, request: str) -> Tuple[str, Optional[str]]:
        """Extract relevant columns from the request"""
        # Look for column names in the request
        found_cols = [col for col in self.data.columns 
                     if re.search(r'\b' + re.escape(col.lower()) + r'\b', request.lower())]
        
        # Default logic if columns not mentioned
        if len(found_cols) >= 2:
            return found_cols[0], found_cols[1]
        elif len(found_cols) == 1:
            numeric_cols = [col for col in self.data.columns if self.column_info[col]['numeric']]
            return found_cols[0], numeric_cols[0] if numeric_cols else found_cols[0]
        else:
            numeric_cols = [col for col in self.data.columns if self.column_info[col]['numeric']]
            if len(numeric_cols) >= 2:
                return self.data.columns[0], numeric_cols[0]
            return (self.data.columns[0], 
                   self.data.columns[1] if len(self.data.columns) > 1 else self.data.columns[0])
    
    def generate_chart_code(self, chart_type: str, request: str) -> str:
        """Generate Python visualization code without return statement"""
        x_col, y_col = self.extract_columns(request)
    
        templates = {
        'bar': """
fig, ax = plt.subplots(figsize=(10,6))
ax.bar(data['{x}'], data['{y}'])
ax.set_title('{title}')
ax.set_xlabel('{x_label}')
ax.set_ylabel('{y_label}')
plt.xticks(rotation=45)
plt.tight_layout()
# Removed the return statement
""".strip(),
        'pie': """
fig, ax = plt.subplots(figsize=(8,8))
data.groupby('{x}')['{y}'].sum().plot.pie(autopct='%1.1f%%', ax=ax)
ax.set_title('{title}')
ax.set_ylabel('')
# Removed the return statement
""".strip(),
        'line': """
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(data['{x}'], data['{y}'])
ax.set_title('{title}')
ax.set_xlabel('{x_label}')
ax.set_ylabel('{y_label}')
ax.grid(True)
# Removed the return statement
""".strip()
    }
    
        return templates[chart_type].format(
            x=x_col,
            y=y_col,
            title=request,
            x_label=x_col,
            y_label=y_col
        )
    
    def generate_chart(self, request: str):
        """Generate and return a matplotlib figure"""
        if self.data is None:
            raise ValueError("No data loaded. Please load data first.")
            
        chart_type = self.determine_chart_type(request)
        code = self.generate_chart_code(chart_type, request)
        
        local_vars = {'data': self.data, 'plt': plt}
        exec(code, globals(), local_vars)
        
        # Get the figure from local variables instead of returning it from the code
        return local_vars.get('fig', None)