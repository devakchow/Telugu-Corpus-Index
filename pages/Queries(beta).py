import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title=" Dataset Q&A", layout="wide")
st.title(" Dataset Q&A")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("sorted_data[1].csv")
    df['Published date'] = pd.to_datetime(df['Published date'], errors='coerce')
    return df

df = load_data()

# Questions mapped to logic
questions = {
    # 🔹 Author-based
    "Who wrote the most stories?": lambda df: f"🖋️ Most stories written by: **{df['Author'].value_counts().idxmax()}**",
    "Top 10 authors by number of works": lambda df: df['Author'].value_counts().head(10).reset_index().rename(columns={"index": "Author", "Author": "Count"}),
    "Top 5 authors who published poems (కవితలు)": lambda df: df[df['Type'].str.contains("కవిత", na=False)]['Author'].value_counts().head(5).reset_index().rename(columns={"index": "Author", "Author": "Poems"}),
    "Which authors published in more than 5 magazines?": lambda df: df.groupby('Author')['Magazine'].nunique().reset_index(name='Magazines').query("Magazines > 5"),
    "Top 10 authors?": lambda df: df['Author'].value_counts().head(10).reset_index().rename(columns={"index": "Author", "Author": "Count"}),

    # 🔹 Type-based
    "Which content type is most common?": lambda df: f"📚 Most common type is: **{df['Type'].value_counts().idxmax()}**",
    "Top 3 content types and their counts": lambda df: df['Type'].value_counts().head(3).reset_index().rename(columns={"index": "Type", "Type": "Count"}),
    "How many poems are there?": lambda df: df[df['Type'].str.contains("కవిత", na=False)].shape[0],
    "How many stories after 1990?": lambda df: df.assign(Published=pd.to_datetime(df['Published date'], errors='coerce')).query("Type.str.contains('కథ')", engine='python').query("Published.dt.year > 1990", engine='python').shape[0],
    "How many stories are there?": lambda df: df['Type'].str.contains("కథ", na=False).sum(),
    "How many magazines are there?": lambda df: df['Magazine'].nunique(),
    # 🔹 Publisher & Magazine
    "Top 10 publishers": lambda df: df['Publisher'].value_counts().head(10).reset_index().rename(columns={"index": "Publisher", "Publisher": "Count"}),
    "Top 10 magazines by publication count": lambda df: df['Magazine'].value_counts().head(10).reset_index().rename(columns={"index": "Magazine", "Magazine": "Count"}),
    "Which magazine has the most publications?": lambda df: f"📰 Magazine with most publications: **{df['Magazine'].value_counts().idxmax()}**",
    "Which publisher published most content after 2000?": lambda df: df.assign(Published=pd.to_datetime(df['Published date'], errors='coerce')).query("Published.dt.year > 2000", engine='python')['Publisher'].value_counts().idxmax(),

    # 🔹 Time-based
    "Most recent publication year?": lambda df: int(pd.to_datetime(df['Published date'], errors='coerce').dt.year.max()),
    "Earliest publication year?": lambda df: int(pd.to_datetime(df['Published date'], errors='coerce').dt.year.min()),
    "How many works were published after 2000?": lambda df: df.assign(Published=pd.to_datetime(df['Published date'], errors='coerce')).query("Published.dt.year > 2000", engine='python').shape[0],
    "How many publications per decade?": lambda df: df.assign(Year=pd.to_datetime(df['Published date'], errors='coerce').dt.year, Decade=lambda d: (d['Year']//10)*10).groupby('Decade').size().reset_index(name="Count"),
    "Which year had the highest number of publications?": lambda df: int(pd.to_datetime(df['Published date'], errors='coerce').dt.year.value_counts().idxmax()),

    # 🔹 Status & Metadata
    "How many active records are there?": lambda df: df[df['STATUS'] == True].shape[0],
    "How many inactive records are there?": lambda df: df[df['STATUS'] == False].shape[0],
    "Which authors have inactive works only?": lambda df: df.groupby("Author")['STATUS'].apply(lambda x: all(x == False)).reset_index(name="All Inactive").query("`All Inactive` == True")['Author'].reset_index(drop=True),
    "Which magazines have only active works?": lambda df: df.groupby("Magazine")['STATUS'].apply(lambda x: all(x == True)).reset_index(name="All Active").query("`All Active` == True")['Magazine'].reset_index(drop=True),
    "Authors ranked by number of works (highest to lowest)": lambda df: df['Author'].value_counts().reset_index().rename(columns={"index": "Author", "Author": "Count"}),
    # 🔹 Vol, Link & Extras
    "Which volume appears most often?": lambda df: f"🔁 Most frequent volume: **{df['Vol'].value_counts().idxmax()}**",
    "How many records have working links?": lambda df: df['Link'].dropna().apply(lambda x: isinstance(x, str) and x.startswith('http')).sum(),
    "Which author has most linked documents?": lambda df: df[df['Link'].notna()]['Author'].value_counts().idxmax(),
    "Any unknown data?": lambda df: df[['Author', 'Title', 'Type', 'Published date', 'Publisher', 'Magazine', 'Vol', 'Link']].isna().sum().reset_index().rename(columns={"index": "Column", 0: "Missing Values"}),
    

    # 🔹 Quality Checks
    "How many missing publication dates?": lambda df: df['Published date'].isna().sum(),
    "Are there duplicate titles?": lambda df: df['Title'].duplicated().sum(),
    "Top 10 duplicated titles": lambda df: df['Title'].value_counts().loc[lambda x: x > 1].head(10).reset_index().rename(columns={"index": "Title", "Title": "Count"}),
    "How many records missing volume info?": lambda df: df['Vol'].isna().sum(),    "Authors ranked from lowest to highest (min 2 works)": lambda df: df['Author'].value_counts().loc[lambda x: x >= 2].sort_values().reset_index().rename(columns={"index": "Author", "Author": "Count"}),
    "Magazines ranked from lowest to highest (min 2 records)": lambda df: df['Magazine'].value_counts().loc[lambda x: x >= 2].sort_values().reset_index().rename(columns={"index": "Magazine", "Magazine": "Count"}),
    "Content types ranked from least to most common": lambda df: df['Type'].value_counts().sort_values().reset_index().rename(columns={"index": "Type", "Type": "Count"}),
    "Publishers ranked from lowest to highest (min 2 records)": lambda df: df['Publisher'].value_counts().loc[lambda x: x >= 2].sort_values().reset_index().rename(columns={"index": "Publisher", "Publisher": "Count"}),
    "How many records missing magazine info?": lambda df: df['Magazine'].isna().sum(),


}

# UI
st.markdown("###  Ask a question from below")
selected_question = st.selectbox(" Select a question", list(questions.keys()), key="qa_selectbox")

if st.button(" Search", key="qa_button"):
    data = st.session_state.get("filtered_df", df)  # fallback to full dataset
    try:
        result = questions[selected_question](data)
        st.success("✅ Answer:")
        if isinstance(result, (pd.DataFrame, pd.Series)):
            st.dataframe(result)
        else:
            st.markdown(f"**{result}**")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
