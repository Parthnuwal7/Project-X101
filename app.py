# streamlit_app.py - Streamlit user interface
import streamlit as st
from charts import ChartGenerator
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="NLP Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generator' not in st.session_state:
        st.session_state.generator = ChartGenerator()
    if 'chart_request' not in st.session_state:
        st.session_state.chart_request = ""
    if 'show_code' not in st.session_state:
        st.session_state.show_code = False

def main():
    initialize_session_state()
    
    # Sidebar - Data Upload
    st.sidebar.header("📂 Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your data file (CSV or Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Supported formats: CSV, Excel (XLSX, XLS)"
    )
    
    if uploaded_file is not None:
        try:
            st.session_state.generator.load_data_from_upload(uploaded_file)
            st.sidebar.success("Data loaded successfully!")
            
            # Show data preview
            st.sidebar.subheader("🔍 Data Preview")
            st.sidebar.dataframe(st.session_state.generator.get_data_preview())
            
            # Show column information
            st.sidebar.subheader("📋 Column Information")
            for col, info in st.session_state.generator.get_column_info().items():
                st.sidebar.text(f"{col}: {info['dtype']} (numeric: {info['numeric']})")
                
        except ValueError as e:
            st.sidebar.error(str(e))
    
    # Main content area
    st.title("📊 NLP Chart Generator")
    st.markdown("""
    Describe the chart you want in natural language, and we'll generate it automatically!
    *Example: "Show me a bar chart of sales by region"*
    """)
    
    # Chart request input
    st.session_state.chart_request = st.text_input(
        "Describe your chart:",
        value=st.session_state.chart_request,
        placeholder="e.g., 'Show sales by region as a bar chart'",
        help="Be as specific or general as you like"
    )
    
    # Generate chart button
    if st.button("Generate Chart") and st.session_state.chart_request:
        if not hasattr(st.session_state, 'generator') or st.session_state.generator.data is None:
            st.error("Please upload a data file first!")
        else:
            with st.spinner("✨ Creating your visualization..."):
                try:
                    fig = st.session_state.generator.generate_chart(st.session_state.chart_request)
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.error("Failed to generate chart. Please try a different description.")
                except Exception as e:
                    st.error(f"Error generating chart: {str(e)}")
    
    # Show generated code checkbox
    st.session_state.show_code = st.checkbox(
        "Show generated Python code",
        value=st.session_state.show_code,
        help="View the code used to generate the chart"
    )
    
    if st.session_state.show_code and st.session_state.chart_request:
        try:
            chart_type = st.session_state.generator.determine_chart_type(st.session_state.chart_request)
            code = st.session_state.generator.generate_chart_code(chart_type, st.session_state.chart_request)
            st.code(code, language='python')
        except Exception as e:
            st.error(f"Couldn't show code: {str(e)}")

if __name__ == "__main__":
    main()