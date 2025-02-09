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

# 计算散点图X轴范围
def CalScatterXRange(points):
    if len(points) == 0:
        print("[CalScatterXRange]points is empty")
        return 0, 0
    min_x = min([point.locaX for point in points])
    max_x = max([point.locaX for point in points])
    return min_x, max_x

# 计算散点图Y轴范围
def CalScatterYRange(points):
    if len(points) == 0:
        print("[CalScatterYRange]points is empty")
        return 0, 0
    min_y = min([point.locaY for point in points])
    max_y = max([point.locaY for point in points])
    return min_y, max_y

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
            symbol='square'
        ),
        customdata=list(range(len(substance.points))),
        hovertemplate='X: %{x}<br>Y: %{y}<extra></extra>'
    ))

    xMin, xMax = CalScatterXRange(substance.points)
    yMin, yMax = CalScatterYRange(substance.points)
    scatter_fig.update_xaxes(range=[xMin, xMax])
    scatter_fig.update_yaxes(range=[yMin, yMax])

    scatter_fig.update_layout(
        xaxis=dict(scaleanchor='y', scaleratio=1),
        yaxis=dict(constrain='domain'),
        title='Intensity',
        xaxis_title='X',
        yaxis_title='Y',
        margin=dict(l=0, r=0, t=50, b=0),
        height=800
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
    curve_fig.update_layout(
        title=f'Intensity Curve for Point ({substance.points[locaInd].locaX}, {substance.points[locaInd].locaY})',
        xaxis_title='Wave Number',
        yaxis_title='Intensity',
        dragmode='select'
    )
    return curve_fig

@app.route('/')
def index():
    scatter_fig = DrawScatter(substance)
    scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')
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
                width: 48%;
            }}
            /* 模态框样式 */
            .modal {{
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
            }}
            .modal-content {{
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 30%;
            }}
            .close {{
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }}
            .close:hover,
            .close:focus {{
                color: black;
                text-decoration: none;
                cursor: pointer;
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
        <!-- 模态框 -->
        <div id="myModal" class="modal">
            <div class="modal-content">
                <span class="close">&times;</span>
                <label for="threshold">阈值:</label>
                <input type="number" id="threshold" name="threshold"><br>
                <label for="color">颜色:</label>
                <input type="text" id="color" name="color"><br>
                <button id="submitBtn">提交</button>
            </div>
        </div>
        <script>
            var scatterPlot = document.getElementById('scatter-plot');
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
                    curvePlotDiv.innerHTML = data.curve_html;
                    var curvePlot = Plotly.react('curve-plot', JSON.parse(data.curve_json), {{}});
                    curvePlot.on('plotly_selected', function(selectedData) {{
                        var selectedPoints = selectedData.points;
                        if (selectedPoints.length > 0) {{
                            var startX = selectedPoints[0].x;
                            var endX = selectedPoints[selectedPoints.length - 1].x;
                            // 显示模态框
                            var modal = document.getElementById('myModal');
                            modal.style.display = "block";

                            // 获取提交按钮并添加点击事件
                            var submitBtn = document.getElementById('submitBtn');
                            submitBtn.onclick = function() {{
                                var threshold = parseFloat(document.getElementById('threshold').value);
                                var color = document.getElementById('color').value;
                                if (!isNaN(threshold) && color!== '') {{
                                    // 发送请求更新散点颜色和曲线图
                                    fetch('/update_curve', {{
                                        method: 'POST',
                                        headers: {{
                                            'Content-Type': 'application/json'
                                        }},
                                        body: JSON.stringify({{
                                            locaInd: locaInd,
                                            startX: startX,
                                            endX: endX,
                                            threshold: threshold,
                                            color: color
                                        }})
                                    }})
                                   .then(response => response.json())
                                   .then(data => {{
                                        curvePlotDiv.innerHTML = data.curve_html;
                                        Plotly.react('curve-plot', JSON.parse(data.curve_json), {{}});
                                        // 关闭模态框
                                        modal.style.display = "none";
                                    }});
                                }}
                            }};

                            // 获取关闭按钮并添加点击事件
                            var span = document.getElementsByClassName("close")[0];
                            span.onclick = function() {{
                                modal.style.display = "none";
                            }};

                            // 点击模态框外部关闭模态框
                            window.onclick = function(event) {{
                                if (event.target == modal) {{
                                    modal.style.display = "none";
                                }}
                            }};
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

@app.route('/update_curve', methods=['POST'])
def update_curve():
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

    # 重新绘制曲线图并标记选择区间和阈值
    curve = substance.curves[locaInd]
    curve_fig = go.Figure(data=go.Scatter(
        x=curve.x,
        y=curve.y,
        mode='lines',
        line=dict(width=0.5)
    ))
    # 添加选择区间标记
    curve_fig.add_shape(
        type="rect",
        x0=startX,
        y0=min(curve.y),
        x1=endX,
        y1=max(curve.y),
        fillcolor="gray",
        opacity=0.2,
        line_width=0
    )
    # 添加阈值标记
    curve_fig.add_hline(y=threshold, line_dash="dash", line_color=color)

    curve_fig.update_layout(
        title=f'Intensity Curve for Point ({substance.points[locaInd].locaX}, {substance.points[locaInd].locaY})',
        xaxis_title='Wave Number',
        yaxis_title='Intensity',
        dragmode='select'
    )

    curve_html = curve_fig.to_html(full_html=False, include_plotlyjs=False, div_id='curve-plot')
    return jsonify({
        'curve_html': curve_html,
        'curve_json': curve_fig.to_json()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9898)