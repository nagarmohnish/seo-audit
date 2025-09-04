# Import libraries
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import os
import base64

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load audit data from audit_report.xlsx
def load_audit_data():
    audit_file = 'reports/audit_report.xlsx'
    if not os.path.exists(audit_file):
        print(f'Error: {audit_file} not found in {os.getcwd()}. Please run audit.ipynb to generate audit reports.')
        return None
    try:
        data = {
            'html_pages': pd.read_excel(audit_file, sheet_name='HTML Pages'),
            '4xx_errors': pd.read_excel(audit_file, sheet_name='4xx Errors'),
            'slow_pages': pd.read_excel(audit_file, sheet_name='Slow Pages'),
            'missing_canonical': pd.read_excel(audit_file, sheet_name='Missing Canonical'),
            'suboptimal_titles': pd.read_excel(audit_file, sheet_name='Suboptimal Titles'),
            'suboptimal_metas': pd.read_excel(audit_file, sheet_name='Suboptimal Metas'),
            'thin_pages': pd.read_excel(audit_file, sheet_name='Thin Content'),
            'low_readability': pd.read_excel(audit_file, sheet_name='Low Readability'),
            'near_duplicates': pd.read_excel(audit_file, sheet_name='Near Duplicates'),
            'deep_pages': pd.read_excel(audit_file, sheet_name='Deep Pages'),
            'low_inlinks': pd.read_excel(audit_file, sheet_name='Low Inlinks'),
            'large_pages': pd.read_excel(audit_file, sheet_name='Large Pages'),
            'outdated_pages': pd.read_excel(audit_file, sheet_name='Outdated Pages'),
            'http_1_pages': pd.read_excel(audit_file, sheet_name='HTTP 1.1 Pages')
        }
        return data
    except Exception as e:
        print(f'Error loading audit data: {e}')
        return None

# Load original CSV for histograms
def load_csv_data():
    csv_file = 'data/raw/internal_all_02.csv'
    if not os.path.exists(csv_file):
        print(f'Error: {csv_file} not found in {os.getcwd()}. Please ensure the Screaming Frog crawl file is in the data/raw directory.')
        return None
    try:
        df = pd.read_csv(csv_file, low_memory=False)
        df.columns = df.columns.str.lower().str.strip()
        if 'title 1 length' not in df.columns or 'meta description 1 length' not in df.columns:
            print(f'Error: Required columns (title 1 length, meta description 1 length) missing in {csv_file}.')
            return None
        return df
    except Exception as e:
        print(f'Error loading CSV: {e}')
        return None

# Load data
data = load_audit_data()
csv_data = load_csv_data()
if data is None or csv_data is None:
    app.layout = html.Div([
        html.H1('Error: Missing data files.', className='text-center my-4'),
        html.P('Please run audit.ipynb to generate reports/audit_report.xlsx and ensure data/raw/internal_all_02.csv exists in C:\\Library\\Projects\\LH2\\Automation\\audit_test\\at_test_01\\data\\raw.')
    ])
else:
    # Load images
    def load_image(image_path):
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('ascii')
            return f'data:image/png;base64,{encoded}'
        print(f'Warning: Image {image_path} not found.')
        return None

    # Create metric card
    def create_metric_card(title, value, color='primary'):
        return dbc.Card([
            dbc.CardBody([
                html.H4(title, className='card-title'),
                html.H2(str(value), className='card-text')
            ])
        ], color=color, className='text-center m-2')

    # Create data table
    def create_data_table(df, table_id, max_rows=10):
        return dash_table.DataTable(
            id=table_id,
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.head(max_rows).to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px'},
            page_size=max_rows,
            page_action='native',
            export_format='csv',
            export_headers='display'
        )

    # Layout with collapsible sections
    app.layout = dbc.Container([
        html.H1('SEO Audit Dashboard', className='text-center my-4'),
        
        # Crawl Overview
        dbc.Card([
            dbc.CardHeader(html.H3('Crawl Overview', id='crawl-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Total URLs', len(data['html_pages']), 'info'), width=3),
                        dbc.Col(create_metric_card('4xx Errors', len(data['4xx_errors']), 'danger'), width=3),
                        dbc.Col(create_metric_card('Slow Pages (>0.5s)', len(data['slow_pages']), 'warning'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([html.Img(src=load_image('reports/status_codes.png'), style={'width': '100%'})], width=6),
                        dbc.Col(create_data_table(data['4xx_errors'], 'table-4xx'), width=6)
                    ])
                ]),
                id='crawl-collapse',
                is_open=True
            )
        ], className='mb-4'),

        # Indexability
        dbc.Card([
            dbc.CardHeader(html.H3('Indexability', id='indexability-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Non-Indexable Pages', len(data['missing_canonical']), 'danger'), width=3),
                        dbc.Col(create_metric_card('Missing Canonical', len(data['missing_canonical']), 'warning'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([html.Img(src=load_image('reports/indexability.png'), style={'width': '100%'})], width=6),
                        dbc.Col(create_data_table(data['missing_canonical'], 'table-canonical'), width=6)
                    ])
                ]),
                id='indexability-collapse',
                is_open=True
            )
        ], className='mb-4'),

        # On-Page SEO
        dbc.Card([
            dbc.CardHeader(html.H3('On-Page SEO', id='onpage-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Suboptimal Titles', len(data['suboptimal_titles']), 'warning'), width=3),
                        dbc.Col(create_metric_card('Suboptimal Metas', len(data['suboptimal_metas']), 'warning'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=px.histogram(csv_data, x='title 1 length', nbins=50, title='Title Length Distribution')),
                            dcc.Graph(figure=px.histogram(csv_data, x='meta description 1 length', nbins=50, title='Meta Description Length Distribution'))
                        ], width=6),
                        dbc.Col(create_data_table(data['suboptimal_titles'], 'table-titles'), width=6)
                    ])
                ]),
                id='onpage-collapse',
                is_open=True
            )
        ], className='mb-4'),

        # Content Quality
        dbc.Card([
            dbc.CardHeader(html.H3('Content Quality', id='content-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Thin Content Pages', len(data['thin_pages']), 'warning'), width=3),
                        dbc.Col(create_metric_card('Low Readability Pages', len(data['low_readability']), 'warning'), width=3),
                        dbc.Col(create_metric_card('Near Duplicates', len(data['near_duplicates']), 'danger'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([html.Img(src=load_image('reports/content_quality.png'), style={'width': '100%'})], width=6),
                        dbc.Col(create_data_table(data['thin_pages'], 'table-thin'), width=6)
                    ])
                ]),
                id='content-collapse',
                is_open=True
            )
        ], className='mb-4'),

        # Site Architecture
        dbc.Card([
            dbc.CardHeader(html.H3('Site Architecture', id='architecture-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Deep Pages (>3)', len(data['deep_pages']), 'warning'), width=3),
                        dbc.Col(create_metric_card('Low Inlinks (<5)', len(data['low_inlinks']), 'warning'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([html.Img(src=load_image('reports/link_correlations.png'), style={'width': '100%'})], width=6),
                        dbc.Col(create_data_table(data['deep_pages'], 'table-deep'), width=6)
                    ])
                ]),
                id='architecture-collapse',
                is_open=True
            )
        ], className='mb-4'),

        # Performance
        dbc.Card([
            dbc.CardHeader(html.H3('Performance', id='performance-header', style={'cursor': 'pointer'})),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(create_metric_card('Large Pages (>100KB)', len(data['large_pages']), 'warning'), width=3),
                        dbc.Col(create_metric_card('Outdated Pages (>1yr)', len(data['outdated_pages']), 'warning'), width=3),
                        dbc.Col(create_metric_card('HTTP 1.1 Pages', len(data['http_1_pages']), 'warning'), width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([html.Img(src=load_image('reports/page_size.png'), style={'width': '100%'})], width=6),
                        dbc.Col(create_data_table(data['large_pages'], 'table-large'), width=6)
                    ])
                ]),
                id='performance-collapse',
                is_open=True
            )
        ], className='mb-4')
    ], fluid=True)

    # Callback for collapsible sections
    @app.callback(
        [Output('crawl-collapse', 'is_open'),
         Output('indexability-collapse', 'is_open'),
         Output('onpage-collapse', 'is_open'),
         Output('content-collapse', 'is_open'),
         Output('architecture-collapse', 'is_open'),
         Output('performance-collapse', 'is_open')],
        [Input('crawl-header', 'n_clicks'),
         Input('indexability-header', 'n_clicks'),
         Input('onpage-header', 'n_clicks'),
         Input('content-header', 'n_clicks'),
         Input('architecture-header', 'n_clicks'),
         Input('performance-header', 'n_clicks')],
        [dash.dependencies.State('crawl-collapse', 'is_open'),
         dash.dependencies.State('indexability-collapse', 'is_open'),
         dash.dependencies.State('onpage-collapse', 'is_open'),
         dash.dependencies.State('content-collapse', 'is_open'),
         dash.dependencies.State('architecture-collapse', 'is_open'),
         dash.dependencies.State('performance-collapse', 'is_open')]
    )
    def toggle_collapse(crawl_clicks, index_clicks, onpage_clicks, content_clicks, arch_clicks, perf_clicks,
                        crawl_state, index_state, onpage_state, content_state, arch_state, perf_state):
        ctx = dash.callback_context
        if not ctx.triggered:
            return crawl_state, index_state, onpage_state, content_state, arch_state, perf_state
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'crawl-header':
            return not crawl_state, index_state, onpage_state, content_state, arch_state, perf_state
        elif button_id == 'indexability-header':
            return crawl_state, not index_state, onpage_state, content_state, arch_state, perf_state
        elif button_id == 'onpage-header':
            return crawl_state, index_state, not onpage_state, content_state, arch_state, perf_state
        elif button_id == 'content-header':
            return crawl_state, index_state, onpage_state, not content_state, arch_state, perf_state
        elif button_id == 'architecture-header':
            return crawl_state, index_state, onpage_state, content_state, not arch_state, perf_state
        elif button_id == 'performance-header':
            return crawl_state, index_state, onpage_state, content_state, arch_state, not perf_state
        return crawl_state, index_state, onpage_state, content_state, arch_state, perf_state

# Run the app
if __name__ == '__main__':
    app.run(debug=True)