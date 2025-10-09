# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# ---------- Task 1: Dropdown options ----------
site_options = (
    [{'label': 'All Sites', 'value': 'ALL'}] +
    [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]
)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Dropdown to select Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',  # default
        placeholder='Select a Launch Site here',
        searchable=True,
        clearable=False,
        style={'width': '60%'}
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[int(min_payload), int(max_payload)],
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        tooltip={'always_visible': False, 'placement': 'bottom'},
    ),
    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ---------------- Task 2 Callback: pie chart ----------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def render_success_pie(selected_site):
    site_col   = 'Launch Site'
    class_col  = 'class'

    if selected_site == 'ALL':
        # Sum of successes per site (class is 0/1)
        df_all = (spacex_df.groupby(site_col, as_index=False)[class_col]
                            .sum()
                            .rename(columns={class_col: 'Successes'}))
        fig = px.pie(
            df_all, values='Successes', names=site_col,
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure counts for the selected site
        df_site = spacex_df[spacex_df[site_col] == selected_site]
        counts = (df_site[class_col]
                  .value_counts()
                  .rename(index={1: 'Success', 0: 'Failure'})
                  .reset_index())
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(
            counts, values='Count', names='Outcome',
            title=f'Success vs Failure — {selected_site}'
        )

    fig.update_traces(textinfo='value+percent')
    return fig

# ------------- Task 4 Callback: scatter chart ----------------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def render_success_payload_scatter(selected_site, payload_range):
    site_col     = 'Launch Site'
    class_col    = 'class'
    payload_col  = 'Payload Mass (kg)'
    booster_col  = 'Booster Version Category'

    df = spacex_df.copy()
    # Ensure payload is numeric
    df[payload_col] = pd.to_numeric(df[payload_col], errors='coerce')
    df = df.dropna(subset=[payload_col])

    low, high = payload_range
    df = df[(df[payload_col] >= low) & (df[payload_col] <= high)]

    if selected_site != 'ALL':
        df = df[df[site_col] == selected_site]
        title = f'Payload vs Success — {selected_site}'
    else:
        title = 'Payload vs Success — All Sites'

    fig = px.scatter(
        df,
        x=payload_col,
        y=class_col,
        color=booster_col,
        hover_data=[site_col, booster_col, payload_col],
        labels={class_col: 'Success (1) / Failure (0)', payload_col: 'Payload Mass (kg)'},
        title=title
    )
    fig.update_traces(mode='markers', marker=dict(size=9, opacity=0.8))
    fig.update_layout(legend_title_text='Booster Version')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051, debug=False)  
