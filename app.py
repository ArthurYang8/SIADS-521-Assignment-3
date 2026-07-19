simport streamlit as st
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

# Isolate Top 50 WRs
wr_df = df[df['POS'] == 'WR'].copy()
wr_df = wr_df.sort_values(by='PTS', ascending=False).head(50)
wr_df['YPR'] = wr_df['Receiving Yards'] / wr_df['Receptions']

p33 = wr_df['YPR'].quantile(0.33)
p66 = wr_df['YPR'].quantile(0.66)

def categorize_wr(ypr):
    if ypr > p66:   return 'Explosive (Deep Threat)'
    elif ypr > p33: return 'Average (Balanced)'
    else:           return 'Short Route / Checkdown'
wr_df['Archetype'] = wr_df['YPR'].apply(categorize_wr)

# Isolate Top 30 QBs
qb_df = df[df['POS'] == 'QB'].copy()
qb_df = qb_df.sort_values(by='Passing Yards', ascending=False).head(30)

# 3. Interactive Web Controls Layout
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

with col_ctrl1:
    selected_position = st.selectbox(
        label = "Select Position to Analyze (Chart 1):",
        options = ['QB', 'RB', 'WR', 'TE'],
        index = 0
    )

with col_ctrl2:
    # Streamlit search dropdown box for the top 50 RBs
    rb_list = sorted(rb_df['Name'].tolist())
    search_name = st.selectbox(
        label = "Highlight a specific Running Back (Chart 2):",
        options = ["Show All Players"] + rb_list
    )

with col_ctrl3:
    # Choose an archetype of WR
    selected_archetype = st.selectbox(
        label = "Filter Roster List by WR Archetype (Chart 3):",
        options = ["All Archetypes", "Explosive (Deep Threat)", "Average (Balanced)", "Short Route / Checkdown"])

# The dashboard itself
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

# Renders the chart
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

# Opacity Values and rendering chart 2
fig_scatter.update_traces(marker=dict(opacity=opacity_array))
fig_scatter.add_vline(x=mid_x, line_dash="dash", line_color="red", annotation_text=" Rushing Median")
fig_scatter.add_hline(y=mid_y, line_dash="dash", line_color="red", annotation_text=" Receiving Median")
fig_scatter.update_layout(hovermode='closest')
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.header("3. Wide Receiver Profiles: Point Distribution by Archetype")

if selected_archetype != 'All Archetypes':
    filtered_wr = wr_df[wr_df['Archetype'] == selected_archetype]
else:
    filtered_wr = wr_df

fig_wr_hist = px.histogram(
    filtered_wr,
    x='PTS',
    color='Archetype',
    nbins=15,
    title=f"Top 50 Wide Receivers Point Distribution Spread: {selected_archetype}",
    labels={'PTS': 'Total Fantasy Points'},
    color_discrete_map={
        'Explosive (Deep Threat)': '#FFD166',
        'Average (Balanced)': '#06D6A0',
        'Short Route / Checkdown': '#118AB2'
    },
    width=950,
    height=450
)
fig_wr_hist.update_layout(yaxis_title="Number of Players")
st.plotly_chart(fig_wr_hist, use_container_width=True)

# the list of WRs as a dataframe
st.subheader("Wide Receiver Archetype Rosters")
st.dataframe(
    filtered_wr[['Name', 'Archetype', 'YPR', 'PTS']].sort_values(by='PTS', ascending=False),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.header("4. Quarterback Efficiency: Passing Yards vs. Total Points")

fig_qb_line = px.line(
    qb_df,
    x='Passing Yards',
    y='PTS',
    hover_name='Name',
    hover_data={'Rushing Yards': True},
    title = "QB Efficiency: Passing Yards vs Total Points",
    labels={
        'Passing Yards': 'Total Passing Yards', 
        'Rushing Yards': 'Total Rushing Yards', 
        'PTS': 'Total Fantasy Points'
    },
    markers=True
)
fig_qb_line.update_traces(line=dict(color='#4A6FA5', width=3), marker=dict(size=8))
st.plotly_chart(fig_qb_line, use_container_width=True)
