import pandas as pd
from dash import html, dcc, Output, Input, Dash, dash_table
from orderbook import product_id, agg_level
import sqlite3

app = Dash(__name__)

app.layout = html.Div([
    html.H1(id='mid-price'),
    dcc.Interval(id='update', interval=2000),
    dash_table.DataTable(id='my-table',
                         columns=[
                             {'name': 'Price', 'id': 'px', 'type': 'text'},
                             {'name': 'Qty', 'id': 'qty', 'type': 'text'},
                         ],
                         style_data_conditional=[
                             {
                                 'if': {
                                     'column_id': 'px',
                                     'filter_query': '{id} contains "bid"'
                                 },
                                 'backgroundColor': '#50C878'
                             },
                             {
                                 'if': {
                                     'column_id': 'px',
                                     'filter_query': '{id} contains "ask"'
                                 },
                                 'backgroundColor': '#DC143C'
                             },
                             {
                                 'if': {
                                     'column_id': 'qty',
                                     'filter_query': '{id} contains "ask"'
                                 },
                                 'backgroundColor': '#FAA0A0'
                             },
                             {
                                 'if': {
                                     'column_id': 'qty',
                                     'filter_query': '{id} contains "bid"'
                                 },
                                 'backgroundColor': '#C1E1C1'
                             }
                         ],
                         style_cell={'font-family': 'Courier New'}
                         )

], style={'width': '30%', 'font-family': 'Arial'}, )


@app.callback(
    Output('mid-price', 'children'),
    Input('update', 'n_intervals'),
)
def update_mid(intervals):
    df = load_data()

    max_bid = df.loc[df['id'].str.contains('bid'), 'px'].max()
    if agg_level == '1':
        max_bid = int(max_bid)

    return f'{product_id}: {max_bid}'


@app.callback(
    Output('my-table', 'data'),
    Input('update', 'n_intervals'),
)
def update_table(intervals):
    df = load_data()

    return df.to_dict(orient='records')


def load_data():
    conn = sqlite3.connect('./prime_orderbook.db')
    cursor = conn.cursor()

    data = cursor.execute("SELECT * FROM book ORDER BY id + 0 ASC LIMIT 50")

    df = pd.DataFrame(data)

    df.columns = ['index', 'px', 'qty', 'id']
    df = df.sort_values(by=['px'], ascending=False)

    return df


if __name__ == '__main__':
    app.run_server(debug=True)
