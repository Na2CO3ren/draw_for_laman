import  json

import numpy as np
import const.color as color

# 物质
class Substance:
    def __init__(self, name: str, path: str, points = [], curves = dict(), cfgs = dict(), pointXNum = 0):
        self.name = name
        self.path = path
        self.points = points
        self.curves = curves
        self.cfgs = cfgs
        self.pointXNum = pointXNum

    def __repr__(self):
        json_str = json.dumps(self.__dict__, cls=NumpyJSONEncoder)
        return json_str

    def CalPointsNum(self):
        if len(self.points) == 0 :
            return
        targetPoint = self.points[0]
        pointXNum = 0
        for point in self.points:
            if point.locaY == targetPoint.locaY:
                pointXNum += 1
        self.pointXNum = pointXNum


# 图上的数据点
class Point:
    def __init__(self, pointId, locaX, locaY, substanceName, color = color.InvalidColor):
        self.pointId = pointId
        self.locaX = locaX
        self.locaY = locaY
        self.color = color
        self.substanceName = substanceName

    def __repr__(self):
        json_str = json.dumps(self.__dict__, cls=NumpyJSONEncoder)
        return json_str

    def SetColor(self, configMap):
        self.color = color.InvalidColor
        if self.pointId in configMap:
            self.color = configMap[self.pointId].color



# 曲线填充
class LineFill:
    def __init__(self, rangeX,rangeY,threshold):
        self.rangeX = rangeX
        self.rangeY = rangeY
        self.threshold = threshold

    def __repr__(self):
        json_str = json.dumps(self.__dict__, cls=NumpyJSONEncoder)
        return json_str

    def IsValid(self):
        for y in self.rangeY:
            if y < self.threshold:
                return False
        return True


# 曲线
class Line:
    def __init__(self, point:Point, x,y,LineFillList = []):
        self.point = point
        self.x = x
        self.y = y
        self.lineFillList = LineFillList
        self.valid = True
        self.ResetValid()

    def __repr__(self):
        json_str = json.dumps(self.__dict__, cls=NumpyJSONEncoder)
        return json_str

    def ResetValid(self):
        self.valid = True
        for lineFill in self.lineFillList:
            if not lineFill.IsValid():
                self.valid = False
                break
#
# # 图
# class Image:
#     def __init__(self, pointList, x,y,colors):
#         self.pointList = pointList
#         self.y = y
#         self.x = x
#         self.colors = colors
#
#     def __repr__(self):
#         json_str = json.dumps(self.__dict__)
#         return json_str

# 图
class ThresholdConfig:
    def __init__(self,cfgId, substance, locaX,locaY,locaInd, lineFillList, color):
        self.cfgId = cfgId
        self.substance = substance
        self.locaX = locaX
        self.locaY = locaY
        self.locaInd = locaInd
        self.lineFillList = lineFillList
        self.color = color

    def __repr__(self):
        json_str = json.dumps(self.__dict__, cls=NumpyJSONEncoder)
        return json_str




class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, LineFill):
            return {"rangeX": obj.rangeX, "rangeY": obj.rangeY, "threshold":obj.threshold}
        if isinstance(obj, Point):
            return {"locaX": obj.locaX, "locaY": obj.locaY, "color": obj.color, "substanceName": obj.substanceName}

        return super().default(obj)