import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Telugu Corpus Data Visualizer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Telugu text rendering and styling
st.markdown("""
<style>
    .telugu-text {
        font-family: 'Noto Sans Telugu', 'Peddana', 'Mallanna', Arial, sans-serif;
        font-size: 16px;
    }
    .main-header {
        background: linear-gradient(90deg, #1F51FF 0%, #000000 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stats-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .search-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .fullscreen-btn {
        background: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    }
    .fullscreen-btn:hover {
        background: #0056b3;
    }
    .ag-theme-streamlit {
        font-family: 'Noto Sans Telugu', 'Peddana', 'Mallanna', Arial, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Centered Header with Gradient Styling
st.markdown("""
<div class="main-header" style="text-align: center;">
    <h1>తెలుగు Corpus Data Visualizer</h1>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'fullscreen_mode' not in st.session_state:
    st.session_state.fullscreen_mode = False
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None

# File upload section
# Data source selection
# Data source selection
st.markdown("### Data Source")
data_source = st.radio(
    "Choose your data source:",
    ["Use Existing Telugu Corpus data", "Upload your own CSV file"],
    horizontal=True
)

uploaded_file = None
existing_file_path = None

if data_source == "Upload your own CSV file":
    uploaded_file = st.file_uploader(
        "Upload your Telugu corpus CSV file",
        type=['csv'],
        help="Upload the sorted_data.csv file containing Telugu corpus information"
    )
else:
    existing_file_path = "sorted_data[1].csv"  # Replace with your actual CSV filename
    try:
        # Test if file exists and is readable
        test_df = pd.read_csv(existing_file_path)
        st.info(f"Using Existing Telugu corpus data ({len(test_df):,} records)")
        del test_df  # Clean up memory
    except FileNotFoundError:
        st.error(f"Existing Corpus data file '{existing_file_path}' not found in the current directory.")
        existing_file_path = None
    except Exception as e:
        st.error(f"Error reading existing Telugu corpus data file: {str(e)}")
        existing_file_path = None

if uploaded_file is not None or existing_file_path is not None:
    try:
        # Load the data
        # Load the data
        with st.spinner("Loading data..."):
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_csv("sorted_data[1].csv")
        
        # Data validation and preprocessing
        st.success(f"Data loaded successfully! Found {len(df):,} records with {len(df.columns)} columns.")
        
        # Display basic statistics
        st.markdown("### Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        with col2:
            st.metric("Unique Authors", f"{df['Author'].nunique():,}")
        with col3:
            st.metric("Unique Publishers", f"{df['Publisher'].nunique():,}")
        with col4:
            st.metric("Active Status", f"{df['STATUS'].sum():,}")
        
        # Data preprocessing for better display
        df_display = df.copy()
        
        # Handle missing values in Vol column
        df_display['Vol'] = df_display['Vol'].fillna('N/A')
        
        # Convert Published date to datetime for better sorting
        try:
            df_display['Published date'] = pd.to_datetime(df_display['Published date'])
            df_display['Year'] = df_display['Published date'].dt.year
            df_display['Month'] = df_display['Published date'].dt.month
            df_display['Decade'] = (df_display['Year'] // 10) * 10
        except:
            st.warning("Some dates could not be parsed. Displaying as original format.")
            df_display['Year'] = 'N/A'
            df_display['Month'] = 'N/A'
            df_display['Decade'] = 'N/A'
        
        # Sidebar filters
        st.sidebar.header("Filter Options")
        
        # Reset filters button
        if st.sidebar.button("Reset All Filters"):
            st.session_state.search_query = ""
            st.rerun()
        
        # Type filter
        types = ['All'] + sorted(df['Type'].unique().tolist())
        selected_type = st.sidebar.selectbox("Filter by Type", types, key="type_filter")
        
        # Author filter (top 50 most frequent authors)
        top_authors = df['Author'].value_counts().head(50).index.tolist()
        authors = ['All'] + top_authors
        selected_author = st.sidebar.selectbox("Filter by Author (Top 50)", authors, key="author_filter")
        
        # Publisher filter
        publishers = ['All'] + sorted(df['Publisher'].unique().tolist())
        selected_publisher = st.sidebar.selectbox("Filter by Publisher", publishers, key="publisher_filter")
        
        # Magazine filter
        magazines = ['All'] + sorted(df['Magazine'].unique().tolist())
        selected_magazine = st.sidebar.selectbox("Filter by Magazine", magazines, key="magazine_filter")
        
        # Status filter
        status_options = ['All', 'Active (True)', 'Inactive (False)']
        selected_status = st.sidebar.selectbox("Filter by Status", status_options, key="status_filter")
        
        # Year range filter (if dates are available)
        year_range = None
        if 'Year' in df_display.columns and df_display['Year'].dtype != 'object':
            min_year = int(df_display['Year'].min())
            max_year = int(df_display['Year'].max())
            year_range = st.sidebar.slider(
                "Filter by Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                key="year_filter"
            )
        
        # Apply filters
        filtered_df = df_display.copy()
        
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['Type'] == selected_type]
        
        if selected_author != 'All':
            filtered_df = filtered_df[filtered_df['Author'] == selected_author]
        
        if selected_publisher != 'All':
            filtered_df = filtered_df[filtered_df['Publisher'] == selected_publisher]
        
        if selected_magazine != 'All':
            filtered_df = filtered_df[filtered_df['Magazine'] == selected_magazine]
        
        if selected_status == 'Active (True)':
            filtered_df = filtered_df[filtered_df['STATUS'] == True]
        elif selected_status == 'Inactive (False)':
            filtered_df = filtered_df[filtered_df['STATUS'] == False]
        
        # Apply year filter if available
        if year_range and 'Year' in filtered_df.columns and filtered_df['Year'].dtype != 'object':
            filtered_df = filtered_df[
                (filtered_df['Year'] >= year_range[0]) & 
                (filtered_df['Year'] <= year_range[1])
            ]
        
        # Store filtered data in session state
        st.session_state.filtered_df = filtered_df
        
        # Apply search filter
        if st.session_state.search_query:
            search_mask = (
                filtered_df['Title'].str.contains(st.session_state.search_query, case=False, na=False) |
                filtered_df['Author'].str.contains(st.session_state.search_query, case=False, na=False) |
                filtered_df['Type'].str.contains(st.session_state.search_query, case=False, na=False) |
                filtered_df['Publisher'].str.contains(st.session_state.search_query, case=False, na=False) |
                filtered_df['Magazine'].str.contains(st.session_state.search_query, case=False, na=False)
            )
            filtered_df = filtered_df[search_mask]
        
        # Display filtered results count
        st.markdown(f"### Filtered Results: {len(filtered_df):,} records")
        
        # Data Visualization Section
        if len(filtered_df) > 0 and 'Year' in filtered_df.columns and filtered_df['Year'].dtype != 'object':
            st.markdown("### Data Visualizations")
            
            # Create tabs for different visualizations
            viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Time Series Analysis", "Distribution Charts", "Detailed Analytics"])
            
            with viz_tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Publications by Year (Bar Chart)
                    yearly_data = filtered_df.groupby('Year').size().reset_index(name='Count')
                    fig_yearly = px.bar(
                        yearly_data, 
                        x='Year', 
                        y='Count',
                        title='Publications by Year',
                        labels={'Count': 'Number of Publications', 'Year': 'Publication Year'},
                        color='Count',
                        color_continuous_scale='blues'
                    )
                    fig_yearly.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_yearly, use_container_width=True)
                
                with col2:
                    # Publications by Decade (Line Chart)
                    decade_data = filtered_df.groupby('Decade').size().reset_index(name='Count')
                    fig_decade = px.line(
                        decade_data, 
                        x='Decade', 
                        y='Count',
                        title='Publications by Decade',
                        labels={'Count': 'Number of Publications', 'Decade': 'Decade'},
                        markers=True
                    )
                    fig_decade.update_layout(height=400)
                    st.plotly_chart(fig_decade, use_container_width=True)
            
            with viz_tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Type Distribution (Pie Chart)
                    type_data = filtered_df['Type'].value_counts().head(10)
                    fig_type = px.pie(
                        values=type_data.values,
                        names=type_data.index,
                        title='Distribution by Content Type (Top 10)',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_type.update_layout(height=400)
                    st.plotly_chart(fig_type, use_container_width=True)
                
                with col2:
                    # Publisher Distribution (Pie Chart)
                    publisher_data = filtered_df['Publisher'].value_counts().head(8)
                    fig_publisher = px.pie(
                        values=publisher_data.values,
                        names=publisher_data.index,
                        title='Distribution by Publisher (Top 8)',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_publisher.update_layout(height=400)
                    st.plotly_chart(fig_publisher, use_container_width=True)
            
            with viz_tab3:
                # Top Authors by Publication Count
                author_data = filtered_df['Author'].value_counts().head(15)
                fig_authors = px.bar(
                    x=author_data.values,
                    y=author_data.index,
                    orientation='h',
                    title='Top 15 Most Prolific Authors',
                    labels={'x': 'Number of Publications', 'y': 'Author'},
                    color=author_data.values,
                    color_continuous_scale='viridis'
                )
                fig_authors.update_layout(height=600, showlegend=False)
                st.plotly_chart(fig_authors, use_container_width=True)
                
                # Monthly Publication Trends (if enough data)
                if len(filtered_df) > 100:
                    monthly_data = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Count')
                    monthly_data['Date'] = pd.to_datetime(monthly_data[['Year', 'Month']].assign(day=1))
                    
                    fig_monthly = px.line(
                        monthly_data, 
                        x='Date', 
                        y='Count',
                        title='Monthly Publication Trends',
                        labels={'Count': 'Number of Publications', 'Date': 'Publication Date'}
                    )
                    fig_monthly.update_layout(height=400)
                    st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Search functionality
        st.markdown("### Search and Filter Data")
        
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_query = st.text_input(
                "Search across Title, Author, Type, Publisher, or Magazine",
                value=st.session_state.search_query,
                placeholder="Enter search terms...",
                help="Search is case-insensitive and searches across multiple fields"
            )
        
        with search_col2:
            if st.button("Search", type="primary"):
                st.session_state.search_query = search_query
                st.rerun()
            
            if st.button("Clear Search"):
                st.session_state.search_query = ""
                st.rerun()
        
        # Update search query in session state
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.rerun()
        
        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        
        # Configure column properties
        gb.configure_column("ID", width=80, type=["numericColumn"], precision=0, pinned='left')
        gb.configure_column("Title", width=250, wrapText=True, autoHeight=True)
        gb.configure_column("Type", width=100, filter=True)
        gb.configure_column("Author", width=200, wrapText=True, autoHeight=True)
        gb.configure_column("Publisher", width=130, filter=True)
        gb.configure_column("Magazine", width=130, filter=True)
        gb.configure_column("Published date", width=120, type=["dateColumnFilter"])
        gb.configure_column("Vol", width=100)
        gb.configure_column("Link", width=100, cellRenderer="""
            function(params) {
                if (params.value) {
                    return '<a href="' + params.value + '" target="_blank" style="color: #007bff; text-decoration: none;">📄 View</a>';
                }
                return '';
            }
        """)
        gb.configure_column("STATUS", width=90, type=["booleanColumn"])
        
        # Hide helper columns
        if 'Year' in filtered_df.columns:
            gb.configure_column("Year", hide=True)
        if 'Month' in filtered_df.columns:
            gb.configure_column("Month", hide=True)
        if 'Decade' in filtered_df.columns:
            gb.configure_column("Decade", hide=True)
        
        # Configure grid options
        gb.configure_default_column(
            groupable=True,
            value=True,
            enableRowGroup=True,
            aggFunc="count",
            editable=False,
            filter=True,
            sortable=True,
            resizable=True
        )
        
        gb.configure_pagination(paginationAutoPageSize=True, paginationPageSize=50)
        gb.configure_side_bar()
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        
        # Enable filtering and sorting
        gb.configure_grid_options(
            enableFilter=True,
            enableSorting=True,
            enableColResize=True,
            enableRangeSelection=True,
            domLayout='normal',
            suppressMenuHide=False,
            animateRows=True,
            enableBrowserTooltips=True
        )
        
        gridOptions = gb.build()
        
        # Display the grid
        st.markdown("###  Interactive Data Table")
        
        # Grid display options
        grid_col1, grid_col2, grid_col3 = st.columns([2, 1, 1])
        
        with grid_col1:
            st.markdown(f"**Showing {len(filtered_df):,} records**")
        
        with grid_col2:
            fit_columns = st.checkbox("Fit columns to width", value=True)
        
        with grid_col3:
            if st.button("Expand/Minimize"):
                st.session_state.fullscreen_mode = not st.session_state.fullscreen_mode
                st.rerun()
        
        # Calculate dynamic height
        if st.session_state.fullscreen_mode:
            grid_height = 800
        else:
            grid_height = min(max(len(filtered_df) * 35, 400), 600)
        
        # Display AgGrid
        grid_response = AgGrid(
            filtered_df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=fit_columns,
            enable_enterprise_modules=True,
            height=grid_height,
            width='100%',
            reload_data=True,
            theme='streamlit',
            key='main_grid'
        )
        
        # Display selection info
        if grid_response and 'selected_rows' in grid_response and grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
            st.markdown("### 🎯 Selected Records")
            selected_df = pd.DataFrame(grid_response['selected_rows'])
            st.write(f"Selected {len(selected_df)} record(s)")
            
            # Show selected records in a compact format
            for idx, row in selected_df.iterrows():
                with st.expander(f"📖 {row['Title']} - {row['Author']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {row['Type']}")
                        st.write(f"**Publisher:** {row['Publisher']}")
                        st.write(f"**Magazine:** {row['Magazine']}")
                    with col2:
                        st.write(f"**Published:** {row['Published date']}")
                        st.write(f"**Volume:** {row['Vol']}")
                        st.write(f"**Status:** {'Active' if row['STATUS'] else 'Inactive'}")
                    if row['Link']:
                        st.markdown(f"[📄 View Document]({row['Link']})")
        
        # Export functionality
        st.markdown("### Export Options(Coming Soon...)")
        export_col1, export_col2, export_col3 = st.columns(3)
        
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure your CSV file has the correct format with columns: ID, Title, Type, Author, Publisher, Magazine, Published date, Vol, Link, STATUS")

else:
    if data_source=="Upload your own CSV file":
        st.info("Please upload your Telugu corpus CSV file to get started.")
    else:
        st.info("Existing Telugu corpus data could not be loaded. Please ensure the file exists in the current directory.")
    
    # Show expected file format
    st.markdown("### Expected CSV Format")
    st.markdown("""
    Your CSV file should contain the following columns:
    - **ID**: Unique identifier (integer)
    - **Title**: Title of the work (Telugu text)
    - **Type**: Type of content (e.g., కథ, కవిత, etc.)
    - **Author**: Author name (Telugu text)
    - **Publisher**: Publisher name
    - **Magazine**: Magazine name
    - **Published date**: Publication date (YYYY-MM-DD format)
    - **Vol**: Volume information (can be empty)
    - **Link**: URL to the document
    - **STATUS**: Boolean (True/False)
    """)
    
    # Sample data preview
    st.markdown("### Sample Visualizations")
    st.info("Upload your data to see interactive charts including time series analysis, distribution charts, and detailed analytics.")

# Footer
st.markdown("---")
st.markdown("**Built for Viswam.ai** by Devak & Rishitha")
