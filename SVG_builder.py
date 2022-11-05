import svgwrite
import math
from itertools import product
import re
import os

from utils import *

from file_checker import *

def main_SVGs(self, final_domain, final_problem):

    file_checker_return = checker(self, final_domain, final_problem)

    predicatesString = file_checker_return[0]
    actionArray = file_checker_return[1]
    initStateString = file_checker_return[2]
    goalStateString = file_checker_return[3]
    objectString = file_checker_return[4]

    initStateArray = []
    goalStateArray = []
    initStateIndex = []
    goalStateIndex = []
    actionsStartsEndsDict = {}

    initStateString = delete_keyword(initStateString, ':init')
    initStateString = delete_keyword(initStateString, 'and')
    goalStateString = delete_keyword(goalStateString, ':goal')
    goalStateString = delete_keyword(goalStateString, 'and')
    initStateArray = bracket_split_in_list(initStateString)
    goalStateArray = bracket_split_in_list(goalStateString)


    predicatesString = delete_keyword(predicatesString, ':predicates')
    predicatesArray = bracket_split_in_list(predicatesString)


    addWhen = []

    if (len(objectString) != 0):
        deleteString = ':objects' + '[\s(]+'
        objectString = re.sub(deleteString, '', objectString)
        objectString = re.sub('^[\s]*', '', objectString)
        objectString = re.sub('^[(]', '', objectString)
        objectString = re.sub('[)]$', '', objectString)
        objectString = re.sub('[\n\t]', ' ', objectString)
        objectString = re.sub('[ ]+', ' ', objectString)

        supportString = objectString
        objectList = []
        while (len(supportString) > 1):
            nextSpace = supportString.find(" ")
            if (nextSpace != -1):
                if (supportString[nextSpace + 1] == "-"):
                    nextnextSpace = supportString.find(" ", nextSpace + 1)
                    objectList.append(supportString[:nextSpace])
                    supportString = supportString[supportString.find(" ", nextnextSpace + 1):]
                else:
                    objectList.append(supportString[:nextSpace])
                    supportString = supportString[nextSpace:]
            else:
                objectList.append(supportString)
                break
            supportString = re.sub('^[ ]*', '', supportString)


    statesList = []
    for predicate in predicatesArray:
        tempList = []
        if (predicate not in statesList):
            if ("not " in predicate or "not(" in predicate):
                currentPredicate = delete_keyword(predicate, 'not')
                tempList.append(currentPredicate)
                tempList.append(predicate)
            else:
                tempList.append(predicate)
                tempList.append("(not" + predicate + ")")
            statesList.append(tempList)


    if (len(objectString) != 0):
        newStatesList = []
        for stateIndex in range(0, len(statesList)):
            tempStatesList = []
            for index in range(0, len(statesList[stateIndex])):
                for object in objectList:
                    supportString = statesList[stateIndex][index]
                    newString = statesList[stateIndex][index][:statesList[stateIndex][index].find("?")]

                    while (supportString.find("?") != -1) :
                        newString += object
                        supportString = supportString[supportString.find("?") + 1:]

                    if ("not" in statesList[stateIndex][index]):
                        newString += ")"
                    newString += ")"

                    tempStatesList.append(newString)
            newStatesList.append(tempStatesList)

        statesList = newStatesList

    if (len(statesList) == 1):
        currentStates = []
        for elem in statesList[0]:
            currentStates.append([elem])
    else:
        try:
            currentStates = list(product(statesList[0], statesList[1], repeat = 1))
            for indexStateList in range(2, len(statesList)):
                currentStates = list(product(currentStates, statesList[indexStateList], repeat = 1))
        except:
            currentStates = [statesList[0][0], statesList[0][1]]

        for indexCurrentState in range(0, len(currentStates)):
            currentStates[indexCurrentState] = str(currentStates[indexCurrentState]).split("'")
            for string in currentStates[indexCurrentState]:
                if string not in predicatesArray:
                    currentStates[indexCurrentState].remove(string)

    if len(initStateArray) == 1 and initStateArray[0] == '()' or initStateArray[0] == ['()']:
        initStateArray = currentStates

    statesNumber = len(currentStates)


    tooMuchStateFlag = 0
    if (statesNumber > 36):
        tooMuchStateFlag = 1
        for index in range(0, len(initStateArray)):
            initStateArray[index] = initStateArray[index].lower()
        for index in range(0, len(goalStateArray)):
            goalStateArray[index] = goalStateArray[index].lower()

        planFilePath = 'sas_plan'
        planFile = open(planFilePath, "r")
        planString = ""

        for line in planFile:
            if ";" in line:
                break
            planString += line

        planArray = bracket_split_in_list(planString)

        for actionIndex in range(0, len(planArray)):
            planArray[actionIndex] = planArray[actionIndex].replace('(', '').replace(')', '')
            planArray[actionIndex] = planArray[actionIndex].split(" ")

        actionsDict = {}
        for action in actionArray:
            actionString = action.split(":")
            nameAction = ""
            parametersArray, preconditionsArray, effectsArray = [], [], []
            for indexPart in range(0, len(actionString)):
                try:
                    actionString[indexPart] = actionString[indexPart].replace("\n", "")
                except:
                    None
                actionString[indexPart] = ":" + actionString[indexPart]
                if ":action" in actionString[indexPart]:
                    actionString[indexPart] = delete_keyword(actionString[indexPart], ':action')
                    nameAction = actionString[indexPart]

                if ":parameters" in actionString[indexPart]:
                    actionString[indexPart] = delete_keyword(actionString[indexPart], ':parameters')
                    parametersArray = actionString[indexPart].split("?")
                    try:
                        parametersArray.remove("")
                    except:
                        None
                    for parameterIndex in range(0, len(parametersArray)):
                        parametersArray[parameterIndex] = "?" + parametersArray[parameterIndex]

                if ":effect" in actionString[indexPart]:
                    actionString[indexPart] = actionString[indexPart].replace(":effect", "")
                    indexLastBracket = actionString[indexPart].rfind(")")
                    actionString[indexPart] = actionString[indexPart][0:indexLastBracket]
                    actionString[indexPart] = delete_keyword(actionString[indexPart], 'and')
                    effectsArray = bracket_split_in_list(actionString[indexPart])
                    try:
                        effectsArray.remove("")
                    except:
                        None


            actionsDict[nameAction] = [parametersArray, [], effectsArray]

        currentStates = [initStateArray]

        for indexPlanAction in range(0, len(planArray)):
            if (indexPlanAction + 1 == len(planArray)):
                break
            currentActionValues = actionsDict[planArray[indexPlanAction][0]]
            currentEffectWithValues = []
            for effect in currentActionValues[2]:
                currentEffect = effect
                for parameterIndex in range(0, len(currentActionValues[0])):
                    currentEffect = currentEffect.replace(currentActionValues[0][parameterIndex], planArray[indexPlanAction][parameterIndex + 1])
                try:
                    currentEffectWithValues.index(currentEffect)
                    currentEffectWithValues.index("(not(" + currentEffect)
                except:
                    currentEffectWithValues.append(currentEffect)
            currentStates.append(currentEffectWithValues)

        currentStates.append(goalStateArray)

    else:
        actionsDict = {}
        for action in actionArray:
            actionString = action.split(":")
            nameAction = ""
            parametersArray, preconditionsArray, effectsArray = [], [], []
            for indexPart in range(0, len(actionString)):
                try:
                    actionString[indexPart] = actionString[indexPart].replace("\n", "")
                except:
                    None
                actionString[indexPart] = ":" + actionString[indexPart]
                if ":action" in actionString[indexPart]:
                    actionString[indexPart] = delete_keyword(actionString[indexPart], ':action')
                    nameAction = actionString[indexPart]
    
                if ":parameters" in actionString[indexPart]:
                    actionString[indexPart] = delete_keyword(actionString[indexPart], ':parameters')
                    parametersArray = actionString[indexPart].split("?")
                    try:
                        parametersArray.remove("")
                    except:
                        None
    
                    for indexParam in range(0, len(parametersArray)):
                        if parametersArray[indexParam][-1] == ' ':
                            parametersArray[indexParam] = parametersArray[indexParam][0:-1]
                        if ')\n' in parametersArray[indexParam]:
                            parametersArray[indexParam] = parametersArray[indexParam][0:-2]
                        parametersArray[indexParam] = "(?" + parametersArray[indexParam]
                        if (parametersArray[indexParam][-1] != ")"):
                            parametersArray[indexParam] = parametersArray[indexParam] + ")"
    
                if ":precondition" in actionString[indexPart]:
                    actionString[indexPart] = actionString[indexPart].replace(":precondition", "")
    
                    actionString[indexPart] = delete_keyword(actionString[indexPart], 'and')
                    preconditionsArray = bracket_split_in_list(actionString[indexPart])
    
                    try:
                        preconditionsArray.remove("")
                    except:
                        None
    
                    if (len(objectString) != 0):
                        newPreconditionList = []
                        for predicateIndex in range(0, len(preconditionsArray)):
                            tempPreconditionList = []
                            for object in objectList:
                                supportString = preconditionsArray[predicateIndex]
                                newString = preconditionsArray[predicateIndex][:preconditionsArray[predicateIndex].find("?")]
    
                                while (supportString.find("?") != -1) :
                                    newString += object
                                    supportString = supportString[supportString.find("?") + 1:]
    
                                if ("not" in preconditionsArray[predicateIndex]):
                                    newString += ")"
                                newString += ")"
    
                                tempPreconditionList.append(newString)
    
                            newPreconditionList.append(tempPreconditionList)
    
                        preconditionsArray = newPreconditionList
    
                        if (len(preconditionsArray) > 1):
                            lenCount = len(preconditionsArray) - 1
                            tempArray, resArray = [], []
                            for elementInLastArray in preconditionsArray[lenCount]:
                                tempArray.append([elementInLastArray])
                            while (lenCount > 0):
                                lenCount -= 1
                                resArray = []
                                for element in preconditionsArray[lenCount]:
                                    for set in tempArray:
                                        tempArray2 = []
                                        tempArray2.append(element)
                                        for numeriTemp in set:
                                            tempArray2.append(numeriTemp)
                                        resArray.append(tempArray2)
                                tempArray = resArray
                            preconditionsArray = resArray
                        else:
                            tempPreco = []
                            for elem in preconditionsArray[0]:
                                tempPreco.append([elem])
                            preconditionsArray = tempPreco
                    else:
                        tempPreco = []
                        for elem in preconditionsArray:
                            tempPreco.append([elem])
                        preconditionsArray = tempPreco
    
                    if (preconditionsArray[0] == '()' or preconditionsArray[0] == ['()']):
                        preconditionsArray = currentStates
    
                if ":effect" in actionString[indexPart]:
                    actionString[indexPart] = actionString[indexPart].replace(":effect", "")
                    indexLastBracket = actionString[indexPart].rfind(")")
                    actionString[indexPart] = actionString[indexPart][0:indexLastBracket]
    
                    actionString[indexPart] = delete_keyword(actionString[indexPart], 'and')
    
                    effectsArray = bracket_split_in_list(actionString[indexPart])
                    try:
                        effectsArray.remove("")
                    except:
                        None
    
                    if (len(objectString) != 0):
                        newEffectList = []
                        for effectIndex in range(0, len(effectsArray)):
                            tempEffectList = []
                            for object in objectList:
                                supportString = effectsArray[effectIndex]
                                newString = effectsArray[effectIndex][:effectsArray[effectIndex].find("?")]
    
                                while (supportString.find("?") != -1) :
                                    newString += object
                                    supportString = supportString[supportString.find("?") + 1:]
    
                                if ("not" in effectsArray[effectIndex]):
                                    newString += ")"
                                newString += ")"
    
                                tempEffectList.append(newString)
    
                            newEffectList.append(tempEffectList)
    
                        effectsArray = newEffectList
    
                        if (len(effectsArray) > 1):
                            lenCount = len(effectsArray) - 1
                            tempArray, resArray = [], []
                            for elementInLastArray in effectsArray[lenCount]:
                                tempArray.append([elementInLastArray])
                            while (lenCount > 0):
                                lenCount -= 1
                                resArray = []
                                for element in effectsArray[lenCount]:
                                    for set in tempArray:
                                        tempArray2 = []
                                        tempArray2.append(element)
                                        for numeriTemp in set:
                                            tempArray2.append(numeriTemp)
                                        resArray.append(tempArray2)
                                tempArray = resArray
                            effectsArray = resArray
                        else:
                            tempEff = []
                            for elem in effectsArray[0]:
                                tempEff.append([elem])
                            effectsArray = tempEff
                    else:
                        tempEff = []
                        for elem in effectsArray:
                            tempEff.append([elem])
                        effectsArray = tempEff
    
                    if (effectsArray[0] == '()' or effectsArray[0] == ['()']):
                        effectsArray = currentStates
    
    
            actionsDict[nameAction] = [parametersArray, preconditionsArray, effectsArray]
    

        for key in actionsDict:
            for effect in actionsDict[key][2]:

                tempWhen = [key, []]
    
                for effInEffect in effect:
                    if "(when" in effInEffect:
                        effInEffect = delete_keyword(effInEffect, 'when')
                        tempWhen.append([bracket_split_in_list(effInEffect)[0]])
                        tempWhen.append([bracket_split_in_list(effInEffect)[1]])
    
    
                        addWhen.append(tempWhen)
    
        for add in range(0, len(addWhen)):
            actionsDict[addWhen[add][0] + str(add)] = [addWhen[add][1], [addWhen[add][2]], [addWhen[add][3]]]
            try:
                actionsDict.pop(addWhen[add][0])
            except:
                None


    # States, actions amounts
    statesNumber = len(currentStates)
    actionNumber = len(list(actionsDict.keys()))
    # Scaling factor
    scalingFactor = (statesNumber / 100) * 5

    # Search Space SVG dimensions
    SVGSearchSpaceWidth = 800 * scalingFactor
    SVGSearchSpaceHeight = 800 * scalingFactor

    # Radius and center of circle around which the states are drawn
    circleRadius = 200 * scalingFactor
    circleXCenter = SVGSearchSpaceWidth / 2
    circleYCenter = SVGSearchSpaceHeight / 2

    # Angle between a state center and the next one
    distanceAngle = (360 / statesNumber) * (math.pi / 180)

    # Radii of states circle: stateRadius is the external one, stateRadiusInitGoal is the middle one, stateRadiusColored is the internal one
    stateRadius = 20
    stateRadiusColored = (stateRadius / 100) * 85
    stateRadiusInitGoal = stateRadiusColored + 1.2
    radiusCircularAction = 3

    maxLenStateString = 0
    for state in currentStates:
        for variable in state:
            if (len(variable) > maxLenStateString):
                maxLenStateString = len(variable)
    maxLenActionString = 0
    for keyAction in actionsDict:
        if (len(keyAction) > maxLenActionString):
            maxLenActionString = len(keyAction)

    # States Key SVG dimensions
    SVGKeyStateSWidth = ((stateRadius) * statesNumber) + (5 * (maxLenStateString * len(currentStates[0])))
    SVGKeyStateSHeight = ((stateRadius * 2.5) * statesNumber)

    # Actions Key SVG dimensions
    SVGKeyActionSWidth = 150 + (len("Action ") + maxLenActionString) * 5
    SVGKeyActionSHeight = 28 * actionNumber

    # SVGs creations
    SVGSearchSpace = svgwrite.Drawing('SVGs/SVGSearchSpace.svg', profile = 'full', size = (SVGSearchSpaceWidth, SVGSearchSpaceHeight))
    SVGKeyState = svgwrite.Drawing('SVGs/SVGKeyState.svg', profile = 'full', size = (SVGKeyStateSWidth, SVGKeyStateSHeight))
    SVGKeyAction = svgwrite.Drawing('SVGs/SVGKeyAction.svg', profile = 'full', size = (SVGKeyActionSWidth, SVGKeyActionSHeight))


    ceilAmountState = math.ceil(statesNumber / 3)
    floorAmountState = math.floor(statesNumber / 3)

    statesDivision = []
    statesDivision.append(ceilAmountState)
    statesDivision.append(floorAmountState)
    if ((statesDivision[0] + statesDivision[1] + ceilAmountState) == statesNumber):
        statesDivision.insert(1, ceilAmountState)
    else:
        statesDivision.insert(1, floorAmountState)

    currentColor, countColor, statesColors = [0.0, 0.0, 0.0], [0, 0, 0], []

    statesCirclesCenters = []

    for indexStates in range(0, statesNumber):
        xCenter = circleXCenter + (circleRadius * math.cos(distanceAngle * indexStates))
        yCenter = circleYCenter + (circleRadius * math.sin(distanceAngle * indexStates))
        statesCirclesCenters.append([xCenter, yCenter])

        if ((currentColor[0] + (255.0 / statesDivision[0])) <= 255.0 and countColor[0] < statesDivision[0]):
            currentColor[0] += (255.0 / statesDivision[0])
            currentColor[1] = 0.0
            currentColor[2] = 0.0
            countColor[0] += 1
        elif ((currentColor[1] + (255.0 / statesDivision[1])) <= 255.0 and countColor[1] < statesDivision[1]):
            currentColor[0] = 0.0
            currentColor[1] += (255.0 / statesDivision[1])
            currentColor[2] = 0.0
            countColor[1] += 1
        elif ((currentColor[2] + (255.0 / statesDivision[2])) <= 255.0 and countColor[2] < statesDivision[2]):
            currentColor[0] = 0.0
            currentColor[1] = 0.0
            currentColor[2] += (255.0 / statesDivision[2])
            countColor[2] += 1

        statesColors.append([currentColor[0], currentColor[1], currentColor[2]])

    # Center of circles in Actions Key SVG
        xCenterKeyState = stateRadius + 5
        yCenterKeyState = (stateRadius + 5) + ((stateRadius * 2.5) * indexStates)
    # States strings for Actions Key SVG
        stringState = ""
        for indexVariable in range(0, len(currentStates[indexStates])):
            if (indexVariable < (len(currentStates[indexStates]) - 1)):
                stringState = stringState + currentStates[indexStates][indexVariable] + " and "
            else:
                stringState += currentStates[indexStates][indexVariable]

    # External black circle in Search Space SVG
        SVGSearchSpace.add(SVGSearchSpace.circle(center = (xCenter, yCenter), r = stateRadius, stroke = svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))
    # Internal colored circle in Search Space SVG
        SVGSearchSpace.add(SVGSearchSpace.circle(center = (xCenter, yCenter), r = stateRadiusColored, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity = 1.0))
    # Internal circles text in Search Space SVG
        SVGSearchSpace.add(SVGSearchSpace.text("State", insert = (xCenter - 12, yCenter - 2), fill = 'white', style = "font-size:10px; font-family:Arial"))
        SVGSearchSpace.add(SVGSearchSpace.text(str(indexStates), insert = (xCenter - 6, yCenter + 10), fill = 'white', style = "font-size:10px; font-family:Arial; font-weight: bold"))

    # External black circle in State Key SVG
        SVGKeyState.add(SVGKeyState.circle(center=(xCenterKeyState, yCenterKeyState), r = stateRadius, stroke=  svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))
    # Internal black circle in State Key SVG
        SVGKeyState.add(SVGKeyState.circle(center = (xCenterKeyState, yCenterKeyState), r = stateRadiusColored, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity = 1.0))
    # Internal circles text in State Key SVG
        SVGKeyState.add(SVGKeyState.text("State", insert = (xCenterKeyState - 12, yCenterKeyState - 2), fill = 'white', style = "font-size:10px; font-family:Arial"))
        SVGKeyState.add(SVGKeyState.text(str(indexStates), insert = (xCenterKeyState - 6, yCenterKeyState + 10), fill = 'white', style = "font-size:10px; font-family:Arial; font-weight: bold"))
        SVGKeyState.add(SVGKeyState.text(stringState, insert = (xCenterKeyState + 30, yCenterKeyState + 2), fill = 'black', style = "font-size:10px; font-family:Arial"))
    # Init and goal circles drawing
        notInit = 0


        for init in initStateArray:
            countInit = 0
            if (type(init) is list):
                for inInInit in init:
                    try:
                        currentStates[indexStates].index(inInInit)
                        countInit += 1
                    except:
                        notInit = 1
                        break
                if (countInit == len(init)):
                    initStateIndex.append(indexStates)
            elif (type(init) is str):
                try:
                    currentStates[indexStates].index(init)
                    initStateIndex.append(indexStates)
                except:
                    notInit = 1
                    break


        if (notInit == 0):
            SVGSearchSpace.add(SVGSearchSpace.circle(center = (xCenter, yCenter), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 255, 0, 'RGB'), fill_opacity = 0.0))
            SVGKeyState.add(SVGKeyState.circle(center = (xCenterKeyState, yCenterKeyState), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 255, 0, 'RGB'), fill_opacity = 0.0))
        notGoal = 0
        for goalVar in goalStateArray:
            try:
                currentStates[indexStates].index(goalVar)
                goalStateIndex.append(indexStates)
            except:
                notGoal = 1
        if (notGoal == 0):
            SVGSearchSpace.add(SVGSearchSpace.circle(center = (xCenter, yCenter), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))
            SVGKeyState.add(SVGKeyState.circle(center = (xCenterKeyState, yCenterKeyState), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))

    for actionKey in actionsDict:
        preconditionIndexArray, effectIndexArray, startsEndsArrays = [], [], []

        for indexState in range(0, len(currentStates)):
            for precondition in actionsDict[actionKey][1]:
                countPreco = 0
                if (type(precondition) is list):
                    for precoInPrecondition in precondition:
                        try:
                            currentStates[indexState].index(precoInPrecondition)
                            countPreco += 1
                        except:
                            continue
                    if (countPreco == len(precondition)):
                        preconditionIndexArray.append(indexState)
                elif (type(precondition) is str):
                    try:
                        currentStates[indexStates].index(precondition)
                        preconditionIndexArray.append(indexStates)
                    except:
                        break

        for indexState in range(0, len(currentStates)):
            for effect in actionsDict[actionKey][2]:
                countEff = 0
                for effInEffect in effect:
                    try:
                        currentStates[indexState].index(effInEffect)
                        countEff += 1
                    except:
                        continue
                if (countEff == len(effect)):
                    effectIndexArray.append(indexState)

        for preconditionStart in preconditionIndexArray:
            for effectEnd in effectIndexArray:
                startsEndsArrays.append([preconditionStart, effectEnd])

        actionsStartsEndsDict[actionKey] = startsEndsArrays


    pathDict = {}
    for actionStartEndKey in actionsStartsEndsDict:
        for path in actionsStartsEndsDict[actionStartEndKey]:
            try:
                indexFound = list(pathDict.keys()).index((path[0], path[1]))
                pathDict[(path[0], path[1])].append(actionStartEndKey)
            except:
                try:
                    indexFound = list(pathDict.keys()).index((path[1], path[0]))
                    pathDict[(path[1], path[0])].append(actionStartEndKey)
                except:
                    pathDict[(path[0], path[1])] = [actionStartEndKey]


    actionColorsDict = {}
    statesDivisionAction = []

    actionsNumber = len(actionsStartsEndsDict)
    ceilAmountAction = math.ceil(actionsNumber / 3)
    floorAmountAction = math.floor(actionsNumber / 3)

    statesDivisionAction = []
    statesDivisionAction.append(ceilAmountAction)
    statesDivisionAction.append(floorAmountAction)
    if ((statesDivisionAction[0] + statesDivisionAction[1] + ceilAmountAction) == actionsNumber):
        statesDivisionAction.insert(1, ceilAmountAction)
    else:
        statesDivisionAction.insert(1, floorAmountAction)

    currentColorAction, countColorAction = [0.0, 0.0, 0.0], [0, 0, 0]
    countPrint = 0
    for actionKeyLine in actionsStartsEndsDict:

        countPrint += 1

        if ((currentColorAction[0] + (255.0 / statesDivisionAction[0])) <= 255.0 and countColorAction[0] < statesDivisionAction[0]):
            currentColorAction[0] += (255.0 / statesDivisionAction[0])
            currentColorAction[1] = 0.0
            currentColorAction[2] = 0.0
            countColorAction[0] += 1
        elif ((currentColorAction[1] + (255.0 / statesDivisionAction[1])) <= 255.0 and countColorAction[1] < statesDivisionAction[1]):
            currentColorAction[0] = 0.0
            currentColorAction[1] += (255.0 / statesDivisionAction[1])
            currentColorAction[2] = 0.0
            countColorAction[1] += 1
        elif ((currentColorAction[2] + (255.0 / statesDivisionAction[2])) <= 255.0 and countColorAction[2] < statesDivisionAction[2]):
            currentColorAction[0] = 0.0
            currentColorAction[1] = 0.0
            currentColorAction[2] += (255.0 / statesDivisionAction[2])
            countColorAction[2] += 1


        actionColorsDict[actionKeyLine] = [currentColorAction[0], currentColorAction[1], currentColorAction[2]]

        stringAction = "Action " + actionKeyLine
        actionCoordX = 30
        actionCoordY = 20

    # Arrows lines in Key Action SVG
        SVGKeyAction.add(SVGKeyAction.line((actionCoordX + 10, (actionCoordY * countPrint)), (actionCoordX + 40, (actionCoordY * countPrint)), stroke = svgwrite.rgb(currentColorAction[0], currentColorAction[1], currentColorAction[2], 'RGB')))
    # Texts in Key Action SVG
        SVGKeyAction.add(SVGKeyAction.text(stringAction, insert = (actionCoordX + 60, (actionCoordY * countPrint) + 3), fill = 'black', style = "font-size:10px; font-family:Arial;"))
        SVGKeyAction.add(SVGKeyAction.circle(center = (actionCoordX, actionCoordY * countPrint), r = radiusCircularAction, fill=svgwrite.rgb(actionColorsDict[actionKeyLine][0], actionColorsDict[actionKeyLine][1], actionColorsDict[actionKeyLine][2], 'RGB'), fill_opacity = 1.0))

    # Arrowheads in Key Action SVG
        trianglePoints = ((actionCoordX + 42, (actionCoordY * countPrint)), (actionCoordX + 42 - 5, (actionCoordY * countPrint) + 5), (actionCoordX + 42 - 5, (actionCoordY * countPrint) - 5))
        SVGKeyAction.add(svgwrite.shapes.Polygon(trianglePoints, fill=svgwrite.rgb(actionColorsDict[actionKeyLine][0], actionColorsDict[actionKeyLine][1], actionColorsDict[actionKeyLine][2], 'RGB'), fill_opacity=100))


    # Dashed arrows lines in Search Space SVG
    repetition = []
    if tooMuchStateFlag == 0:
        for actionKeyLine in actionsStartsEndsDict:
            dottedDimension = statesNumber * 1.5
            for pathKey in list(pathDict.keys()):
                initialPointLine = statesCirclesCenters[pathKey[0]]
                finalPointLine = statesCirclesCenters[pathKey[1]]

                if (initialPointLine != finalPointLine):
                    angle = math.atan2((finalPointLine[1] - initialPointLine[1]), (finalPointLine[0] - initialPointLine[0]))
                    initialPointLine = [statesCirclesCenters[pathKey[0]][0] + (stateRadius * math.cos(angle)), statesCirclesCenters[pathKey[0]][1] + (stateRadius * math.sin(angle))]
                    finalPointLine = [statesCirclesCenters[pathKey[1]][0] - (stateRadius * math.cos(angle)), statesCirclesCenters[pathKey[1]][1] - (stateRadius * math.sin(angle))]

                    for bondIndex in range(0, len(pathDict[pathKey])):
                        pointString = 'M' + str(initialPointLine[0]) + ',' + str(initialPointLine[1]) + ' '
                        pointString += str(finalPointLine[0]) + ',' + str(finalPointLine[1])
                        SVGSearchSpace.add(SVGSearchSpace.path(d = pointString, stroke = svgwrite.rgb(actionColorsDict[pathDict[pathKey][bondIndex]][0], actionColorsDict[pathDict[pathKey][bondIndex]][1], actionColorsDict[pathDict[pathKey][bondIndex]][2], 'RGB'), stroke_dasharray = str(0) + "," + str(dottedDimension * bondIndex) + "," + str(dottedDimension) + "," + str(((len(pathDict[pathKey]) - 1) * dottedDimension) - (bondIndex * dottedDimension))))

            for startEnd in actionsStartsEndsDict[actionKeyLine]:
                initialStateLine = statesCirclesCenters[startEnd[0]]
                finalStateLine = statesCirclesCenters[startEnd[1]]

                angle = math.atan2((finalStateLine[1] - initialStateLine[1]), (finalStateLine[0] - initialStateLine[0]))
                initialPointLine = [statesCirclesCenters[startEnd[0]][0] + (stateRadius * math.cos(angle)), statesCirclesCenters[startEnd[0]][1] + (stateRadius * math.sin(angle))]
                finalPointLine = [statesCirclesCenters[startEnd[1]][0] - (stateRadius * math.cos(angle)), statesCirclesCenters[startEnd[1]][1] - (stateRadius * math.sin(angle))]

                if (initialStateLine != finalStateLine):

                    arrowSize = 12

                    circleArrowRadius = 10
                    firstCenter = [statesCirclesCenters[startEnd[1]][0] - ((stateRadius + circleArrowRadius) * math.cos(angle)), statesCirclesCenters[startEnd[1]][1] - ((stateRadius + circleArrowRadius) * math.sin(angle))]
                    secondCenter = [statesCirclesCenters[startEnd[1]][0] - ((stateRadius + circleArrowRadius - arrowSize) * math.cos(angle)), statesCirclesCenters[startEnd[1]][1] - ((stateRadius + circleArrowRadius - arrowSize) * math.sin(angle))]

                    a1 = -2 * firstCenter[0]
                    b1 = -2 * firstCenter[1]
                    c1 = (firstCenter[0]**2) + (firstCenter[1]**2) - (circleArrowRadius**2)
                    a2 = -2 * secondCenter[0]
                    b2 = -2 * secondCenter[1]
                    c2 = (secondCenter[0]**2) + (secondCenter[1]**2) - (circleArrowRadius**2)

                    x1 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 - b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    x2 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 + b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    y1 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 + a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    y2 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 - a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    pointAArrow = (x1, y1)
                    pointBArrow = (x2, y2)

                    trianglePoints = ((pointAArrow[0], pointAArrow[1]), (pointBArrow[0], pointBArrow[1]), (finalPointLine[0], finalPointLine[1]))

                    SVGSearchSpace.add(svgwrite.shapes.Polygon(trianglePoints, fill = svgwrite.rgb(actionColorsDict[actionKeyLine][0], actionColorsDict[actionKeyLine][1], actionColorsDict[actionKeyLine][2], 'RGB'), fill_opacity=100))
                else:
                    repetition.append(startEnd)


                    centerCircularAction = [statesCirclesCenters[startEnd[0]][0] + ((stateRadius + radiusCircularAction*2*repetition.count(startEnd)) * math.cos(distanceAngle * startEnd[0])), statesCirclesCenters[startEnd[0]][1] + ((stateRadius + radiusCircularAction*2*repetition.count(startEnd)) * math.sin(distanceAngle * startEnd[0]))]

        # Circles of ciclic actions
                    SVGSearchSpace.add(SVGSearchSpace.circle(center = (centerCircularAction[0], centerCircularAction[1]), r = radiusCircularAction, fill=svgwrite.rgb(actionColorsDict[actionKeyLine][0], actionColorsDict[actionKeyLine][1], actionColorsDict[actionKeyLine][2], 'RGB'), fill_opacity = 1.0))

    else:
        for indexStateCenter in range(0, len(statesCirclesCenters)):
            initialStateLine = statesCirclesCenters[indexStateCenter]
            if (indexStateCenter + 1 == len(statesCirclesCenters)):
                break
            finalStateLine = statesCirclesCenters[indexStateCenter + 1]

            angle = math.atan2((finalStateLine[1] - initialStateLine[1]), (finalStateLine[0] - initialStateLine[0]))
            initialPointLine = [statesCirclesCenters[indexStateCenter][0] + (stateRadius * math.cos(angle)), statesCirclesCenters[indexStateCenter][1] + (stateRadius * math.sin(angle))]
            finalPointLine = [statesCirclesCenters[indexStateCenter + 1][0] - (stateRadius * math.cos(angle)), statesCirclesCenters[indexStateCenter + 1][1] - (stateRadius * math.sin(angle))]

            pointString = 'M' + str(initialPointLine[0]) + ',' + str(initialPointLine[1]) + ' '
            pointString += str(finalPointLine[0]) + ',' + str(finalPointLine[1])

            SVGSearchSpace.add(SVGSearchSpace.path(d = pointString,
                                                stroke = svgwrite.rgb(actionColorsDict[planArray[indexStateCenter][0]][0],
                                                                      actionColorsDict[planArray[indexStateCenter][0]][1],
                                                                      actionColorsDict[planArray[indexStateCenter][0]][2], 'RGB')))

            arrowSize = 12

            circleArrowRadius = 10
            firstCenter = [statesCirclesCenters[indexStateCenter + 1][0] - ((stateRadius + circleArrowRadius) * math.cos(angle)), statesCirclesCenters[indexStateCenter + 1][1] - ((stateRadius + circleArrowRadius) * math.sin(angle))]
            secondCenter = [statesCirclesCenters[indexStateCenter + 1][0] - ((stateRadius + circleArrowRadius - arrowSize) * math.cos(angle)), statesCirclesCenters[indexStateCenter + 1][1] - ((stateRadius + circleArrowRadius - arrowSize) * math.sin(angle))]

            a1 = -2 * firstCenter[0]
            b1 = -2 * firstCenter[1]
            c1 = (firstCenter[0]**2) + (firstCenter[1]**2) - (circleArrowRadius**2)
            a2 = -2 * secondCenter[0]
            b2 = -2 * secondCenter[1]
            c2 = (secondCenter[0]**2) + (secondCenter[1]**2) - (circleArrowRadius**2)

            x1 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 - b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

            x2 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 + b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

            y1 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 + a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

            y2 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 - a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

            pointAArrow = (x1, y1)
            pointBArrow = (x2, y2)

            trianglePoints = ((pointAArrow[0], pointAArrow[1]), (pointBArrow[0], pointBArrow[1]), (finalPointLine[0], finalPointLine[1]))

            SVGSearchSpace.add(svgwrite.shapes.Polygon(trianglePoints,
                                                       fill = svgwrite.rgb(actionColorsDict[planArray[indexStateCenter][0]][0],
                                                                           actionColorsDict[planArray[indexStateCenter][0]][1],
                                                                           actionColorsDict[planArray[indexStateCenter][0]][2],
                                                                           'RGB'),
                                                       fill_opacity=100))

    SVGSearchSpace.save()
    SVGKeyState.save()
    SVGKeyAction.save()

    return [initStateIndex, goalStateIndex, actionsStartsEndsDict, statesNumber, pathDict, statesColors, actionColorsDict, addWhen, tooMuchStateFlag]

def plan_SVGs(returnMain_SVGs):
    initStateIndex = returnMain_SVGs[0]
    goalStateIndex = returnMain_SVGs[1]
    actionsStartsEndsDict = returnMain_SVGs[2]
    statesNumber = returnMain_SVGs[3]
    pathDict = returnMain_SVGs[4]
    statesColors = returnMain_SVGs[5]
    actionColorsDict = returnMain_SVGs[6]
    addWhen = returnMain_SVGs[7]
    tooMuchStateFlag = returnMain_SVGs[8]


    planFilePath = 'sas_plan'
    planSVGsDirectoryPath = "SVGs/Plan"

    planFile = open(planFilePath, "r")
    planString = ""

    for file in os.listdir(planSVGsDirectoryPath):
        os.remove(planSVGsDirectoryPath + "/" + file)

    arrayStateActions, tempStateActions = [], []
    solution = []
    if (tooMuchStateFlag == 0):
        for line in planFile:
            if ";" in line:
                break
            planString += line
        planArray = bracket_split_in_list(planString)
        for actionIndex in range(0, len(planArray)):
            planArray[actionIndex] = planArray[actionIndex].replace('(', '').replace(')', '')
            planArray[actionIndex] = planArray[actionIndex].split(" ")[0]

        for initState in initStateIndex:
            tempStateActions = []

            notInitIndex = 0
            whenFound = 0
            try:
                for pair in actionsStartsEndsDict[planArray[0]]:
                    if (initState == pair[0]):
                        notInitIndex = 1
                        break
            except:
                for indexWhen in range(0, len(addWhen)):
                    for pair in actionsStartsEndsDict[planArray[0] + str(indexWhen)]:
                        if (initState == pair[0]):
                            notInitIndex = 1
                            whenFound = indexWhen
                            break
            if (notInitIndex != 1):
                continue

            currentState = initState
            tempStateActions.append(currentState)

            for indexAction in range(0, len(planArray)):
                try:
                    for startEnd in actionsStartsEndsDict.get(planArray[indexAction]):
                        flagEnd = 0
                        if startEnd[0] == currentState:
                            if (indexAction + 1 < len(planArray)):
                                for nextStartEnd in actionsStartsEndsDict.get(planArray[indexAction + 1]):
                                    if startEnd[1] == nextStartEnd[0]:
                                        break
                                    flagEnd = 1
                            if flagEnd == 1:
                                continue
                            try:
                                tempStateActions.index(startEnd[1])
                            except:
                                tempStateActions.append(planArray[indexAction])
                                tempStateActions.append(startEnd[1])
                                currentState = startEnd[1]
                except:
                    for startEnd in actionsStartsEndsDict.get(planArray[indexAction] + str(whenFound)):
                        if startEnd[0] == currentState:
                            try:
                                tempStateActions.index(startEnd[1])
                            except:
                                tempStateActions.append(planArray[indexAction] + str(whenFound))
                                tempStateActions.append(startEnd[1])
                                currentState = startEnd[1]
                                break

            arrayStateActions.append(tempStateActions)

        for stateActions in arrayStateActions:
            for init in initStateIndex:
                if (stateActions[0] == init):
                    for goal in goalStateIndex:
                        if (stateActions[-1] == goal):
                            solution = stateActions
                        if (len(solution) > 0):
                            break
                if (len(solution) > 0):
                    break
    else:
        for line in planFile:
            if ";" in line:
                break
            planString += line

        planArray = bracket_split_in_list(planString)

        for actionIndex in range(0, len(planArray)):
            planArray[actionIndex] = planArray[actionIndex].replace('(', '').replace(')', '')
            planArray[actionIndex] = planArray[actionIndex].split(" ")

        solution = [0]
        for indexAction in range(0, len(planArray)):
            solution.append(planArray[indexAction][0])
            solution.append(indexAction + 1)


    # Scaling factor
    scalingFactor = (statesNumber / 100) * 5

    # Search Space SVG dimensions
    SVGPlanWidth = 800 * scalingFactor
    SVGPlanHeight = 800 * scalingFactor

    for indexActionState in range(0, len(solution)):
        SVGPlanName = 'SVGs/Plan/SVGPlan' + str(indexActionState) + '.svg'
        SVGPlan = svgwrite.Drawing(SVGPlanName, profile = 'full', size = (SVGPlanWidth, SVGPlanHeight))

        # Radius and center of circle around which the states are drawn
        circleRadius = 200 * scalingFactor
        circleXCenter = SVGPlanWidth / 2
        circleYCenter = SVGPlanHeight / 2

        # Angle between a state center and the next one
        distanceAngle = (360 / statesNumber) * (math.pi / 180)

        # Radii of states circle: stateRadius is the external one, stateRadiusInitGoal is the middle one, stateRadiusColored is the internal one
        stateRadius = 20
        stateRadiusColored = (stateRadius / 100) * 85
        stateRadiusInitGoal = stateRadiusColored + 1.2

        statesCirclesCenters = []

        for indexStates in range(0, statesNumber):
            xCenter = circleXCenter + (circleRadius * math.cos(distanceAngle * indexStates))
            yCenter = circleYCenter + (circleRadius * math.sin(distanceAngle * indexStates))
            statesCirclesCenters.append([xCenter, yCenter])

            if (indexActionState % 2 == 0 and indexStates == solution[indexActionState]):
                currentColor = statesColors[solution[indexActionState]]
            else:
                currentColor = [220.0, 220.0, 220.0]

            SVGPlan.add(SVGPlan.circle(center = (xCenter, yCenter), r = stateRadius, stroke = svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))
        # Internal colored circle in Search Space SVG
            SVGPlan.add(SVGPlan.circle(center = (xCenter, yCenter), r = stateRadiusColored, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity = 1.0))
        # Internal circles text in Search Space SVG
            SVGPlan.add(SVGPlan.text("State", insert = (xCenter - 12, yCenter - 2), fill = 'white', style = "font-size:10px; font-family:Arial"))
            SVGPlan.add(SVGPlan.text(str(indexStates), insert = (xCenter - 6, yCenter + 10), fill = 'white', style = "font-size:10px; font-family:Arial; font-weight: bold"))

            if (indexStates == solution[0]):
                SVGPlan.add(SVGPlan.circle(center = (xCenter, yCenter), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 255, 0, 'RGB'), fill_opacity = 0.0))
            if (indexStates == solution[-1]):
                SVGPlan.add(SVGPlan.circle(center = (xCenter, yCenter), r = stateRadiusInitGoal, stroke = svgwrite.rgb(0, 0, 0, 'RGB'), fill_opacity = 0.0))

        # Dashed arrows lines in Search Space SVG
        repetition = []

        coloredPath = []
        if (tooMuchStateFlag == 0):
            for actionKeyLine in actionsStartsEndsDict:
                for path in actionsStartsEndsDict[actionKeyLine]:
                    if (path in coloredPath) or ([path[1], path[0]] in coloredPath):
                        continue
                    initialPointLine = statesCirclesCenters[path[0]]
                    finalPointLine = statesCirclesCenters[path[1]]

                    currentColor = [220.0, 220.0, 220.0]
                    if (indexActionState % 2 == 1):
                        if ((solution[indexActionState - 1] == path[0] and solution[indexActionState + 1] == path[1])):
                            currentColor = actionColorsDict[actionKeyLine]
                            coloredPath.append(path)
                        else:
                            currentColor = [220.0, 220.0, 220.0]

                    if (initialPointLine != finalPointLine):
                        angle = math.atan2((finalPointLine[1] - initialPointLine[1]), (finalPointLine[0] - initialPointLine[0]))
                        initialPointLine = [statesCirclesCenters[path[0]][0] + (stateRadius * math.cos(angle)), statesCirclesCenters[path[0]][1] + (stateRadius * math.sin(angle))]
                        finalPointLine = [statesCirclesCenters[path[1]][0] - (stateRadius * math.cos(angle)), statesCirclesCenters[path[1]][1] - (stateRadius * math.sin(angle))]
                        pointString = 'M' + str(initialPointLine[0]) + ',' + str(initialPointLine[1]) + ' '
                        pointString += str(finalPointLine[0]) + ',' + str(finalPointLine[1])
                        if (currentColor[0] == 220.0):
                            SVGPlan.add(SVGPlan.path(d = pointString, stroke = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), stroke_opacity = 0.5, stroke_width = 1.0))
                        else:
                            SVGPlan.add(SVGPlan.path(d = pointString, stroke = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), stroke_opacity = 1.0, stroke_width = 2.0))

                        arrowSize = 12

                        circleArrowRadius = 10
                        firstCenter = [statesCirclesCenters[path[1]][0] - ((stateRadius + circleArrowRadius) * math.cos(angle)), statesCirclesCenters[path[1]][1] - ((stateRadius + circleArrowRadius) * math.sin(angle))]
                        secondCenter = [statesCirclesCenters[path[1]][0] - ((stateRadius + circleArrowRadius - arrowSize) * math.cos(angle)), statesCirclesCenters[path[1]][1] - ((stateRadius + circleArrowRadius - arrowSize) * math.sin(angle))]

                        a1 = -2 * firstCenter[0]
                        b1 = -2 * firstCenter[1]
                        c1 = (firstCenter[0]**2) + (firstCenter[1]**2) - (circleArrowRadius**2)
                        a2 = -2 * secondCenter[0]
                        b2 = -2 * secondCenter[1]
                        c2 = (secondCenter[0]**2) + (secondCenter[1]**2) - (circleArrowRadius**2)

                        x1 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 - b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                        x2 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 + b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                        y1 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 + a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                        y2 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 - a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                        pointAArrow = (x1, y1)
                        pointBArrow = (x2, y2)

                        trianglePoints = ((pointAArrow[0], pointAArrow[1]), (pointBArrow[0], pointBArrow[1]), (finalPointLine[0], finalPointLine[1]))

                        if (currentColor[0] == 220.0):
                            SVGPlan.add(svgwrite.shapes.Polygon(trianglePoints, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity=50))
                        else:
                            SVGPlan.add(svgwrite.shapes.Polygon(trianglePoints, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity=100))

                    else:
                        repetition.append(path)

                        radiusCircularAction = 3
                        centerCircularAction = [statesCirclesCenters[path[0]][0] + ((stateRadius + radiusCircularAction*2*repetition.count(path)) * math.cos(distanceAngle * path[0])), statesCirclesCenters[path[0]][1] + ((stateRadius + radiusCircularAction*2*repetition.count(path)) * math.sin(distanceAngle * path[0]))]

            # Circles of ciclic actions

                        SVGPlan.add(SVGPlan.circle(center = (centerCircularAction[0], centerCircularAction[1]), r = radiusCircularAction, fill=svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity = 1.0))

        else:
            if (indexActionState + 1 > len(solution)):
                break

            for indexActionStateInt in range(0, len(solution)):
                if (indexActionStateInt % 2 != 0):
                    if (indexActionStateInt == indexActionState):
                        currentColor = actionColorsDict[solution[indexActionStateInt]]
                    else:
                        currentColor = [220.0, 220.0, 220.0]

                    initialPointLine = statesCirclesCenters[solution[indexActionStateInt - 1]]
                    finalPointLine = statesCirclesCenters[solution[indexActionStateInt + 1]]

                    angle = math.atan2((finalPointLine[1] - initialPointLine[1]), (finalPointLine[0] - initialPointLine[0]))
                    initialPointLine = [statesCirclesCenters[solution[indexActionStateInt - 1]][0] + (stateRadius * math.cos(angle)), statesCirclesCenters[solution[indexActionStateInt - 1]][1] + (stateRadius * math.sin(angle))]
                    finalPointLine = [statesCirclesCenters[solution[indexActionStateInt + 1]][0] - (stateRadius * math.cos(angle)), statesCirclesCenters[solution[indexActionStateInt + 1]][1] - (stateRadius * math.sin(angle))]
                    pointString = 'M' + str(initialPointLine[0]) + ',' + str(initialPointLine[1]) + ' '
                    pointString += str(finalPointLine[0]) + ',' + str(finalPointLine[1])
                    if (indexActionStateInt == indexActionState):
                        SVGPlan.add(SVGPlan.path(d = pointString, stroke = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), stroke_opacity = 1.0, stroke_width = 2.0))
                    else:
                        SVGPlan.add(SVGPlan.path(d = pointString, stroke = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), stroke_opacity = 1.0, stroke_width = 1.0))

                    arrowSize = 12

                    circleArrowRadius = 10
                    firstCenter = [statesCirclesCenters[solution[indexActionStateInt + 1]][0] - ((stateRadius + circleArrowRadius) * math.cos(angle)), statesCirclesCenters[solution[indexActionStateInt + 1]][1] - ((stateRadius + circleArrowRadius) * math.sin(angle))]
                    secondCenter = [statesCirclesCenters[solution[indexActionStateInt + 1]][0] - ((stateRadius + circleArrowRadius - arrowSize) * math.cos(angle)), statesCirclesCenters[solution[indexActionStateInt + 1]][1] - ((stateRadius + circleArrowRadius - arrowSize) * math.sin(angle))]

                    a1 = -2 * firstCenter[0]
                    b1 = -2 * firstCenter[1]
                    c1 = (firstCenter[0]**2) + (firstCenter[1]**2) - (circleArrowRadius**2)
                    a2 = -2 * secondCenter[0]
                    b2 = -2 * secondCenter[1]
                    c2 = (secondCenter[0]**2) + (secondCenter[1]**2) - (circleArrowRadius**2)

                    x1 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 - b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    x2 = -(2*a1*c1 - 2*a1*c2 - 2*a2*c1 + 2*a2*c2 + a1*b2**2 + a2*b1**2 + b1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - b2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*b1*b2 - a2*b1*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    y1 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 + a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    y2 = -(2*b1*c1 - 2*b1*c2 - 2*b2*c1 + 2*b2*c2 + a1**2*b2 + a2**2*b1 - a1*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) + a2*(a1**2*b2**2 - 4*a1**2*c2 - 2*a1*a2*b1*b2 + 4*a1*a2*c1 + 4*a1*a2*c2 + a2**2*b1**2 - 4*a2**2*c1 - 4*b1**2*c2 + 4*b1*b2*c1 + 4*b1*b2*c2 - 4*b2**2*c1 - 4*c1**2 + 8*c1*c2 - 4*c2**2)**(1/2) - a1*a2*b1 - a1*a2*b2)/(2*(a1**2 - 2*a1*a2 + a2**2 + b1**2 - 2*b1*b2 + b2**2))

                    pointAArrow = (x1, y1)
                    pointBArrow = (x2, y2)

                    trianglePoints = ((pointAArrow[0], pointAArrow[1]), (pointBArrow[0], pointBArrow[1]), (finalPointLine[0], finalPointLine[1]))
                    SVGPlan.add(svgwrite.shapes.Polygon(trianglePoints, fill = svgwrite.rgb(currentColor[0], currentColor[1], currentColor[2], 'RGB'), fill_opacity=100))

        SVGPlan.save()
