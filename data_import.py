import numpy as np

import const.const as const
import model.model as model
import util.util as util
import threshold as thd

# 定义

def ImportData(substanceName):
    points = []
    curves = {}
    path = util.GenSubstanceDataPath(substanceName)
    substance = model.Substance(substanceName, path)
    # 加载配置
    cfgMap = thd.LoadThresholdConfig(substanceName)
    substance.cfgs = cfgMap

    # 加载数据
    with (open(path, 'r') as file):
        lines = file.readlines()
        # 处理第一行数据，放入wave_number数组
        xData = list(map(float, lines[0].split()))
        wave_number = np.array(xData)

        # 从第二行开始处理每一行数据
        for index, line in enumerate(lines[1:]):
            # 读取点
            data = list(map(float, line.split()))
            point = model.Point(index, data[0], data[1], substanceName)

            # 读取曲线
            intensity = data[2:]
            # 无配置则根据默认的阈值生成曲线
            if not point.pointId in substance.cfgs :
                curve = model.Line(point, wave_number, np.array(intensity),
                               [model.LineFill(wave_number, np.array(intensity), const.DefaultThreshold)])
            else :
                curve = model.Line(point, wave_number, np.array(intensity),
                                   substance.cfgs[point.pointId].lineFillList)
            curves[point.pointId] = curve
            # 设置颜色
            point.SetColor(substance.cfgs, curve)
            points.append(point)

    substance.curves = curves
    substance.points = points
    substance.CalPointsNum()

    return substance
