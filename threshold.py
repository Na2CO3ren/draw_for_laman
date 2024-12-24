import json
import model.model as model
import const.const as const
import util.util as util
import os.path

DefaultThreshold = 120

ThresholdConfigMap = {}

# 将config写入文件中
def SaveThresholdConfig(config_map):
    serializable_config_map = {cfgId: vars(config) for cfgId, config in config_map.items()}
    with open(const.ThresholdConfigPath, 'w') as file:
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
    new_x = new_line_fill.rangeX
    exist_x = existing_line_fill.rangeX
    if (new_x[0] <= exist_x[-1] and new_x[0] >= exist_x[0]) or (new_x[-1] <= exist_x[-1] and new_x[-1] >= exist_x[0]):
        return True

    return False


def AddFillLine(new_line_fill, line_fills):
    newFillLineList = []
    for existLine in line_fills:
        if not check_overlap(new_line_fill, existLine) :
            newFillLineList.append(existLine)
    newFillLineList.append(new_line_fill)
    return newFillLineList