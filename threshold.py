import json
import model.model as model
import const.const as const
import numpy as np
import util.util as util
import os.path

ThresholdConfigMap = {}

# 将config写入文件中
def SaveThresholdConfig(config_map, substanceName):
    cfgPath = util.GenSubstanceConfigPath(substanceName)
    serializable_config_map = {int(locateId): vars(config) for locateId, config in config_map.items()}
    with open(cfgPath, 'w') as file:
        json.dump(serializable_config_map, file, cls=model.NumpyJSONEncoder)


# 加载threshold的配置
def LoadThresholdConfig(substanceName):
    global ThresholdConfigMap
    config_map = {}

    configPath = util.GenSubstanceConfigPath(substanceName)

    if not os.path.exists(configPath):
        return config_map
    file_size = os.path.getsize(configPath)
    if file_size == 0:
        return config_map
    with open(configPath, 'r') as file:
        loaded_dict = json.load(file)
        for cfgId, config_dict in loaded_dict.items():
            # 从字典数据重新创建ThresholdConfig类实例
            cfgId = cfgId
            substance = config_dict["substance"]
            color = config_dict["color"]
            locaX = config_dict["locaX"]
            locaY = config_dict["locaY"]
            locaInd = config_dict["locaInd"]
            lineFillList_data = config_dict["lineFillList"]
            lineFillList = []
            for line_fill_dict in lineFillList_data:
                # 解析LineFill部分
                rangeX = line_fill_dict["rangeX"]
                rangeY = line_fill_dict["rangeY"]
                threshold = line_fill_dict["threshold"]
                lineFill = model.LineFill(rangeX, rangeY, threshold)
                lineFillList.append(lineFill)
            threshold_config = model.ThresholdConfig(cfgId, substance, locaX, locaY, locaInd, lineFillList, color)

            config_map[locaInd] = threshold_config
    ThresholdConfigMap = config_map
    return config_map


def check_overlap(new_line_fill, existing_line_fill):
    if len(new_line_fill.rangeX) == 0 or len(existing_line_fill.rangeX) == 0:
        return False
    new_x = new_line_fill.rangeX
    exist_x = existing_line_fill.rangeX
    if ((new_x[0] >= exist_x[0] and new_x[-1] <= exist_x[-1]) or
            (new_x[0] <= exist_x[0] <= new_x[-1]) or
            (new_x[0] <= exist_x[-1] <= new_x[-1]) or
            (new_x[0]<= exist_x[0] and new_x[-1] >= exist_x[-1])):
        return True

    return False


def AddFillLine(new_line_fill, line_fills):
    newFillLineList = []
    for existLine in line_fills:
        if not check_overlap(new_line_fill, existLine) :
            newFillLineList.append(existLine)
    newFillLineList.append(new_line_fill)
    return newFillLineList

def MatchSubstance(line_data) :
    matchedSubstance = []
    for substance, featureData in const.SubstanceFeatureMap.items():
        for data in line_data:
            for feature in featureData:
                if abs(feature - data) <= 2:
                    matchedSubstance.append(substance)
    return list(set(matchedSubstance))