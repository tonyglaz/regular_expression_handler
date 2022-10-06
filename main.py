from collections import deque
import itertools

# Parser
text = ' '
index = 0
line = 0
pos = 0


def Error(textError):
    print("\nСтрока", line, ", символ ", pos, ": ", textError)
    quit()


def NextSymbol():
    global index, pos
    if index == len(text):
        quit()
    elif text[index] == '{':
        index += 1
        pos += 1
    elif text[index] == '}':
        index += 1
        pos += 1
    elif text[index] == ',':
        index += 1
        pos += 1
    elif text[index] == '-':
        index += 1
        pos += 1
    elif text[index] == '*':
        index += 1
        pos += 1


def Init(source):
    global text, index, pos
    text = source
    index = 0
    pos = 1

    '''if text[index] == '-' or text[index] == '{':
        index += 1'''
    if text[index] == '}' or text[index] == '*' or text[index] == ',':
        Error("Выражение должно начинаться с '{', 0 или 1")
    if text[index] != '1' and text[index] != '0' and text[index] != '{':
        Error("Неизвестный символ")


def Accept(expected):
    if text[index] != expected:
        Error("Ожидалось " + expected)
    NextSymbol()


def Line10():
    global index, pos
    startIndex = index

    while text[index] == '1' or text[index] == '0':
        index += 1
        pos += 1
        if index == len(text):
            break
    return text[startIndex: index]  # index - startIndex + 1 мб


def ParseOr():
    result = []

    result = RegexFunc()
    if text[index] != ',':
        return result
    else:
        tempElement = ['type', 'justline']
        tempRegex = []
        temp = []
        tempElement[0] = 'OR'
        while text[index] == ',':
            NextSymbol()
            tempRegex.append(RegexFunc())
        tempRegex.insert(0, result)
        # print("TempRegex: ", tempRegex)
        tempElement[1] = tempRegex
        temp.append(tempElement)
        return temp


def Element():
    newElement = ['type', '']
    temp = []
    if text[index] == '1' or text[index] == '0':
        newElement[0] = 'justLine'
        newElement[1] = Line10()
    # NextSymbol()
    elif text[index] == '{':
        newElement[0] = 'repeat'
        NextSymbol()
        temp = ParseOr()
        # print("Temp: ", temp)
        newElement[1] = temp
        Accept('}')
        Accept('*')
    elif text[index] == '-':
        temp.append('-')
        NextSymbol()
    return newElement


def RegexFunc():
    result = []
    temp = []
    while text[index] == '1' or text[index] == '0' or text[index] == '{' or text[index] == '-':
        temp.append(Element())
        if index == len(text):
            break
    result = temp
    return result

    # NFA


def AddStatesElement(startIndex, nfa, element):
    currentIndex = startIndex
    nextIndex = -1

    if element[0] == 'justLine':
        for symbol in element[1]:
            nextIndex = len(nfa)
            nfa.append([-1, -1, -1])

            if symbol == '0':
                nfa[currentIndex][0] = nextIndex
            if symbol == '1':
                nfa[currentIndex][1] = nextIndex
            currentIndex = nextIndex
        return currentIndex
    if element[0] == 'OR':
        nextIndex = len(nfa)
        nfa.append([-1, -1, -1])

        for regex in element[1]:
            currentIndex = AddStatesRegex(startIndex, nfa, regex)
            nfa[currentIndex][2] = nextIndex
        return nextIndex
    if element[0] == 'repeat':
        currentIndex = AddStatesRegex(startIndex, nfa, element[1])
        nfa[currentIndex][2] = startIndex
        return startIndex
    return currentIndex


def AddStatesRegex(startIndex, nfa, peace):
    currentIndex = startIndex

    for element in peace:
        currentIndex = AddStatesElement(currentIndex, nfa, element)
    return currentIndex


def BuildNFA(peace):
    nfa = ['final', []]
    zeroState = [-1, -1, -1]
    nfa[1].append(zeroState)
    nfa[0] = AddStatesRegex(0, nfa[1], peace)
    return nfa

    # Generator


d = deque()


def ConfigZero(config, nfa):
    tempList = [0] * len(nfa[1])
    tempStr = config[1]
    for i in range(len(config[0])):
        if config[0][i] == 1:
            if nfa[1][i][0] != -1:
                tempList[nfa[1][i][0]] = 1
                tempStr += '0'
    return (tempList, tempStr)


def ConfigOne(config, nfa):
    tempList = [0] * len(nfa[1])
    tempStr = config[1]
    for i in range(len(config[0])):
        if config[0][i] == 1:
            if nfa[1][i][1] != -1:  # проверка перехода по 1
                tempList[nfa[1][i][1]] = 1
                tempStr += '1'

    return (tempList, tempStr)


def EmptyConfig(config, nfa):
    tempList = config[0]
    tempStr = config[1]
    for i in range(len(config[0])):
        j = i
        if config[0][j] == 1:
            while nfa[1][j][2] != -1:
                if tempList[nfa[1][j][2]] == 1:
                    break
                tempList[nfa[1][j][2]] = 1
                j = nfa[1][j][2]
    return (tempList, tempStr)


def ConfigMain(nfa):
    zeroConfig = ([0] * len(nfa[1]), '')
    zeroConfig[0][0] = 1
    finishState = nfa[0]
    d.append(zeroConfig)
    resultRegex = ''
    while len(d):
        currentConfig = d.pop()
        cZ = EmptyConfig(ConfigZero(currentConfig, nfa), nfa)
        cO = EmptyConfig(ConfigOne(currentConfig, nfa), nfa)

        if cO[0][finishState] != 0:
            yield resultRegex + cO[1]
        if cZ[0][finishState] != 0:
            yield resultRegex + cZ[1]

        if cZ[0] != [0] * len(nfa[1]):
            d.append(cZ)
        if cO[0] != [0] * len(nfa[1]):
            d.append(cO)


# Main
print('Введите регулярное выражение и желаемую мощность регулярного множества: ')  # 0110{1{11,0}*}* 5
temp = input().split()
regex = temp[0]
M = int(temp[1])
Init(regex)
mainRegex = RegexFunc()
mainNFA = BuildNFA(mainRegex)

print('Синтаксичекое дерево: ')
print(mainRegex)
print('НКА: ')
print(mainNFA)
print('Регулярное множество: ')
print(list(itertools.islice(ConfigMain(mainNFA), M)))
