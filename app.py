import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO

# --- Data ---
data = {
    'Category': ['Adjective', 'Adjective', 'Adjective', 'Verb', 'Verb', 'Verb'],
    'Subcategory': ['Color', 'Size', 'Emotion', 'Movement', 'Action', 'State'],  # Added Subcategory
    'French': ['rouge', 'grand', 'heureux', 'courir', 'manger', 'dormir'],
    'Russian': ['красный', 'большой', 'счастливый', 'бегать', 'есть', 'спать']
}

df = pd.DataFrame(data)


# --- Helper Function for TTS ---
def get_audio_base64(text):
    tts = gTTS(text=text, lang='ru')  # Set language to Russian
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    return f'<audio controls src="data:audio/mpeg;base64,{b64}"/>'


# --- Streamlit App ---
st.title('French-Russian Vocabulary for French Learners')

# --- Initial Values for Multiselect and Checkbox ---
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = df['Category'].unique()[:1]
if 'selected_subcategories' not in st.session_state:
    st.session_state.selected_subcategories = df['Subcategory'].unique()[:1]
if 'show_french' not in st.session_state:  # Initialize show_french in session state
    st.session_state.show_french = True

# --- Sidebar ---
with st.sidebar:
    st.header('Filters')
    selected_categories = st.multiselect('Select Categories', df['Category'].unique())
    selected_subcategories = st.multiselect('Select Subcategories', df['Subcategory'].unique())

# --- Filter DataFrame ---
if selected_categories or selected_subcategories:
    filtered_df = df.loc[
        (df['Category'].isin(selected_categories) if selected_categories else True) & 
        (df['Subcategory'].isin(selected_subcategories) if selected_subcategories else True)
    ].copy()

    # --- Add TTS Column ---
    filtered_df.loc[:, 'Listen'] = filtered_df['Russian'].apply(get_audio_base64)


    # --- Show/Hide Columns ---
    col1, col2 = st.columns(2)
    with col1:
        show_russian = st.checkbox('Show Russian')
    with col2:
        show_french = st.checkbox('Show French',  value=st.session_state.show_french)

    columns_to_show = ['Category', 'Subcategory', 'Listen']  # Always show Listen column
    if show_french:
        columns_to_show.append('French')
    if show_russian:
        columns_to_show.append('Russian')

    # --- Slider ---
    num_words = st.slider('Number of Words', min_value=1, max_value=len(filtered_df), value=5)
    displayed_df = filtered_df[columns_to_show].head(num_words)

    # --- Display DataFrame with HTML for Audio ---
    st.write(displayed_df.to_html(escape=False, formatters={'Listen': lambda x: x}), unsafe_allow_html=True)

else:
    st.warning('Please select at least one category or subcategory.')
