##
# Ice Parser
# Intuitive Coding languagE parser
#
# author William F.
# version 0.143
#
# Fix:
# FIXME: Add variable protection checks to all opcodes.
# FIXME: Ensure all opcodes check for valid variable names and types.
#
# Do:
# TODO: Implement FWRITE.
# TODO: Implement FWSEEK.
# TODO: Implement FCLOSE.
##

import sys
import re
import time

# Data
ep = 0
current = None

returnPoint = 0
currentReturn = 0
returnStack = [returnPoint]

safeVariableAccess = False

execTrue, execFalse, execCode = (False, False, True)
currentIf = 0
ifStack = [[False, False, True]]

types = {}
instances = {}
classes = {
    "File": {
        "props": {
            "name": {"type": "Str", "data": ""},
            "data": {"type": "Arr", "data": []},
            "size": {"type": "Int", "data": 0}
        }
    }
}
pointers = {}
variables = {
    "EMPTY": {
        "data": "__INFO_EMPTYSTACK__",
        "type": "Str",
        "protected": True
    }
}
labels = {}
stack = []

validTypes = ["Int", "Flt", "Str", "FileStr", "Arr"]
validConditions = ["==", "!=", ">", ">=", "<", "<="]
validMulti = ["and", "or"]

validOperations = ["!", "+", "-", "*", "/", "&", "|", "~", "^", "<<", ">>"]


# Utils
def Throw(error):
    print "\r\n[Error] " + str(ep+1) + ": " + error
    sys.exit(1)


def DbgThrow(failure):
    print "\r\n[Failure]: " + failure
    sys.exit(1)


def ParseFlag(data, do=True):
    typeFlag = data[:1]
    typeID = data[1:]

    resProtected = False

    if do:
        if typeFlag == "$":  # Variable
            if typeID not in variables:
                Throw("Unknown variable \"" + typeID + "\".")

            if variables[typeID]["protected"] and not safeVariableAccess:
                Throw("Trying to access a protected variable. ($"
                      + typeID + ")")

            resData = variables[typeID]["data"]
            resType = variables[typeID]["type"]
            resProtected = variables[typeID]["protected"]

            if resType == "Str" or resType == "FileStr":
                resData = resData
            elif resType == "Int":
                resData = int(resData)
            elif resType == "Flt":
                resData = float(resData)
            elif resType == "Arr":
                resData = "<Array " + typeID + ">"
        elif typeFlag == "#":  # Field
            if current is None or current not in instances:
                Throw("Unknown instance.")

            if typeID not in instances[current]["fields"]:
                Throw("Unknown field \"" + typeID + "\".")

            resData = instances[current]["fields"][typeID]["data"]
            resType = instances[current]["fields"][typeID]["type"]
            resProtected = instances[current]["fields"][typeID]["protected"]

            if resType == "Str":
                resData = resData.lstrip("\"").rstrip("\"")
            elif resType == "Int":
                resData = int(resData)
            elif resType == "Flt":
                resData = float(resData)
            elif resType == "Arr":
                resData = "<Array " + typeID + ">"
        elif typeFlag == "&":  # Instance
            if typeID not in instances:
                Throw("Unknown instance \"" + typeID +"\".")

            resData = "<InstanceOf " + instances[typeID]["instanceOf"] + ">"
            resType = "Instance"
        elif typeFlag == "%":  # Pointer
            if typeID not in pointers:
                Throw("Unknown pointer \"" + typeID + "\".")

            resData = "<PointerOf " + pointers[typeID]["pointerOf"] + ">"
            resType = "Pointer"
        elif typeFlag == "*":  # Label
            if typeID not in labels:
                Throw("Unknown label \""+ typeID +"\".")

            resData = labels[typeID]["point"]
            resType = "Int"
        else:
            unquote = data.lstrip("\"").rstrip("\"")

            if data == unquote:
                if "." in data:
                    resData = float(data)
                    resType = "Flt"
                else:
                    resData = int(data)
                    resType = "Int"
            else:
                resData = unquote
                resType = "Str"

        return (resData, resType, typeID, typeFlag, resProtected)

    unquote = data.lstrip("\"").rstrip("\"")

    if data == unquote:
        if "." in data:
            resType = "Flt"
        else:
            resType = "Int"
    else:
        resType = "Str"

    return (data, typeID, typeFlag, resType)

# Then the magic happens:
lines = []
with open(sys.argv[1]) as f:
    lines = [l.lstrip().rstrip("\n") for l in f.readlines()]

    ep = 0
    while ep <= len(lines)-1:
        line = lines[ep]

        if line == "" or line[0] == "#":
            ep += 1
            continue

        line = [e.lstrip() for e in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line.lstrip())]
        opcode = line[0]
        args = []
        for i in range(1, len(line)):
            args.append(line[i].strip())

        if opcode == "def":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            defName = args[0]

            labels[defName] = {}
            labels[defName]["point"] = ep+1

            ep += 1
            continue

        # Structs
        elif opcode == "struct":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            argName = args[0]
            argFlag = ParseFlag(argName, False)[2]

            if argFlag == "$" or argFlag == "#" or argFlag == "@" or argFlag == "*" or any(char.isdigit() for char in argName):
                Throw("Invalid struct name \""+ argName +"\".")

            # Function code
            if argName in types:
                Throw("Struct already exists.")

            types[argName] = {}
            types[argName]["fields"] = {}

            current = argName

            ep += 1
            continue

        elif opcode == "field":
            if len(args) != 2:
                Throw("Invalid argument count.")

            # Arguments
            argName = args[0]
            argType = args[1]

            if any(char.isdigit() for char in argName):
                Throw("Invalid field name.")

            # Function code
            if current is None or current not in types:
                Throw("Unknown struct.")

            if argType not in validTypes:
                Throw("Invalid data type for field.")

            if argName in types[current]["fields"]:
                Throw("Trying to overwrite an existing field.")

            types[current]["fields"][argName] = {}
            types[current]["fields"][argName]["data"] = None
            types[current]["fields"][argName]["type"] = argType

            ep += 1
            continue

        ep += 1

    if "program" not in labels:
        DbgThrow("No entrypoint (\"program\" label).")
    else:
        ep = labels["program"]["point"]

    while ep <= len(lines)-1:
        line = lines[ep]

        if line == "" or line[0] == "#":
            ep += 1
            continue

        line = [e.lstrip() for e in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line.lstrip())]
        opcode = line[0]
        args = []
        for i in range(1, len(line)):
            args.append(line[i].strip())

        # Condition handling
        execTrue = ifStack[currentIf][0]
        execFalse = ifStack[currentIf][1]
        execCode = ifStack[currentIf][2]

        # print ep, opcode, args, (execTrue, execFalse, execCode)

        if execTrue:
            if opcode == "else":
                ifStack[currentIf][0] = False
                ifStack[currentIf][2] = False
            elif opcode == "endif":
                ifStack[currentIf][0] = False
                ifStack[currentIf][2] = True
        elif execFalse:
            if opcode == "else":
                ifStack[currentIf][1] = False
                ifStack[currentIf][2] = True
            elif opcode == "endif":
                ifStack[currentIf][1] = False
                ifStack[currentIf][2] = True

        if not execCode and opcode != "endif" and opcode != "elif":
            ep += 1
            continue

        # Parse opcode
        if opcode == "exit":
            sys.exit(0)

        # Conditions
        elif opcode == "if" or opcode == "elif":
            if len(args) < 3:
                Throw("Invalid argument count.")

            if opcode == "if":
                currentIf += 1
                item = [False, False, True]
                ifStack.append(item)

            if opcode == "elif" and ifStack[currentIf][0]:
                ifStack[currentIf][2] = False

                ep += 1
                continue

            # Arguments
            i = 0
            answers = []
            sep = []
            sepName = 0
            done = False
            result = []

            # Enable protected variable access
            safeVariableAccess = True

            # Function code
            while not done:
                argA = ParseFlag(args[i])[0]
                argB = ParseFlag(args[i+2])[0]
                typeA = ParseFlag(args[i])[1]
                typeB = ParseFlag(args[i+2])[1]
                condition = args[i+1]

                if i+3 != len(args):
                    sepName = args[i+3]

                    if sepName not in validMulti:
                        Throw("Invalid condition(s).")

                    sep.append(sepName)

                if condition not in validConditions:
                    Throw("Unknown condition \"" + condition + "\".")

                if (typeA != "Instance" and typeB != "Instance")\
                   and (typeA not in validTypes or typeB not in validTypes):
                    Throw("Invalid data type(s).")

                if condition == "==":
                    if argA == argB:
                        answers.append(True)
                    else:
                        answers.append(False)
                elif condition == "!=":
                    if argA != argB:
                        answers.append(True)
                    else:
                        answers.append(False)
                elif condition == ">":
                    if argA > argB:
                        answers.append(True)
                    else:
                        answers.append(False)
                elif condition == ">=":
                    if argA >= argB:
                        answers.append(True)
                    else:
                        answers.append(False)
                elif condition == "<":
                    if argA < argB:
                        answers.append(True)
                    else:
                        answers.append(False)
                elif condition == "<=":
                    if argA <= argB:
                        answers.append(True)
                    else:
                        answers.append(False)

                if i+3 == len(args):
                    done = True
                else:
                    i += 4

            e = 0
            edone = False
            while not edone and len(answers) > 1:
                if args[e+3] == "and":
                    if answers[e] and answers[e+1]:
                        result.append(True)
                    else:
                        result.append(False)
                elif args[e+3] == "or":
                    if answers[e] or answers[e+1]:
                        result.append(True)
                    else:
                        result.append(False)

                if e+1 == len(answers):
                    edone = True
                else:
                    e += 1

            if len(result) > 1:
                ifStack[currentIf][0] = all(e is True for e in result)
            elif result != []:
                ifStack[currentIf][0] = result[0]
            else:
                ifStack[currentIf][0] = answers[0]
            ifStack[currentIf][1] = not ifStack[currentIf][0]
            ifStack[currentIf][2] = not ifStack[currentIf][1]

            # Disable protected variable access
            safeVariableAccess = False

            ep += 1
            continue

        elif opcode == "else" or opcode == "endif":
            if len(args) != 0:
                Throw("Invalid argument count.")

            if opcode == "endif":
                currentIf -= 1

            ep += 1
            continue

        # Timing
        elif opcode == "wait":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            argTime = args[0]
            argType = ParseFlag(argTime, False)[3]
            argFlag = ParseFlag(argTime, False)[2]

            # Function code
            if argFlag == "$" or argFlag == "#":
                argTime = ParseFlag(argTime)[0]
            else:
                if any(not char.isdigit() for char in argTime) or argType != "Int":
                    Throw("Invalid argument type (expects \"Int\".")

            argTime = float(int(argTime)/1000)

            time.sleep(argTime)

            ep += 1
            continue

        # Calls
        elif opcode == "def":
            ep += 1
            continue

        elif opcode == "call" or opcode == "jump":
            if len(args) != 1:
                Throw("Invalid argument count.")

            if opcode == "call":
                returnPoint = ep+1

            # Arguments
            argFlag = ParseFlag(args[0], False)[2]
            lblName = ParseFlag(args[0], False)[1]

            # Function code
            if argFlag == "@" or argFlag == "&" or argFlag == "#":
                Throw("Invalid variable type.")

            if argFlag == "*":
                if not lblName in labels:
                    Throw("Unknown label \""+ lblName +"\".")

                ep = labels[lblName]["point"]
            elif argFlag == "$":
                dataType = ParseFlag(args[0])[1]

                if dataType != "Int" and dataType != "Label":
                    Throw("Invalid execution point \""+ args[0] +"\".")

                ep = ParseFlag(args[0])[0]
            else:
                dataType = ParseFlag(args[0], False)[3]

                if dataType != "Int":
                    Throw("Invalid execution point \""+ args[0] +"\".")

                ep = int(args[0])

            if opcode == "call":
                currentReturn += 1

                ifStack[currentIf] = [False, False, True]
                returnStack.append(returnPoint)

            continue

        elif opcode == "return":
            if len(args) != 0:
                Throw("Invalid argument count.")

            ep = returnStack[currentReturn]
            del returnStack[currentReturn]
            currentReturn -= 1

            continue

        # Stack
        elif opcode == "push":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            argFlag = ParseFlag(args[0], False)[2]

            if argFlag == "@":
                _typeID = ParseFlag(args[0], False)[1]
                tempStack = []

                if not _typeID in types:
                    Throw("Unknown struct \""+ _typeID +"\".")

                for instance in instances:
                    if instances[instance]["instanceOf"] == _typeID:
                        item = {}
                        item["data"] = instance
                        item["type"] = "Str"
                        item["protected"] = False

                        tempStack.append(item)

                for item in reversed(tempStack):
                    stack.append(item)
            elif argFlag == "%":
                _typeID = ParseFlag(args[0], False)[1]

                if not _typeID in pointers:
                    Throw("Unknown pointer \""+ _typeID +"\".")

                pointerType = pointers[_typeID]["pointerOf"]

                if pointerType == "File":
                    pointerData = pointers[_typeID]["props"]["data"]["data"]

                    for _line in reversed(pointerData):
                        item = {}
                        item["data"] = _line
                        item["type"] = "FileStr"
                        item["protected"] = False

                        stack.append(item)
            else:
                argData = ParseFlag(args[0])[0]
                argType = ParseFlag(args[0])[1]

                if argType == "Arr":
                    if len(argData) > 0:
                        arrayName = ParseFlag(args[0])[2]
                        arrayData = variables[arrayName]["data"]

                        for entry in reversed(arrayData):
                            item = {}
                            item["data"] = entry["data"]
                            item["type"] = entry["type"]
                            item["protected"] = False

                            stack.append(item)
                else:
                    item = {}
                    item["data"] = argData
                    item["type"] = argType
                    item["protected"] = False

                    stack.append(item)

            ep += 1
            continue

        elif opcode == "pop":
            if len(args) > 1:
                Throw("Invalid argument count.")

            # Arguments
            if len(args) == 1:
                popName = args[0]
                popFlag = ParseFlag(popName, False)[2]

                if popFlag == "$" or popFlag == "#" or popFlag == "@" or popFlag == "*" or popFlag == "&" or popFlag == "%" or any(char.isdigit() for char in popName):
                    Throw("Invalid data type.")

                if popName in variables:
                    if variables[popName]["protected"]:
                        Throw("Trying to write on a protected variable. ($"+ popName +")")
            else:
                popName = 0

            # Function code:
            if popName:
                if len(stack) != 0:
                    variables[popName] = stack.pop()
                else:
                    variables[popName] = variables["EMPTY"]
                    variables[popName]["protected"] = False
            else:
                if len(stack) != 0:
                    stack.pop()

            ep += 1
            continue

        elif opcode == "read":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            popName = args[0]
            popFlag = ParseFlag(popName, False)[2]

            if popFlag == "$" or popFlag == "#" or popFlag == "*" or popFlag == "%" or any(char.isdigit() for char in popName):
                Throw("Invalid data type.")

            if popName in variables:
                if variables[popName]["protected"]:
                    Throw("Trying to write on a protected variable. ($"+ popName +")")

            # Function code:
            if len(stack) != 0:
                variables[popName] = stack[-1]
            else:
                variables[popName] = variables["EMPTY"]
                variables[popName]["protected"] = False

            ep += 1
            continue

        # FIXME When deleting a struct, delete all of its instances too.
        elif opcode == "delete":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            argName = args[0]
            argFlag = ParseFlag(argName, False)[2]

            if argFlag == "$" or argFlag == "#" or argFlag == "*" or argFlag == "%" or any(char.isdigit() for char in argName):
                Throw("Invalid struct name \""+ argName +"\".")

            # Function code
            if argName in types:
                Throw("Trying to delete an unknown struct.")

            del(types[argName])

            ep += 1
            continue

        elif opcode == "with":
            if len(args) != 1:
                Throw("Invalid argument count.")

            # Arguments
            argFlag = ParseFlag(args[0], False)[2]

            if argFlag == "$":
                argName = ParseFlag(args[0])[0]
            elif argFlag == "&":
                argName = ParseFlag(args[0], False)[1]
            else:
                Throw("Invalid data type.")

            # Function code
            if not argName in instances:
                Throw("Invalid instance \""+ str(argName) +"\".")

            current = argName

            ep += 1
            continue

        elif opcode == "end":
            current == None

            ep += 1
            continue

        # Variables
        # FIXME Exclude special characters from variable names.
        elif opcode == "set":
            if len(args) != 2:
                Throw("Invalid argument count.")

            # Arguments
            varName = ParseFlag(args[0], False)[0]
            varData = ParseFlag(args[1], False)[0]
            nameFlag = ParseFlag(args[0], False)[2]
            dataFlag = ParseFlag(args[1], False)[2]
            dataType = ParseFlag(args[1], False)[1]

            # Function code
            if nameFlag in ["$", "@", "*", "&", "%"] or any(not char.isalpha() for char in varName):
                Throw("Invalid variable name \""+ varName +"\".")

            if dataFlag == "&":
                Throw("Invalid data type.")

            if dataFlag == "@": # New instance:
                varData = varData[1:]

                if not varData in types:
                    Throw("Unknown struct \""+ varData +"\".")

                if varName in instances or varName in types:
                    Throw("Trying to overwrite a struct/instance.")

                instances[varName] = {}
                instances[varName]["instanceOf"] = varData
                instances[varName]["fields"] = {}

                for field in types[varData]["fields"]:
                    instances[varName]["fields"][field] = {}
                    instances[varName]["fields"][field]["data"] = None
                    instances[varName]["fields"][field]["type"] = types[varData]["fields"][field]["type"]

                current = varName
            elif nameFlag == "#": # Set field
                if current == None or not current in instances:
                    Throw("Invalid struct.")

                varName = varName[1:]
                dataType = ParseFlag(args[1])[1]
                varData = ParseFlag(args[1])[0]

                if not varName in instances[current]["fields"]:
                    Throw("Unknown field \""+ varName +"\".")

                fieldType = instances[current]["fields"][varName]["type"]
                if dataType != fieldType:
                    Throw("Incompatible data type \""+ dataType +"\" (field expects \""+ fieldType +"\").")

                instances[current]["fields"][varName]["data"] = varData
            elif dataFlag == "%": # New pointer:
                varData = varData[1:]

                if not varData in classes:
                    Throw("Unknown class \""+ varData +"\".")

                if varName in pointers or varName in classes:
                    Throw("Trying to overwrite a class/pointer.")

                pointers[varName] = {}
                pointers[varName]["pointerOf"] = varData
                pointers[varName]["props"] = {}

                for prop in classes[varData]["props"]:
                    pointers[varName]["props"][prop] = {}
                    pointers[varName]["props"][prop]["data"] = None
                    pointers[varName]["props"][prop]["type"] = classes[varData]["props"][prop]["type"]
            else:
                if varName in variables:
                    if variables[varName]["protected"]:
                        Throw("Trying to write on a protected variable. ($"+ varName +")")

                if varData == "Arr":
                    variables[varName] = {}
                    variables[varName]["type"] = "Arr"
                    variables[varName]["data"] = []
                else:
                    variables[varName] = {}
                    variables[varName]["type"] = ParseFlag(varData)[1]

                    varData = ParseFlag(varData)[0]

                    if variables[varName]["type"] == "Int":
                        varData = int(varData)
                    elif variables[varName]["type"] == "Flt":
                        varData = float(varData)

                    variables[varName]["data"] = varData
                variables[varName]["protected"] = False

            ep += 1
            continue

        elif opcode == "insert":
            if len(args) < 2:
                Throw("Invalid argument count.")

            varName = args[0]

            if not varName in variables:
                Throw("Unknown variable \""+ varName +"\".")

            if variables[varName]["protected"]:
                Throw("Trying to write on a protected variable. ($"+ varName +")")

            if variables[varName]["type"] != "Arr":
                Throw("Variable \"" + varName +"\" is not an array.")

            for arg in args[1:]:
                # Arguments
                argData = ParseFlag(arg)[0]
                argType = ParseFlag(arg)[1]

                # Function code
                item = {}
                item["data"] = argData
                item["type"] = argType

                variables[varName]["data"].append(item)

            ep += 1
            continue

        elif opcode == "seek":
            if len(args) != 3:
                Throw("Invalid argument count.")

            arrayName = args[0]
            index = ParseFlag(args[1])[0]
            varName = args[2]

            if not arrayName in variables:
                Throw("Unknown variable \""+ arrayName +"\".")
            if varName in variables:
                if variables[varName]["protected"]:
                    Throw("Trying to access a protected variable. ($"+ varName +")")

            if variables[arrayName]["protected"]:
                Throw("Trying to access a protected variable. ($"+ arrayName +")")

            if variables[arrayName]["type"] != "Arr":
                Throw("Variable \"" + arrayName +"\" is not an array.")

            arrayData = variables[arrayName]["data"]

            if index > len(arrayData)-1:
                Throw("Index out of range. ("+ str(index) +")")

            variables[varName] = {}
            variables[varName]["data"] = arrayData[index]["data"]
            variables[varName]["type"] = arrayData[index]["type"]
            variables[varName]["protected"] = False

            ep += 1
            continue

        elif opcode == 'frseek':
            if len(args) != 3:
                Throw('Invalid argument count.')

            pointerName = args[0]
            justName = pointerName[1:]
            index = ParseFlag(args[1])[0]
            varName = args[2]

            if not justName in pointers:
                Throw('Unknown variable \''+ pointerName +'\'.')
            if varName in variables:
                if variables[varName]['protected']:
                    Throw('Trying to access a protected variable. ($'+ varName +')')

            if pointers[justName]['pointerOf'] != 'File':
                Throw('Variable "' + pointerName +'" is not a file pointer.')

            fileData = pointers[justName]['props']['data']['data']

            if index > len(fileData)-1:
                Throw('Index out of range. ('+ str(index) +')')

            variables[varName] = {}
            variables[varName]['data'] = fileData[index]
            variables[varName]['type'] = 'FileStr'
            variables[varName]['protected'] = False

            ep += 1
            continue

        elif opcode == "size":
            if len(args) != 2:
                Throw("Invalid argument count.")

            arrayName = args[0]
            varName = args[1]
            justName = arrayName[1:]

            if nameFlag in ["@", "*", "&"] or any(not char.isalpha() for char in varName):
                Throw("Invalid variable name \""+ varName +"\".")
            elif not justName in variables and not justName in pointers:
                Throw("Unknown variable \""+ arrayName +"\".")

            nameFlag = ParseFlag(arrayName, False)[2]
            nameProtected = ParseFlag(arrayName, True)[4]

            if varName in variables:
                varProtected = ParseFlag("$"+varName, True)[4]

                if varProtected:
                    Throw("Trying to access a protected variable. ("+ varName +")")

            if nameProtected:
                Throw("Trying to access a protected variable. ("+ arrayName +")")

            arrayType = ParseFlag(arrayName, True)[1]

            if arrayType == "Arr":
                arrayData = variables[justName]["data"]
            elif arrayType == "Pointer":
                arrayData = pointers[justName]["props"]["data"]["data"]
            else:
                Throw("Invalid data type.")

            variables[varName] = {}
            variables[varName]["data"] = len(arrayData)
            variables[varName]["type"] = "Int"
            variables[varName]["protected"] = False

            ep += 1
            continue

        elif opcode == "bit":
            if len(args) != 3:
                Throw("Invalid argument count.")

            # Arguments
            varA = args[0]
            varB = args[2]
            flagA = ParseFlag(varA, False)[2]
            flagB = ParseFlag(varB, False)[2]
            typeA = ParseFlag("$"+ varA)[1]
            typeB = ParseFlag(varB, False)[3]

            if flagB in ["$", "#"]:
                typeB = ParseFlag(varB)[1]

            if flagA in ["$", "@", "*", "&"] or any(not char.isalpha() for char in varA):
                Throw("Invalid variable name \""+ varA +"\".")

            if flagB in ["@", "*", "&", "%"]:
                Throw("Invalid variable name \""+ varB +"\".")

            if flagB != "$" and any(not char.isdigit() for char in varB):
                Throw("Invalid argument type.")

            if (typeA != "Int" and typeA != "Flt") or (typeB != "Int" and typeB != "Flt"):
                Throw("Invalid argument type(s).")

            argB = ParseFlag(args[2])[0]
            operation = args[1]

            # Function code
            if not operation in validOperations:
                Throw("Unknown operation \""+ operation +"\".")

            if flagA == "#": # Set field
                if current == None or not current in instances:
                    Throw("Invalid struct.")

                varName = varA[1:]

                if not varName in instances[current]["fields"]:
                    Throw("Unknown field \""+ varName +"\".")

                fieldType = instances[current]["fields"][varName]["type"]
                if typeB != fieldType:
                    Throw("Incompatible data type \""+ typeB +"\" (field expects \""+ fieldType +"\").")

                if operation == "!":
                    instances[current]["fields"][varName]["data"] = -argB
                elif operation == "+":
                    instances[current]["fields"][varName]["data"] += argB
                elif operation == "-":
                    instances[current]["fields"][varName]["data"] -= argB
                elif operation == "*":
                    instances[current]["fields"][varName]["data"] *= argB
                elif operation == "/":
                    instances[current]["fields"][varName]["data"] /= argB
                elif operation == "&":
                    instances[current]["fields"][varName]["data"] = instances[current]["fields"][varName]["data"] & argB
                elif operation == "|":
                    instances[current]["fields"][varName]["data"] = instances[current]["fields"][varName]["data"] | argB
                elif operation == "~":
                    instances[current]["fields"][varName]["data"] = ~ argB
                elif operation == "^":
                    instances[current]["fields"][varName]["data"] = instances[current]["fields"][varName]["data"] ^ argB
                elif operation == "<<":
                    instances[current]["fields"][varName]["data"] = instances[current]["fields"][varName]["data"] << argB
                elif operation == ">>":
                    instances[current]["fields"][varName]["data"] = instances[current]["fields"][varName]["data"] >> argB
            else:
                if not varA in variables:
                    Throw("Unknown variable.")

                if operation == "!":
                    variables[varA]["data"] = -argB
                elif operation == "+":
                    variables[varA]["data"] += argB
                elif operation == "-":
                    variables[varA]["data"] -= argB
                elif operation == "*":
                    variables[varA]["data"] *= argB
                elif operation == "/":
                    variables[varA]["data"] /= argB
                elif operation == "&":
                    variables[varA]["data"] = variables[varA]["data"] & argB
                elif operation == "|":
                    variables[varA]["data"] = variables[varA]["data"] | argB
                elif operation == "~":
                    variables[varA]["data"] = ~ argB
                elif operation == "^":
                    variables[varA]["data"] = variables[varA]["data"] ^ argB
                elif operation == "<<":
                    variables[varA]["data"] = variables[varA]["data"] << argB
                elif operation == ">>":
                    variables[varA]["data"] = variables[varA]["data"] >> argB

            ep += 1
            continue

        # I/O
        elif opcode == "print":
            if len(args) == 0:
                print
            else:
                i = 1
                for arg in args:
                    # Arguments
                    argData = ParseFlag(arg)[0]
                    argType = ParseFlag(arg)[1]

                    # Function code
                    if i == len(args):
                        if argType == "FileStr":
                            sys.stdout.write(str(argData))
                            continue

                        if argType == "Str":
                            if len(argData) > 1:
                                if argData[-1] != ",":
                                    print argData
                                else:
                                    sys.stdout.write(argData[:-2])
                            else:
                                if argData != ",":
                                    print argData
                                else:
                                    sys.stdout.write(argData[:-1])
                        else:
                            print str(argData)
                    else:
                        sys.stdout.write(str(argData))

                    i += 1

            ep += 1
            continue

        elif opcode == "fread":
            if len(args) != 2:
                Throw("Invalid argument count.")

            # Arguments
            varName = args[0]
            varFlag = ParseFlag(varName, False)[2]
            varType = ParseFlag("%"+varName)[0]
            fileName = ParseFlag(args[1])[0]

            # Function code
            if varFlag in ["$", "#", "@", "*", "&", "%"] or any(not char.isalpha() for char in varName):
                Throw("Invalid variable name \""+ varName +"\".")

            if varType != "<PointerOf File>":
                Throw("FREAD requires a <PointerOf File>, not a "+ varType +".")

            try:
                dataFile = open(fileName)
            except:
                Throw("Could not open file \""+ fileName +"\".")

            pointers[varName]["props"]["name"]["data"] = fileName
            pointers[varName]["props"]["data"]["data"] = []
            pointers[varName]["props"]["size"]["data"] = 0

            for line in dataFile.readlines():
                for c in line:
                    pointers[varName]["props"]["size"]["data"] += 1

                # line = line.strip("\r\n")
                pointers[varName]["props"]["data"]["data"].append(line)

            # print pointers[varName]["props"]["data"]["data"]
            # print pointers[varName]

            ep += 1
            continue

        # FIXME Handle wrong inputs.
        elif opcode == "input":
            if len(args) != 2:
                Throw("Invalid argument count.")

            # Arguments
            varName = args[0]
            varFlag = ParseFlag(varName, False)[2]
            varType = args[1]

            # Function code
            if varFlag == "$" or varFlag == "#" or varFlag == "@" or varFlag == "*" or varFlag == "&" or any(char.isdigit() for char in varName):
                Throw("Invalid variable name \""+ varName +"\".")

            if not varType in validTypes:
                Throw("Invalid data type \""+ varType +"\".")

            inData = raw_input()

            variables[varName] = {}
            variables[varName]["type"] = varType

            if varType == "Str":
                variables[varName]["data"] = str(inData)
            elif varType == "Int":
                variables[varName]["data"] = int(inData)
            else:
                variables[varName]["data"] = float(inData)

            variables[varName]["protected"] = False

            ep += 1
            continue

        # Default
        else:
            Throw("Unknown opcode \""+ opcode +"\".")
            sys.exit(1)

    print "EOF"
