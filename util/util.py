import const.const as const

def GetFileName(path):
    parts = path.split('/')  # 以'/'为分隔符将路径分割成多个部分
    last_part = parts[-1]  # 获取最后一个部分，即文件名带扩展名
    file_name = last_part.split('.')[0]  # 再以'.'为分隔符分割，取第一个元素就是文件名
    return file_name

def GenCfgId(substance, pointId):
    return "{}_{}".format(substance, pointId)


def GenSubstanceConfigPath(substance):
    return "{}{}_config.txt".format(const.ThresholdConfigPath, substance)


def GenSubstanceDataPath(substance):
    return "{}{}.txt".format(const.DataPath, substance)