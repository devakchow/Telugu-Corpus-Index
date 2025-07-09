# Telugu Corpus Data Visualizer 

A comprehensive Streamlit-based web application for visualizing and analyzing Telugu literature corpus data with advanced filtering, search capabilities, and interactive data exploration tools.

## Description

The Telugu Corpus Data Visualizer is a powerful analytics tool designed specifically for researchers, linguists, and enthusiasts working with Telugu literature datasets. This application provides an intuitive interface to explore large collections of Telugu literary works, offering insights through interactive visualizations, advanced filtering options, and detailed data analysis capabilities.

### Key Features

- **Interactive Data Visualization**: Time series analysis, distribution charts, and detailed analytics with Plotly
- **Advanced Filtering System**: Multi-level filtering by type, author, publisher, magazine, status, and date ranges
- **Optimized Search**: Cross-field search functionality across titles, authors, types, publishers, and magazines
- **Telugu Text Support**: Optimized rendering for Telugu scripts with proper font support
- **Interactive Data Grid**: Sortable, filterable, and selectable data table with AgGrid integration

### What Makes This Different

- **Telugu-Specific Optimization**: Specially designed for Telugu literature corpus with proper Unicode support
- **Publication Timeline Analysis**: Comprehensive time-based analysis including yearly, monthly, and decade trends
- **Author Productivity Analytics**: Detailed insights into prolific authors and their publication patterns
- **Status Tracking**: Monitor active vs. inactive publications in your corpus

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Required Dependencies

```bash
pip install streamlit pandas st-aggrid numpy plotly
```

### Step-by-Step Installation

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd telugu-corpus-visualizer
   
   # Or download and extract the files to your preferred directory
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install streamlit==1.28.0
   pip install pandas==2.0.3
   pip install st-aggrid==0.3.4
   pip install numpy==1.24.3
   pip install plotly==5.15.0
   ```

3. **Prepare your data file**
   - Place your Telugu corpus CSV file in the same directory as the application
   - Rename it to `sorted_data[1].csv` or use the upload feature avaiable directly upon running the streamlit app

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`

### Data Source Options

**Option 1: Use Existing Data**
- Place your CSV file as `sorted_data[1].csv` in the application directory
- Select "Use Existing Telugu Corpus data" in the interface

**Option 2: Upload Data direclty on the App**
- Select "Upload your own CSV file"
- Use the file uploader to select your Telugu corpus CSV file

### Expected CSV Format

Your CSV file should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| ID | Unique identifier | 1, 2, 3... |
| Title | Title of the work | "రామాయణం", "మహాభారతం" |
| Type | Content type | "కథ", "కవిత", "నవల" |
| Author | Author name | "విశ్వనాథ సత్యనారాయణ" |
| Publisher | Publisher name | "వాణీ ప్రకాశన్" |
| Magazine | Magazine name | "ఆంధ్రజ్యోతి" |
| Published date | Publication date | YYYY-MM-DD format |
| Vol | Volume information | Can be empty |
| Link | Document URL | Web link to document |
| STATUS | Active status | True/False |

### Feature Walkthrough

1. **Data Overview**: View basic statistics including total records, unique authors, publishers, and active status count

2. **Filtering Options** (Sidebar):
   - Filter by content type (కథ, కవిత, etc.)
   - Select specific authors (top 50 most frequent)
   - Filter by publisher or magazine
   - Choose active/inactive status
   - Set year range for publications

3. **Search Functionality**:
   - Enter search terms in the search box
   - Searches across Title, Author, Type, Publisher, and Magazine fields
   - Case-insensitive search with accurate results

4. **Data Visualizations**:
   - **Time Series Analysis**: Publications by year and decade
   - **Distribution Charts**: Content type and publisher distribution
   - **Detailed Analytics**: Top authors and monthly trends

5. **Interactive Data Table**:
   - Sort columns by clicking headers
   - Use column filters for precise data selection
   - Select multiple rows for detailed view
   - Resize columns and customize layout

### Example Usage Scenarios

**Scenario 1: Analyzing Author Productivity**
```
1. Go to "Detailed Analytics" tab
2. View "Top 15 Most Prolific Authors" chart
3. Filter by specific author using sidebar
4. Analyze their publication timeline
```

**Scenario 2: Publisher Market Analysis**
```
1. Navigate to "Distribution Charts" tab
2. View "Distribution by Publisher" pie chart
3. Filter by specific publisher
4. Analyze their publication types and timeline
```

**Scenario 3: Historical Publication Trends**
```
1. Use year range slider in sidebar
2. View "Publications by Year" in Time Series Analysis
3. Analyze trends across different decades
4. Compare with monthly publication trends
```

## Contributing

We welcome contributions from the community! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make your changes
5. Test thoroughly with sample data
6. Submit a pull request

### Contribution Guidelines

- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Test with various data sizes and formats
- Update documentation for new features
- Ensure Telugu text rendering works correctly

### Areas for Contribution

- **Bug Fixes**: Report and fix any issues found
- **New Visualizations**: Add more chart types and analytics
- **Performance Improvements**: Optimize for larger datasets
- **UI/UX Enhancements**: Improve user experience
- **Documentation**: Improve README, add code comments
- **Testing**: Add unit tests and integration tests

## Authors and Acknowledgment

**Built for Viswam.ai**

by Devak & Rishitha

## Special Thanks
We would like to extend our heartfelt gratitude to @ranjithraj, our mentor, for his invaluable guidance and support throughout the development of this project

### Recent Updates
- Enhanced Telugu text rendering
- Improved filtering performance
- Added comprehensive data visualizations
- Optimized for larger datasets

### Getting Involved

We're always looking for contributors! Whether you're interested in:
- Adding new features
- Improving documentation
- Testing with different datasets
- Providing feedback

Feel free to reach out or submit pull requests. This project thrives on community involvement and feedback from Telugu literature researchers and enthusiasts.

---

**Happy Analyzing!**