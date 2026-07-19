import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup and Titles (Displays text on the web page)
st.set_page_config(layout="wide")
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

# Isolate the Top 50 RBs
rb_df = df[df['POS'] == 'RB'].copy()
rb_df = rb_df.sort_values(by='PTS', ascending=False).head(50)

mid_x = rb_df['Rushing Yards'].median()
mid_y = rb_df['Receiving Yards'].median()

# 3. Interactive Web Controls (Swapped widgets for st.selectbox)
col_left, col_right = st.columns(2)

with col_left:
    selected_position = st.selectbox(
        label = "Select Position to Analyze (Chart 1):",
        options = ['QB', 'RB', 'WR', 'TE'],
        index = 0
    )

with col_right:
    # Streamlit search dropdown box for the top 50 RBs
    rb_list = sorted(rb_df['Name'].tolist())
    search_name = st.selectbox(
        label = "Highlight a specific Running Back (Chart 2):",
        options = ["Show All Players"] + rb_list
    )

# 4. Filter and Chart Logic
st.write("")
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
st.plotly_chart(fig_tier, use_container_width = True)

st.markdown("---")

st.header("2. Top 50 Running Back Profiles: Archetype Quadrants")
st.markdown(
    "**Top-Right:** Well-Rounded | **Bottom-Right:** Pure Runners | "
    "**Top-Left:** Pass-Catchers | **Bottom-Left:** Waiver RBs"
)

fig_scatter = px.scatter(
    rb_df,
    x='Rushing Yards',
    y='Receiving Yards',
    color='PTS',
    size='Receptions',
    hover_name='Name',
    title="Top 50 Running Back Profiles: Rushing vs. Receiving Yards",
    labels={
        'Rushing Yards': 'Total Rushing Yards',
        'Receiving Yards': 'Total Receiving Yards',
        'PTS': 'Total Fantasy Points'
    },
    color_continuous_scale=px.colors.sequential.Viridis,
    width=950,
    height=600
)

if search_name != "Show All Players":
    opacity_array = [1.0 if n == search_name else 0.15 for n in rb_df['Name']]
else:
    opacity_array = [0.85 for _ in rb_df['Name']]

# Safely inject the opacity values into the trace layout mapping
fig_scatter.update_traces(marker=dict(opacity=opacity_array))

# Draw the benchmark quadrant crosshairs onto the Streamlit canvas
fig_scatter.add_vline(x=mid_x, line_dash="dash", line_color="red", annotation_text=" Rushing Median")
fig_scatter.add_hline(y=mid_y, line_dash="dash", line_color="red", annotation_text=" Receiving Median")
fig_scatter.update_layout(hovermode='closest')

st.plotly_chart(fig_scatter, use_container_width=True)
