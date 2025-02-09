from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import plotly.express as px
import pandas as pd

# 生成示例数据
x = list(range(100))
y = [i**2 for i in x]
data = {'x': x, 'y': y}
df = pd.DataFrame(data)

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 生成 Plotly 图表的 HTML 代码，添加 config 参数
fig = px.line(df, x='x', y='y', title='曲线图')
fig.update_layout(dragmode='select')  # 开启选择模式
plot_div = fig.to_html(full_html=False, config={'modeBarButtonsToAdd': ['select2d', 'lasso2d']})
# 将 plot_div 输出到文件
with open('plot_div_output.html', 'w', encoding='utf-8') as f:
    f.write(plot_div)

# 定义 HTML 模板
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>曲线图选择区间示例</title>
    <script src="https://cdn.plot.ly/plotly-2.20.0.min.js"></script>
    {{ plot_div|safe }}
    <script>
        window.onload = function() {
            if (typeof Plotly === 'undefined') {
                console.error('Plotly 库未正确加载');
                return;
            }
            const elementId = '{{ plot_div.split("<div id=\\"")[1].split("\\"")[0] }}'
            console.log('elementId:', elementId);
            const graphElement = document.getElementById(elementId);
            console.log('获取到的图表元素:', graphElement);
            if (!graphElement) {
                console.error('未找到图表元素');
                return;
            }

            function handleSelection(selectedData) {
                console.log('handleSelection 函数被调用，选择的数据:', selectedData);
                const x_values = [];
                const y_values = [];
                selectedData.points.forEach(point => {
                    x_values.push(point.x);
                    y_values.push(point.y);
                });
                const data = {x: x_values, y: y_values};
                console.log('准备发送的数据:', data);
                // 发送 AJAX 请求到后端处理选择的数据
                fetch('/process_selection', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
               .then(response => {
                    console.log('响应状态:', response.status);
                    if (!response.ok) {
                        throw new Error('网络响应不正常');
                    }
                    return response.json();
                })
               .then(result => {
                    console.log('后端返回结果:', result);
                    // 弹出窗口显示选择的数据点
                    alert(result.message);
                })
               .catch(error => {
                    console.error('请求出错:', error);
                });
            }

            // 直接在 DOM 元素上监听 plotly_selected 事件
            graphElement.on('plotly_selected', function(event) {
                console.log('检测到选择事件:', event.detail);
                handleSelection(event.detail);
            });
        };
    </script>
</head>
<body>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template, plot_div=plot_div)

@app.route('/process_selection', methods=['POST'])
def process_selection():
    try:
        data = request.get_json()
        print('接收到的数据:', data)
        selected_df = pd.DataFrame(data)
        message = "选择的数据点:\n" + selected_df.to_csv(sep='\t', na_rep='nan')
        print('处理后返回的消息:', message)
        return jsonify({'message': message})
    except Exception as e:
        print(f"后端处理出错: {e}")
        return jsonify({'message': f"后端处理出错: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)