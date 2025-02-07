import numpy as np
import plotly.graph_objects as go
from flask import Flask, render_template_string

app = Flask(__name__)

# 生成示例数据
x = np.linspace(0, 10, 100)
y1 = np.sin(x)  # 曲线图数据
y2 = np.random.randn(100)  # 散点图数据

# 创建散点图和曲线图
scatter_fig = go.Figure(data=go.Scatter(
    x=x,
    y=y2,
    mode='markers',
    name='Random Scatter',
    marker=dict(color='red'),
    customdata=y1,  # 将曲线图的 y 值作为自定义数据
    hovertemplate='X: %{x}<br>Y: %{y}<extra></extra>'
))

curve_fig = go.Figure(data=go.Scatter(
    x=x,
    y=y1,
    mode='lines',
    name='Sine Curve',
    visible=False  # 初始时曲线图不可见
))

# 设置曲线图布局，允许框选操作
curve_fig.update_layout(
    dragmode='select'
)

# 将图形转换为 HTML 字符串，并为散点图和曲线图指定 div ID
scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')
curve_html = curve_fig.to_html(full_html=False, include_plotlyjs=False, div_id='curve-plot')

@app.route('/')
def index():
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Interactive Scatter and Curve Plots</title>
    </head>
    <body>
        <h1>Interactive Scatter and Curve Plots</h1>
        {scatter_html}
        {curve_html}
        <script>
            window.onload = function() {{
                var scatterPlot = document.getElementById('scatter-plot');
                var curvePlot = document.getElementById('curve-plot');

                scatterPlot.on('plotly_click', function(data) {{
                    var point = data.points[0];
                    var newY = point.customdata;
                    curvePlot.data[0].y = newY;
                    curvePlot.data[0].visible = true;
                    Plotly.react('curve-plot', curvePlot.data, curvePlot.layout);
                }});

                curvePlot.on('plotly_selected', function(data) {{
                    var selectedPoints = data.points;
                    if (selectedPoints.length > 0) {{
                        var startX = selectedPoints[0].x;
                        var endX = selectedPoints[selectedPoints.length - 1].x;
                        var inputValue = prompt('您选择的区间是 [' + startX + ', ' + endX + ']，请输入一个数字:');
                        if (inputValue!== null) {{
                            console.log('您输入的数字是: ', inputValue);
                            // 这里可以添加处理输入数字的逻辑
                        }}
                    }}
                }});
            }};
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9898)