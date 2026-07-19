import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup and Titles (Displays text on the web page)
st.title('2025 Fantasy Football Analytics Dashboard')
st.markdown('Explore positional value scarcity, efficiency metrics, and distribution models.')

# 2. Data Pulling and Cleaning
data_url = "https://raw.githubusercontent.com/ArthurYang8/SIADS-521-Assignment-3/main/2025%20Fantasy%20Football%20Stats%20-%20Fantasy%20Footballers%20Podcast.csv"
df = pd.read_csv(data_url)

rename_columns = {
    'CMP': 'Pass Completions', 'YDS': 'Passing Yards', 'TD': 'Passing TDs', 'INT': 'Interceptions',
    'ATT': 'Rushing Attempts', 'YDS.1': 'Rushing Yards', 'TD.1': 'Rushing TDs', 'FUM': 'Fumbles',
    'TGT': 'Targets', 'REC': 'Receptions', 'YDS.2': 'Receiving Yards', 'TD.2': 'Receiving TDs'
}
df = df.rename(columns = rename_columns)
df['PositionRank'] = df.groupby('POS')['PTS'].rank(ascending = False, method = 'first')

def assign_tier(rank):
    if rank <= 5:     return '1: Top 5 (Ranks 1-5)'
    elif rank <= 10:  return '2: Elite (Ranks 6-10)'
    elif rank <= 15:  return '3: Solid (Ranks 11-15)'
    elif rank <= 20:  return '4: Depth (Ranks 16-20)'
    else:             return '5: Waiver Wire (Ranks 21+)'
df['Tier'] = df['PositionRank'].apply(assign_tier)

# 3. Interactive Web Controls (Swapped widgets for st.selectbox)
selected_position = st.selectbox(
    label = "Select Position to Analyze:",
    options = ['QB', 'RB', 'WR', 'TE'],
    index = 0
)

# 4. Filter and Chart Logic
filtered_df = df[df['POS'] == selected_position]
avg_tier_points = filtered_df.groupby('Tier', as_index=False)['PTS'].mean().sort_values('Tier')

st.subheader(f"1. Value Scarcity Curve: {selected_position}s")

fig_tier = px.bar(
    avg_tier_points,
    x='Tier',
    y='PTS',
    text_auto='.1f',
    labels={'PTS': 'Avg Points', 'Tier': 'Performance Tier'},
    title=f'Average Total Points Dropped by Tier ({selected_position})',
    color='Tier',
    color_discrete_sequence=px.colors.sequential.OrRd_r
)
fig_tier.update_layout(showlegend=False)

# Renders the interactive Plotly chart on the web page canvas
st.plotly_chart(fig_tier)
