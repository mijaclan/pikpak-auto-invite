
# 处理矩阵运算，返回四个哈希值
def processMatrix(matrixList, index):
    # 获取前一个矩阵元素，若为第一个元素则取自己
    prevIndex = index - 1 if index > 0 else 0
    prevMatrix = matrixList[prevIndex]
    centerRow = prevMatrix['row'] // 2 + 1
    centerCol = prevMatrix['column'] // 2 + 1
    centerValue = prevMatrix['matrix'][centerRow][centerCol]
    
    # 获取后一个矩阵元素，若为最后一个元素则取自己
    nextIndex = index + 1 if index + 1 < len(matrixList) else index
    nextMatrix = matrixList[nextIndex]
    modRow = nextIndex % nextMatrix['row']
    modCol = nextIndex % nextMatrix['column']
    modValue = nextMatrix['matrix'][modRow][modCol]
    
    # 获取当前矩阵的特定固定位置元素
    currentMatrix = matrixList[index]
    fixedRow = 3 % currentMatrix['row']
    fixedCol = 7 % currentMatrix['column']
    fixedValue = currentMatrix['matrix'][fixedRow][fixedCol]
    
    # 计算两个值的和与差
    sumValue = extractFirst(centerValue) + extractSecond(fixedValue)
    diffValue = extractFirst(fixedValue) - extractSecond(centerValue)
    
    # 返回四个哈希值
    return [
        hashString(combineValues(extractFirst(centerValue), extractSecond(centerValue))),
        hashString(combineValues(extractFirst(modValue), extractSecond(modValue))),
        hashString(combineValues(extractFirst(fixedValue), extractSecond(fixedValue))),
        hashString(combineValues(sumValue, diffValue))
    ]

# 提取逗号分隔字符串的第一个部分并转换为整数
def extractFirst(value):
    return int(value.split(",")[0])

# 提取逗号分隔字符串的第二个部分并转换为整数
def extractSecond(value):
    return int(value.split(",")[1])

# 将两个整数转换为字符串并用 ^⁣^ 连接
def combineValues(first, second):
    return f"{first}^⁣^{second}"

# 计算字符串的哈希值
def hashString(string):
    hashValue = 0
    for char in string:
        hashValue = limitRange(31 * hashValue + ord(char))
    return hashValue

# 将整数限制在 -2147483648 到 2147483647 之间
def limitRange(value):
    minVal = -2147483648
    maxVal = 2147483647
    if value > maxVal:
        return minVal + (value - maxVal) % (maxVal - minVal + 1) - 1
    if value < minVal:
        return maxVal - (minVal - value) % (maxVal - minVal + 1) + 1
    return value

# 进行字符串拼接并哈希
def combineAndHash(baseString, index):
    return hashString(f"{baseString}⁣{index}")

# 主函数，生成包含矩阵处理结果和字符串拼接哈希的字典
def imgSecret(matrixList, index, baseString):
    return {
        'ca': processMatrix(matrixList, index),
        'f': combineAndHash(baseString, index)
    }
