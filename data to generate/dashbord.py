import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# --- THEME AND STYLES (VIP Professional Look) ---
VIP_BG = '#1e1e1e'       # Deep Dark Background
VIP_CARD_BG = '#2d2d2d'  # Card Background (Slightly Lighter)
VIP_TEXT = '#ffffff'     # White Text
VIP_ACCENT = '#00bcd4'   # Cyan/Aqua Accent Color (Primary Highlight)
KPI_GOOD = '#4CAF50'     # Green for positive change
KPI_BAD = '#FF5722'      # Orange/Red for negative change

# --- METRIC MAPPING for dynamic selection ---
METRIC_OPTIONS = {
    'Box_Office_Revenue_USD': 'Box Office Revenue',
    'IMDb_Rating': 'IMDb Rating',
    'Budget_USD': 'Production Budget'
}

# Function to format large numbers (e.g., 50000000 -> $50M)
def format_currency(value):
    if pd.isna(value) or value == 0:
        return "$0"
    if abs(value) >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    return f"${value:,.0f}"

# Function to format benchmark comparison
def format_benchmark(filtered_value, total_value, is_better_higher=True):
    if pd.isna(filtered_value) or pd.isna(total_value) or total_value == 0:
        return html.Span("-", style={'color': '#aaa', 'fontSize': '0.9em', 'marginLeft': '5px'})
    
    diff = filtered_value - total_value
    percent_diff = (diff / total_value) * 100
    
    arrow = "▲" if diff > 0 else "▼"
    color = KPI_GOOD if (diff > 0 and is_better_higher) or (diff < 0 and not is_better_higher) else KPI_BAD
    
    # Text for comparison
    return html.Span(
        f" {arrow} {abs(percent_diff):.1f}% vs Total",
        style={'color': color, 'fontSize': '0.9em', 'marginLeft': '5px'}
    )

# --- DATA LOAD AND GLOBAL BENCHMARK CALCULATIONS ---
try:
    df = pd.read_csv("Realistic_Movie_Dataset_1Lakh.csv")
except FileNotFoundError:
    print("ERROR: Please ensure 'Realistic_Movie_Dataset_1Lakh.csv' is in the same directory.")
    exit()

# Global Benchmarks (Calculated only once)
TOTAL_REVENUE_ALL = df['Box_Office_Revenue_USD'].sum()
AVG_BUDGET_ALL = df['Budget_USD'].mean()
AVG_RATING_ALL = df['IMDb_Rating'].mean()

# Data Preparation
df['Year'] = df['Release_Year'].astype(str)
min_year = df['Release_Year'].min()
max_year = df['Release_Year'].max()
ALL_GENRES = [{'label': i, 'value': i} for i in df['Genre'].unique()] # Defined for Dropdown

# --- DASH APP INITIALIZATION ---
# Dash automatically loads CSS files from the 'assets' folder
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']) 

# --- CARD STYLE DEFINITION (Added CSS Class) ---
card_style = {
    'backgroundColor': VIP_CARD_BG,
    'color': VIP_TEXT,
    'padding': '20px',
    'borderRadius': '12px',
    'boxShadow': '0 4px 8px 0 rgba(0, 0, 0, 0.4)',
    'marginBottom': '20px',
    'border': f'1px solid {VIP_ACCENT}',
}

# --- KPI CARD STYLE ---
kpi_card_style = {
    'flex': '1',
    'textAlign': 'center',
    'padding': '15px',
    'borderRadius': '8px',
    'backgroundColor': VIP_CARD_BG,
    'boxShadow': '0 2px 4px 0 rgba(0, 0, 0, 0.4)',
}

# --- APP LAYOUT (Responsive Classes Added) ---
app.layout = html.Div(
    className='dash-app-container', # Added class for global padding adjustment
    style={'backgroundColor': VIP_BG, 'padding': '30px'}, 
    children=[
    
    # VIP Title Bar
    html.H1("👑 Enterprise Movie Success Dashboard", style={
        'textAlign': 'center', 
        'color': VIP_ACCENT, 
        'marginBottom': '5px',
        'fontWeight': '900',
        'fontSize': '3em',
        'borderBottom': f'3px solid {VIP_ACCENT}'
    }),
    
    # Dynamic Filter Summary Title
    html.P(id='filter-summary', style={'textAlign': 'center', 'marginBottom': '40px', 'color': '#ccc', 'fontSize': '1.1em'}),


    # --- CONTROLS / FILTERS (Styled as a Card) ---
    html.Div(style=card_style, children=[
        html.H5("FILTERS", style={'color': VIP_TEXT, 'borderBottom': '1px solid #444', 'paddingBottom': '10px'}),
        
        # Row 1: Genre & Year Slider (Added Responsive Class)
        html.Div(className='filter-row-flex', 
                 style={'display': 'flex', 'gap': '50px', 'paddingTop': '10px', 'marginBottom': '20px'}, 
                 children=[
            
            # Genre Dropdown
            html.Div([
                html.Label("Genre Filter:", style={'fontWeight': 'bold', 'color': VIP_TEXT}),
                dcc.Dropdown(
                    id='genre-dropdown',
                    options=ALL_GENRES,
                    value=df['Genre'].unique()[:4].tolist(), 
                    multi=True,
                    style={'backgroundColor': VIP_CARD_BG, 'color': '#000'}
                ),
            ], style={'flexGrow': '1'}),

            # Year Slider
            html.Div([
                html.Label("Release Year Range:", style={'fontWeight': 'bold', 'color': VIP_TEXT}),
                dcc.RangeSlider(
                    id='year-slider',
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=[2000, max_year],
                    marks={
                        str(year): {'label': str(year), 'style': {'color': VIP_ACCENT}} 
                        for year in range(min_year, max_year + 1, 5)
                    }
                ),
            ], style={'flexGrow': '2', 'paddingTop': '10px'}),
        ]),
        
        # Row 2: METRIC SELECTOR (Added Responsive Class)
        html.Div(className='metric-selector-div', children=[
            html.Label("Select Y-Axis Metric (For Scatter/Bubble Charts):", style={'fontWeight': 'bold', 'color': VIP_TEXT}),
            dcc.Dropdown(
                id='y-axis-metric-selector',
                options=[
                    {'label': v, 'value': k} for k, v in METRIC_OPTIONS.items()
                ],
                value='Box_Office_Revenue_USD',
                clearable=False,
                style={'backgroundColor': VIP_CARD_BG, 'color': '#000'}
            ),
        ], style={'width': '50%', 'paddingTop': '10px'}),
        
    ]), # End of Filters Card

    # --- KPI SCORECARDS (Added Responsive Class) ---
    html.Div(className='kpi-row', 
             style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}, 
             children=[
        # KPI 1: Total Revenue
        html.Div(style=kpi_card_style, children=[
            html.H3(html.Div([html.Span(id='kpi-revenue-value'), html.Span(id='kpi-revenue-bench')]), 
                    style={'color': KPI_GOOD, 'fontSize': '2.2em', 'margin': '0'}),
            html.P("TOTAL BOX OFFICE (Filtered)", style={'color': '#aaa', 'margin': '0'})
        ]),
        # KPI 2: Avg Budget
        html.Div(style=kpi_card_style, children=[
            html.H3(html.Div([html.Span(id='kpi-budget-value'), html.Span(id='kpi-budget-bench')]), 
                    style={'color': VIP_ACCENT, 'fontSize': '2.2em', 'margin': '0'}),
            html.P("AVERAGE BUDGET", style={'color': '#aaa', 'margin': '0'})
        ]),
        # KPI 3: Avg IMDb Rating
        html.Div(style=kpi_card_style, children=[
            html.H3(html.Div([html.Span(id='kpi-rating-value'), html.Span(id='kpi-rating-bench')]), 
                    style={'color': KPI_GOOD, 'fontSize': '2.2em', 'margin': '0'}),
            html.P("AVERAGE IMDb RATING", style={'color': '#aaa', 'margin': '0'})
        ]),
        # KPI 4: Records Count
        html.Div(style=kpi_card_style, children=[
            html.H3(id='kpi-records', style={'color': VIP_ACCENT, 'fontSize': '2.5em', 'margin': '0'}),
            html.P("RECORDS ANALYZED", style={'color': '#aaa', 'margin': '0'})
        ]),
    ]),
    

    # --- GRAPHS AREA (Added Responsive Class) ---
    html.Div(className='graph-container-flex', 
             style={'marginTop': '20px', 'display': 'flex', 'gap': '20px'}, 
             children=[
        
        # 1. Regression Plot (Added Class)
        html.Div(className='card-style', children=[
            dcc.Graph(id='regression-plot', style={'height': '500px'}),
        ], style={
            'flex': '1', 
            **card_style 
        }), 

        # 2. Treemap (Added Class)
        html.Div(className='card-style', children=[
            dcc.Graph(id='treemap-plot', style={'height': '500px'}),
        ], style={
            'flex': '1', 
            **card_style 
        }),
    ]),

    # 3. TREND PLOT (HISTOGRAM)
    html.Div(className='card-style', children=[
        dcc.Graph(id='trend-plot', style={'height': '400px'}),
    ], style={'marginTop': '20px', **card_style}),
    
    # 4. Bubble Chart
    html.Div(className='card-style', children=[
        dcc.Graph(id='bubble-plot', style={'height': '500px'}),
    ], style={'marginTop': '20px', **card_style}),

])

# --- CALLBACKS (The Dynamic/Interactive Part) ---
# ... (Callback function remains the same as it doesn't need responsiveness) ...

@app.callback(
    [Output('regression-plot', 'figure'),
     Output('treemap-plot', 'figure'),
     Output('bubble-plot', 'figure'),
     Output('trend-plot', 'figure'),
     
     # KPI Values
     Output('kpi-revenue-value', 'children'),
     Output('kpi-budget-value', 'children'),
     Output('kpi-rating-value', 'children'),
     Output('kpi-records', 'children'),

     # KPI Benchmarks
     Output('kpi-revenue-bench', 'children'),
     Output('kpi-budget-bench', 'children'),
     Output('kpi-rating-bench', 'children'),
     
     # Filter Summary
     Output('filter-summary', 'children')
     ],
    [Input('genre-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('y-axis-metric-selector', 'value')]
)
def update_graph(selected_genres, year_range, y_axis_metric):
    # Data Filtering
    filtered_df = df[
        (df['Genre'].isin(selected_genres)) &
        (df['Release_Year'] >= year_range[0]) &
        (df['Release_Year'] <= year_range[1])
    ].copy()
    
    # Robust Check for empty data before proceeding
    if filtered_df.empty:
        # Return empty figures and zero KPIs with a clear warning message
        empty_fig = {'data': [], 'layout': {'title': 'NO DATA: Please broaden your selection.', 'template': 'plotly_dark'}}
        
        empty_kpi = [
            'N/A', 'N/A', 'N/A', '0', 
            html.Span("---", style={'color': KPI_BAD}),
            html.Span("---", style={'color': KPI_BAD}),
            html.Span("---", style={'color': KPI_BAD}),
            "DATASET EMPTY"
        ]
        return empty_fig, empty_fig, empty_fig, empty_fig, *empty_kpi


    # Get the display name for the selected metric
    y_axis_name = METRIC_OPTIONS[y_axis_metric]

    # --- KPI CALCULATIONS (Filtered) ---
    total_revenue = filtered_df['Box_Office_Revenue_USD'].sum()
    avg_budget = filtered_df['Budget_USD'].mean()
    avg_rating = filtered_df['IMDb_Rating'].mean()
    record_count = len(filtered_df)

    # --- KPI OUTPUTS ---
    kpi_rev_output = format_currency(total_revenue)
    kpi_bud_output = format_currency(avg_budget)
    kpi_rat_output = f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A"
    kpi_rec_output = f"{record_count:,}"

    # --- BENCHMARK OUTPUTS (Comparing Filtered vs ALL) ---
    kpi_rev_bench = format_benchmark(total_revenue, TOTAL_REVENUE_ALL, is_better_higher=True)
    kpi_bud_bench = format_benchmark(avg_budget, AVG_BUDGET_ALL, is_better_higher=False) # Lower budget is better
    kpi_rat_bench = format_benchmark(avg_rating, AVG_RATING_ALL, is_better_higher=True)

    # --- FILTER SUMMARY OUTPUT (Clarity) ---
    genre_text = ", ".join(selected_genres) if selected_genres else "All Selected Genres"
    summary_output = f"Analyzing {record_count:,} Records for Genres: {genre_text} | Years: {year_range[0]} to {year_range[1]}"
    
    
    # Performance optimization: Sample data for scatter/bubble plots
    if len(filtered_df) > 7000:
        plot_df = filtered_df.sample(7000)
    else:
        plot_df = filtered_df
        
    # --- CONDITIONAL LOGIC FOR REGRESSION PLOT (FIXED ERROR) ---
    x_axis_metric = 'Budget_USD'
    
    if y_axis_metric == x_axis_metric:
        trendline_val = None
        regression_title = f"1. Budget Distribution (Regression Line Skipped)"
    else:
        trendline_val = "ols"
        regression_title = f"1. Budget vs {y_axis_name} (Regression Line)"
        
    # --- 1. REGRESSION PLOT ---
    fig_reg = px.scatter(
        plot_df,
        x=x_axis_metric,
        y=y_axis_metric,
        color="Genre",
        trendline=trendline_val, 
        template="plotly_dark",
        title=regression_title,
        hover_data=["Title", "IMDb_Rating"]
    )
    fig_reg.update_layout(transition_duration=500)

    # --- 2. TREEMAP PLOT ---
    tree_data = filtered_df.groupby("Genre")["Box_Office_Revenue_USD"].sum().reset_index()
    fig_tree = px.treemap(
        tree_data,
        path=["Genre"],
        values="Box_Office_Revenue_USD",
        title="2. Total Revenue by Genre (Treemap)",
        template="plotly_dark",
        color_continuous_scale='Bluered'
    )
    fig_tree.update_layout(transition_duration=500)

    # --- 3. BUBBLE CHART ---
    fig_bubble = px.scatter(
        plot_df,
        x="IMDb_Rating",
        y=y_axis_metric,
        size="Budget_USD",
        color="Genre",
        size_max=40,
        template="plotly_dark",
        title=f"4. IMDb Rating vs {y_axis_name} (Bubble Size = Budget)",
    )
    fig_bubble.update_layout(transition_duration=500)

    # --- 4. TREND PLOT (HISTOGRAM) ---
    fig_trend = px.histogram(
        filtered_df,
        x='Release_Year',
        title='3. Movie Release Volume Trend by Year',
        template='plotly_dark',
        color_discrete_sequence=[VIP_ACCENT]
    ).update_xaxes(type='category')
    fig_trend.update_layout(bargap=0.1)


    return (
        fig_reg, fig_tree, fig_bubble, fig_trend, 
        kpi_rev_output, kpi_bud_output, kpi_rat_output, kpi_rec_output,
        kpi_rev_bench, kpi_bud_bench, kpi_rat_bench,
        summary_output
    )

# --- RUN SERVER ---
if __name__ == '__main__':
    app.run(debug=True)