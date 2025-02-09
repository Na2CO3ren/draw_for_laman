import numpy as np
import plotly.graph_objects as go
from flask import Flask, render_template_string, request, jsonify
import page_show as show
import data_import as data
import const.const as const
import point_size as point_size


app = Flask(__name__)
substance = data.ImportData(const.ShowSubstanceName)

# 计算散点大小
# def CalPointSize(pointNum):
#     return 10

# 计算散点图X轴范围，添加偏移量
def CalScatterXRange(points):
    if len(points) == 0:
        print("[CalScatterXRange]points is empty")
        return 0, 0
    min_x = min([point.locaX for point in points])
    max_x = max([point.locaX for point in points])
    offset = (max_x - min_x) * 0.1  # 5% 的偏移量
    return min_x - offset, max_x + offset

# 计算散点图Y轴范围，添加偏移量
def CalScatterYRange(points):
    if len(points) == 0:
        print("[CalScatterYRange]points is empty")
        return 0, 0
    min_y = min([point.locaY for point in points])
    max_y = max([point.locaY for point in points])
    offset = (max_y - min_y) * 0.1  # 5% 的偏移量
    return min_y - offset, max_y + offset

# 绘制散点图
def DrawScatter(substance):
    locaX = np.array([point.locaX for point in substance.points])
    locaY = np.array([point.locaY for point in substance.points])
    colors = [point.color for point in substance.points]
    size = point_size.CalPointSize(substance.pointXNum)

    scatter_fig = go.Figure(data=go.Scatter(
        x=locaX,
        y=locaY,
        mode='markers',
        marker=dict(
            color=colors,
            size=size,
            symbol='square'  # 设置散点形状为正方形
        ),
        customdata=list(range(len(substance.points))),  # 用于传递点的索引
        hovertemplate='X: %{x}<br>Y: %{y}<extra></extra>'
    ))

    xMin, xMax = CalScatterXRange(substance.points)
    yMin, yMax = CalScatterYRange(substance.points)
    scatter_fig.update_xaxes(range=[xMin, xMax])
    scatter_fig.update_yaxes(range=[yMin, yMax])

    # 调整布局参数，去除不必要的边距
    plot_height = 800  # 统一设置高度
    scatter_fig.update_layout(
        xaxis=dict(scaleanchor='y', scaleratio=1),  # 设置散点图边框为正方形
        yaxis=dict(constrain='domain'),
        title='Intensity',
        xaxis_title='X',
        yaxis_title='Y',
        margin=dict(l=0, r=0, t=50, b=0),  # 调整边距，使散点更靠近边缘
        height=plot_height
    )

    return scatter_fig

# 绘制曲线图
def drawInnerLine(substance, locaInd):
    curve = substance.curves[locaInd]
    curve_fig = go.Figure(data=go.Scatter(
        x=curve.x,
        y=curve.y,
        mode='lines',
        line=dict(width=0.5)
    ))
    plot_height = 800  # 统一设置高度
    curve_fig.update_layout(
        title=f'Intensity Curve for Point ({substance.points[locaInd].locaX}, {substance.points[locaInd].locaY})',
        xaxis_title='Wave Number',
        yaxis_title='Intensity',
        dragmode='select',  # 允许框选操作
        height=plot_height
    )
    return curve_fig

@app.route('/')
def index():
    scatter_fig = DrawScatter(substance)
    scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')
    # 将 plot_div 输出到文件
    with open('plot_div_output.html', 'w', encoding='utf-8') as f:
        f.write(scatter_html)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Interactive Scatter and Curve Plots</title>
        <style>
            .plot-container {{
                display: flex;
                flex-direction: row;
                justify-content: space-between;
            }}
            .plot {{
                width: 48%; /* 为了留出一些间距 */
            }}
        </style>
    </head>
    <body>
        <h1>Interactive Scatter and Curve Plots</h1>
        <div class="plot-container">
            <div class="plot" id="scatter-plot">
                {scatter_html}
            </div>
            <div class="plot" id="curve-plot"></div>
        </div>
        <script>
            var scatterPlot = document.getElementById('scatter-plot');
            console.log('scatterPlot',scatterPlot)
            scatterPlot.on('plotly_click', function(data) {{
                var point = data.points[0];
                var locaInd = point.customdata;
                // 发送请求获取曲线图数据
                fetch('/get_curve', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ locaInd: locaInd }})
                }})
               .then(response => response.json())
               .then(data => {{
                    var curvePlotDiv = document.getElementById('curve-plot');
                    console.log('curvePlotDiv',curvePlotDiv)
                    curvePlotDiv.innerHTML = data.curve_html;
                    var curvePlot = Plotly.react('curve-plot', JSON.parse(data.curve_json), {{}});
                    console.log('curvePlot',curvePlot)
                    curvePlotDiv.on('plotly_selected', function(selectedData) {{
                        console.log('plotly_selected!!!!',selectedData)
                        var selectedPoints = selectedData.points;
                        if (selectedPoints.length > 0) {{
                            var startX = selectedPoints[0].x;
                            var endX = selectedPoints[selectedPoints.length - 1].x;
                            var threshold = prompt('请输入阈值:');
                            var color = prompt('请输入颜色:');
                            if (threshold!== null && color!== null) {{
                                // 发送请求更新散点颜色
                                fetch('/update_color', {{
                                    method: 'POST',
                                    headers: {{
                                        'Content-Type': 'application/json'
                                    }},
                                    body: JSON.stringify({{
                                        locaInd: locaInd,
                                        startX: startX,
                                        endX: endX,
                                        threshold: parseFloat(threshold),
                                        color: color
                                    }})
                                }})
                               .then(response => response.json())
                               .then(data => {{
                                    var scatterPlotDiv = document.getElementById('scatter-plot');
                                    scatterPlotDiv.innerHTML = data.scatter_html;
                                }});
                            }}
                        }}
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/get_curve', methods=['POST'])
def get_curve():
    data = request.get_json()
    locaInd = data['locaInd']
    curve_fig = drawInnerLine(substance, locaInd)
    curve_html = curve_fig.to_html(full_html=False, include_plotlyjs=False, div_id='curve-plot')
    return jsonify({
        'curve_html': curve_html,
        'curve_json': curve_fig.to_json()
    })

@app.route('/update_color', methods=['POST'])
def update_color():
    data = request.get_json()
    locaInd = data['locaInd']
    startX = data['startX']
    endX = data['endX']
    threshold = data['threshold']
    color = data['color']

    # 更新散点颜色逻辑
    for point in substance.points:
        if startX <= point.locaX <= endX and point.locaY > threshold:
            point.color = color

    scatter_fig = DrawScatter(substance)
    scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')
    return jsonify({
        'scatter_html': scatter_html
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9898)