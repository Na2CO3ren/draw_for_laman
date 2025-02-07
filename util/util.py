import const.const as const

def GetFileName(path):
    parts = path.split('/')  # 以'/'为分隔符将路径分割成多个部分
    last_part = parts[-1]  # 获取最后一个部分，即文件名带扩展名
    file_name = last_part.split('.')[0]  # 再以'.'为分隔符分割，取第一个元素就是文件名
    return file_name

def GenCfgId(substance, pointId):
    return "{}_{}".format(substance.name, pointId)


def GenSubstanceConfigPath(substance):
    return "{}{}_config.txt".format(const.ThresholdConfigPath, substance)


def GenSubstanceDataPath(substance):
    return "{}{}.txt".format(const.DataPath, substance)



def hex_to_rgb(hex_color):
    """将十六进制颜色代码转换为 RGB 元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """将 RGB 元组转换为十六进制颜色代码"""
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def MixColors(hex_colors):
    """混合多种十六进制颜色"""
    total_r, total_g, total_b = 0, 0, 0
    num_colors = len(hex_colors)

    for hex_color in hex_colors:
        r, g, b = hex_to_rgb(hex_color)
        total_r += r
        total_g += g
        total_b += b

    # 计算平均值
    avg_r = int(total_r / num_colors)
    avg_g = int(total_g / num_colors)
    avg_b = int(total_b / num_colors)

    return rgb_to_hex(avg_r, avg_g, avg_b)

def FormatComponent(components):
    result = ''
    for component in components:
        result = result + component + '\n'
    return result