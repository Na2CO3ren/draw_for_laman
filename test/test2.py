import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 生成示例数据
x = list(range(10))
y = [i**2 for i in x]
data = {'x': x, 'y': y}
df = pd.DataFrame(data)

# 创建 Dash 应用
app = dash.Dash(__name__)

# 定义应用布局
app.layout = html.Div([
    dcc.Graph(
        id='line-plot',
        figure=px.line(df, x='x', y='y')
    ),
    html.Div(id='selected-points-info')
])

# 定义回调函数，处理 plotly_selected 事件
@app.callback(
    Output('selected-points-info', 'children'),
    Input('line-plot', 'selectedData')
)
def display_selected_points(selectedData):
    if selectedData is not None:
        points = selectedData['points']
        info = []
        for point in points:
            info.append(f"选中点坐标: ({point['x']}, {point['y']})")
        return html.Ul([html.Li(item) for item in info])
    return html.P("未选中任何数据点。")

if __name__ == '__main__':
    app.run_server(debug=True)