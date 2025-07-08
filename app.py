import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import altair as alt
from matplotlib.font_manager import FontProperties

# Load Telugu font if available
telugu_font_path = None
for f in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    if "notosanstelugu" in f.lower():
        telugu_font_path = f
        break
telugu_font = FontProperties(fname=telugu_font_path) if telugu_font_path else None
if telugu_font:
    plt.rcParams['font.family'] = telugu_font.get_name()

st.set_page_config(page_title="📚 Telugu Literature Dashboard", layout="wide")
st.title("📚 Telugu Literature Dashboard")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def find_column(possible_names, columns):
    for name in columns:
        if name.strip().lower() in [n.lower() for n in possible_names]:
            return name
    return None

uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)

    # Detect important columns
    title_col = find_column(["Title", "Book Title", "Work"], df.columns)
    author_col = find_column(["Author", "Writer"], df.columns)
    date_col = find_column(["Published date", "Publish date", "Date Published"], df.columns)
    magazine_col = find_column(["Magazine", "Journal", "Publication"], df.columns)
    status_col = find_column(["STATUS", "Status"], df.columns)
    type_col = find_column(["Type", "Category", "Genre"], df.columns)

    # Rename for uniform usage
    df = df.rename(columns={
        title_col: "Title",
        author_col: "Author",
        date_col: "Published date",
        magazine_col: "Magazine",
        status_col: "STATUS",
        type_col: "Type"
    })

    # Handle dates and extract year
    if "Published date" in df.columns:
        df["Published date"] = pd.to_datetime(df["Published date"], errors='coerce')
        df['published_year'] = df["Published date"].dt.year

    df['Type'] = df['Type'].astype(str).str.strip()

    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    start = st.sidebar.number_input("Start Row", min_value=0, max_value=len(df)-1, value=0)
    end = st.sidebar.number_input("End Row", min_value=start+1, max_value=len(df), value=min(len(df), 1000))
    df_range = df.iloc[start:end]

    years = sorted(df['published_year'].dropna().unique())
    selected_year = st.sidebar.selectbox("🗕️ Year", years)
    types = df['Type'].dropna().unique().tolist()
    mags = df['Magazine'].dropna().unique().tolist()
    statuses = df['STATUS'].dropna().unique().tolist()

    selected_types = st.sidebar.multiselect("📂 Type", types, default=types)
    selected_mags = st.sidebar.multiselect("🕴️ Magazine", mags, default=mags)
    selected_statuses = st.sidebar.multiselect("📌 Status", statuses, default=statuses)

    # Filtered Data
    filtered_df = df[
        (df['published_year'] == selected_year) &
        (df['Type'].isin(selected_types)) &
        (df['Magazine'].isin(selected_mags)) &
        (df['STATUS'].isin(selected_statuses))
    ]

    # Preview selected rows
    st.subheader(f"🔍 Previewing Rows {start} to {end}")
    st.dataframe(df_range, use_container_width=True, column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="Open")
    })

    # Author counts for selected year
    st.subheader(f"👤 Unique Title Counts by Author in {selected_year}")
    author_counts = (
        filtered_df.groupby("Author")["Title"].nunique()
        .reset_index().rename(columns={"Title": "Unique Titles"})
        .sort_values(by="Unique Titles", ascending=False)
    )
    st.dataframe(author_counts, use_container_width=True)

    # Author selection based on selected year authors
    st.subheader("📘 Author Overview")
    author_list = author_counts["Author"].tolist()
    selected_author = st.selectbox("Choose an Author", options=author_list, format_func=lambda x: x)

    author_df = df[df["Author"] == selected_author]
    author_year_df = author_df[author_df['published_year'] == selected_year]
    total_titles = author_df["Title"].count()
    unique_titles = author_df["Title"].nunique()
    duplicate_titles = total_titles - unique_titles
    year_titles = author_year_df["Title"].nunique()

    st.subheader("📊 Title Summary for Selected Author")
    summary_df = pd.DataFrame({
        "Author": [selected_author],
        "Total Titles": [total_titles],
        "Unique Titles": [unique_titles],
        "Duplicate Titles": [duplicate_titles]
    })
    st.dataframe(summary_df, use_container_width=True)

    st.markdown(f"📚 **{selected_author}** has published **{unique_titles} unique titles** across all years.")
    st.markdown(f"📅 In **{selected_year}**, they published **{year_titles} unique title(s)**.")

    # Duplicates
    duplicate_titles_list = author_df["Title"].value_counts()
    duplicate_titles_list = duplicate_titles_list[duplicate_titles_list > 1]
    duplicate_count = duplicate_titles_list.sum() - len(duplicate_titles_list)
    st.markdown(f"🔁 Found **{duplicate_count} duplicate entries**, where the same title appears multiple times.")

    if not duplicate_titles_list.empty:
        st.markdown("#### 📌 Duplicate Titles by Count")
        st.dataframe(duplicate_titles_list.reset_index().rename(columns={"index": "Title", "Title": "Count"}), use_container_width=True)

    # Titles by author
    st.markdown("### 📄 Titles by Author")
    st.dataframe(
        author_df[["Title", "Published date", "Magazine", "STATUS", "Link"]],
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("Link", display_text="Open")}
    )

    # Yearly title chart
    if "Published date" in author_df.columns:
        author_df["Year"] = author_df["Published date"].dt.year
        available_years = sorted(author_df["Year"].dropna().unique())
        selected_years = st.multiselect("📊 Select Years to Visualize", available_years, default=available_years)
        year_data = author_df[author_df["Year"].isin(selected_years)]
        year_count = year_data.groupby("Year")["Title"].nunique().reset_index()

        st.markdown("#### 📈 Unique Titles Published Over Selected Years")
        fig, ax = plt.subplots()
        sns.barplot(data=year_count, x="Year", y="Title", ax=ax)
        if telugu_font:
            ax.set_title(f"{selected_author} - Publications Over Time", fontproperties=telugu_font)
            for label in ax.get_xticklabels():
                label.set_fontproperties(telugu_font)
        for container in ax.containers:
            ax.bar_label(container)
        st.pyplot(fig)

    # Type-wise breakdown
    type_counts = author_df["Type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    st.markdown("#### 📚 Type-wise Breakdown (Total Entries, including duplicates)")
    st.caption("Note: If a title appears in multiple issues or magazines, it is counted more than once.")
    fig, ax = plt.subplots()
    sns.barplot(data=type_counts, x="Type", y="Count", ax=ax)
    if telugu_font:
        for label in ax.get_xticklabels():
            label.set_fontproperties(telugu_font)
    for container in ax.containers:
        ax.bar_label(container)
    st.pyplot(fig)

    # Publication timeline
    st.markdown("#### ⏳ Publication Timeline")
    st.caption("Each row = one appearance of a title. Filter by type, magazine, status.")
    timeline_df = author_df[
        (author_df["Type"].isin(selected_types)) &
        (author_df["Magazine"].isin(selected_mags)) &
        (author_df["STATUS"].isin(selected_statuses))
    ]
    timeline_df = timeline_df.dropna(subset=["Published date"])

    if not timeline_df.empty:
        chart = alt.Chart(timeline_df).mark_bar().encode(
            x=alt.X('yearmonth(Published date):T', title='Publication Date'),
            y=alt.Y('Title:N', sort='-x', title='Title'),
            color=alt.Color('Magazine:N'),
            tooltip=['Title', 'Magazine', 'Type', 'STATUS', 'Published date']
        ).properties(
            width=800,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No publication data available for the selected filters.")
else:
    st.info("📂 Upload a CSV file to begin.")














