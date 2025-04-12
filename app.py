import numpy as np
import plotly.graph_objects as go
from flask import Flask, render_template_string, request, jsonify
import data_import as data
import const.const as const
import point_size as point_size
import model.model as model
import util.util as util
import const.color as cl
import threshold as thd
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
substance = data.ImportData(const.ShowSubstanceName)

# 计算散点图X轴范围，添加偏移量
def CalScatterXRange(points):
    if len(points) == 0:
        logging.debug("[CalScatterXRange]points is empty")
        return 0, 0
    min_x = min([point.locaX for point in points])
    max_x = max([point.locaX for point in points])
    offset = (max_x - min_x) * 0.1  # 10% 的偏移量
    return min_x - offset, max_x + offset

# 计算散点图Y轴范围，添加偏移量
def CalScatterYRange(points):
    if len(points) == 0:
        logging.debug("[CalScatterYRange]points is empty")
        return 0, 0
    min_y = min([point.locaY for point in points])
    max_y = max([point.locaY for point in points])
    offset = (max_y - min_y) * 0.1  # 10% 的偏移量
    return min_y - offset, max_y + offset

# 绘制散点图
def DrawScatter(substance):
    if not substance.points:
        logging.debug("No points in substance for scatter plot.")
        return None
    locaX = np.array([point.locaX for point in substance.points])
    locaY = np.array([point.locaY for point in substance.points])
    colors = [point.color for point in substance.points]
    size = point_size.CalPointSize(substance.pointXNum)
    components = [util.FormatComponent(point.components) for point in substance.points]

    scatter_fig = go.Figure(data=go.Scatter(
        x=locaX,
        y=locaY,
        mode='markers',
        marker=dict(
            color=colors,
            size=size,
            symbol='square'
        ),
        text = components,
        customdata=list(range(len(substance.points))),
        hovertemplate='Components: %{text}<extra></extra>'
    ))

    xMin, xMax = CalScatterXRange(substance.points)
    yMin, yMax = CalScatterYRange(substance.points)
    scatter_fig.update_xaxes(range=[xMin, xMax])
    scatter_fig.update_yaxes(range=[yMin, yMax])

    plot_height = 800
    scatter_fig.update_layout(
        xaxis=dict(scaleanchor='y', scaleratio=1),
        yaxis=dict(constrain='domain'),
        title='Intensity',
        xaxis_title='X',
        yaxis_title='Y',
        margin=dict(l=0, r=0, t=50, b=0),
        height=plot_height
    )

    return scatter_fig

# 绘制曲线图
def drawInnerLine(substance, locaInd):
    if locaInd >= len(substance.curves):
        logging.debug(f"Invalid locaInd {locaInd} for curve plot.")
        return None
    curve = substance.curves[locaInd]
    curve_fig = go.Figure(data=go.Scatter(
        x=curve.x,
        y=curve.y,
        mode='lines',
        line=dict(width=0.5)
    ))
    plot_height = 800
    curve_fig.update_layout(
        title=f'Intensity Curve for Point ({substance.points[locaInd].locaX}, {substance.points[locaInd].locaY})',
        xaxis_title='Wave Number',
        yaxis_title='Intensity',
        dragmode='select',
        height=plot_height
    )
    return curve_fig

@app.route('/')
def index():
    scatter_fig = DrawScatter(substance)
    if scatter_fig is None:
        scatter_html = "<p>No scatter plot data available.</p>"
    else:
        scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Interactive Scatter and Curve Plots</title>
        <style>
            .plot-container {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
            }
            .plot {
                width: 48%;
            }
            #myModal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
            }
            .modal-content {
                background-color: #fefefe;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 30%;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }
            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Interactive Scatter and Curve Plots</h1>
        <div class="plot-container">
            <div class="plot" id="scatter-plot">
                {{ scatter_html|safe }}
            </div>
            <div class="plot" id="curve-plot"></div>
        </div>
        <div id="myModal" class="modal">
            <div class="modal-content">
                <span class="close">&times;</span>
                <p><strong>xMin:</strong> <span id="xMinValue"></span></p>
                <p><strong>xMax:</strong> <span id="xMaxValue"></span></p>
                <p><strong>阈值:</strong> <input type="text" id="thresholdInput"></p>
                <p><strong>颜色:</strong> 
                    <select id="colorSelect">
                        <option value="#FF0000">红色</option>
                        <option value="#FFA500">橙色</option>
                        <option value="#FFFF00">黄色</option>
                        <option value="#00FF00">绿色</option>
                        <option value="#00FFFF">青色</option>
                        <option value="#0000FF">蓝色</option>
                        <option value="#FF00FF">紫色</option>
                    </select>
                </p>
                <button onclick="submitData()">提交</button>
            </div>
        </div>
        <script>
            var scatterPlot = document.getElementById('scatter-plot');
            var locaIndGlobal;
            if (scatterPlot) {
                scatterPlot.on('plotly_click', function(data) {
                    var point = data.points[0];
                    locaIndGlobal = point.customdata;
                    fetch('/get_curve', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ locaInd: locaIndGlobal })
                    })
                   .then(response => response.json())
                   .then(data => {
                        var curvePlotDiv = document.getElementById('curve-plot');
                        curvePlotDiv.innerHTML = data.curve_html;
                        var curvePlot = Plotly.react('curve-plot', JSON.parse(data.curve_json), {});
                        curvePlotDiv.on('plotly_selected', function(selectedData) {
                            var xRange = selectedData.range.x;
                            var startX = xRange[0];
                            var endX = xRange[1];
                            var curveData = JSON.parse(data.curve_data)
                            var selectedPoints = [];
                            for (var i = 0; i < curveData.x.length; i++) {
                                if (curveData.x[i] >= startX && curveData.x[i] <= endX) {
                                    selectedPoints.push({
                                        x: curveData.x[i],
                                        y: curveData.y[i]
                                    });
                                }
                            }
                            document.getElementById('xMinValue').textContent = startX;
                            document.getElementById('xMaxValue').textContent = endX;
                            var modal = document.getElementById('myModal');
                            modal.style.display = "block";
                        });
                    });
                });
            }

            var span = document.getElementsByClassName("close")[0];
            if (span) {
                span.onclick = function() {
                    var modal = document.getElementById('myModal');
                    modal.style.display = "none";
                }
            }

            window.onclick = function(event) {
                var modal = document.getElementById('myModal');
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            function submitData() {
                var startX = parseFloat(document.getElementById('xMinValue').textContent);
                var endX = parseFloat(document.getElementById('xMaxValue').textContent);
                var threshold = parseFloat(document.getElementById('thresholdInput').value);
                var color = document.getElementById('colorSelect').value;
                if (!isNaN(threshold)) {
                    fetch('/update_color', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            locaInd: locaIndGlobal,
                            startX: startX,
                            endX: endX,
                            threshold: threshold,
                            color: color
                        })
                    })
                   .then(response => response.json())
                   .then(data => {
                        var scatterPlotDiv = document.getElementById('scatter-plot');
                        scatterPlotDiv.innerHTML = data.scatter_html;
                        var modal = document.getElementById('myModal');
                        modal.style.display = "none";
                    });
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, scatter_html=scatter_html)

@app.route('/get_curve', methods=['POST'])
def get_curve():
    data = request.get_json()
    locaInd = data['locaInd']
    curve_fig = drawInnerLine(substance, locaInd)
    if curve_fig is None:
        return jsonify({
            'curve_html': "<p>No curve plot data available.</p>",
            'curve_json': '{}',
            'curve_data': '{}'
        })
    curve_html = curve_fig.to_html(full_html=False, include_plotlyjs=False, div_id='curve-plot')
    curve_data = substance.curves[locaInd]
    str_data = curve_data.__repr__()
    return jsonify({
        'curve_html': curve_html,
        'curve_json': curve_fig.to_json(),
        'curve_data': str_data
    })

@app.route('/update_color', methods=['POST'])
def update_color():
    data = request.get_json()
    locaInd = data['locaInd']
    startX = data['startX']
    endX = data['endX']
    threshold = data['threshold']
    color = data['color']
    cfgId = util.GenCfgId(substance, locaInd)
    point = substance.points[locaInd]

    if locaInd in substance.cfgs:
        config = substance.cfgs[locaInd]
    else:
        config = model.ThresholdConfig(
            cfgId=cfgId,
            substance=substance.name,
            locaX=point.locaX,
            locaY=point.locaY,
            locaInd=locaInd,
            lineFillList=[],
            color=cl.InvalidColor
        )
    newLineFillList = thd.AddFillLine(model.LineFill(startX, endX, threshold), config.lineFillList)
    config.lineFillList = newLineFillList
    substance.curves[locaInd].lineFillList = config.lineFillList

    substance.points[locaInd].SetColor(substance.cfgs, substance.curves[locaInd])
    thd.ThresholdConfigMap[locaInd] = config
    thd.SaveThresholdConfig(thd.ThresholdConfigMap, substance.name)

    scatter_fig = DrawScatter(substance)
    if scatter_fig is None:
        scatter_html = "<p>No scatter plot data available after update.</p>"
    else:
        scatter_html = scatter_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='scatter-plot')
    return jsonify({
        'scatter_html': scatter_html
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9898, debug=True)