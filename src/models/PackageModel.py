from pydantic import Field, validator
from typing import List, Optional, Union, Literal, Dict
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, Config, Detection



class InputData(Input):
    name: Literal["inputData"] = "inputData"
    value: Union[List[Image], Image, List[Detection], Detection, Dict, List, str]
    type: str = "object"


class OutputData(Output):
    name: Literal["outputData"] = "outputData"
    value: Union[List[Image], Image, List[Detection], Detection, Dict, List, str]
    type: str = "object"

    class Config:
        title = "Output Data"


class FlagAscii(Config):
    name: Literal["flagAscii"] = "flagAscii"
    value: Literal["A"] = "A"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "ASCII (re.A)"


class FlagIgnoreCase(Config):
    name: Literal["flagIgnoreCase"] = "flagIgnoreCase"
    value: Literal["I"] = "I"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Ignore Case (re.I)"


class FlagMultiline(Config):
    name: Literal["flagMultiline"] = "flagMultiline"
    value: Literal["M"] = "M"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Multiline (re.M)"


class FlagDotAll(Config):
    name: Literal["flagDotAll"] = "flagDotAll"
    value: Literal["S"] = "S"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Dot All (re.S)"


class FlagVerbose(Config):
    name: Literal["flagVerbose"] = "flagVerbose"
    value: Literal["X"] = "X"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Verbose (re.X)"


class ConfigFlags(Config):

    name: Literal["configFlags"] = "configFlags"
    value: List[Union[
            FlagAscii,
            FlagIgnoreCase,
            FlagMultiline,
            FlagDotAll,
            FlagVerbose,
    ] ]
    type: Literal["object"] = "object"
    field: Literal["selectBox"] = "selectBox"

    class Config:
        title = "Regex Flags"
        json_schema_extra = {
            "shortDescription": "Select one or more re flags (A, I, M, S, X)"
        }


class ConfigFlagsDisabled(Config):
    """
    Disable regex flags usage.
    """

    name: Literal["configFlagsDisabled"] = "configFlagsDisabled"
    value: Literal["disable"] = "disable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Disable"


class ConfigFlagsEnabled(Config):
    """
    Enable regex flags and show flags selector.
    """

    name: Literal["configFlagsEnabled"] = "configFlagsEnabled"
    value: Literal["enable"] = "enable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    configFlags: ConfigFlags

    class Config:
        title = "Enable"


class ConfigFlagsMode(Config):
    name: Literal["configFlagsMode"] = "configFlagsMode"
    value: Union[ConfigFlagsDisabled, ConfigFlagsEnabled]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Flags"
        json_schema_extra = {
            "shortDescription": "Enable or disable regex flags"
        }

class ConfigPattern(Config):
    """
    Regular expression pattern applied to the input data.
    Supports named groups, backreferences and advanced constructs.
    """

    name: Literal["configPattern"] = "configPattern"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["Enter regex pattern"] = "Enter regex pattern"

    class Config:
        title = "Pattern"
        json_schema_extra = {
            "shortDescription": "Regex pattern (supports named groups and backreferences)"
        }


class ConfigMaxSplit(Config):
    """
    Maximum number of splits for the 'split' method.
    0 means no limit.
    """

    name: Literal["configMaxSplit"] = "configMaxSplit"
    value: int = Field(default=0, ge=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["0 = no limit"] = "0 = no limit"

    class Config:
        title = "Max Split"
        json_schema_extra = {
            "shortDescription": "Max number of splits for split() (0 = no limit)"
        }


class ConfigReplacement(Config):
    """
    Replacement template for 'sub' and 'subn' methods.
    Supports backreferences like \\1 or \\g<name>.
    """

    name: Literal["configReplacement"] = "configReplacement"
    value: str = Field(default="")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["Replacement template"] = "Replacement template"

    class Config:
        title = "Replacement"
        json_schema_extra = {
            "shortDescription": "Replacement text for sub/subn (supports backreferences)"
        }


class ConfigKeyInput(Config):
    """
    Specifies the key name to apply regex on within a dictionary input.
    If the input is a dict, regex will be applied to the value of this key.
    Leave empty to apply regex on the full input.
    """

    name: Literal["configKeyInput"] = "configKeyInput"
    value: str = Field(default="", min_length=0)
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["key name"] = "key name "

    class Config:
        title = "Key"
        json_schema_extra = {
            "shortDescription": "Enter the dictionary key whose value will be used for regex operations. Leave empty to use the full input."
        }

class KeyInputDisabled(Config):
    """
    Disable key input usage.
    """

    name: Literal["keyInputDisabled"] = "keyInputDisabled"
    value: Literal["disable"] = "disable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Disable"


class KeyInputEnabled(Config):
    """
    
    """

    name: Literal["keyInputEnabled"] = "keyInputEnabled"
    value: Literal["enable"] = "enable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    configKeyInput: ConfigKeyInput

    class Config:
        title = "Enable"


class ConfigKeyInputMode(Config):
    name: Literal["ConfigKeyInputMode"] = "ConfigKeyInputMode"
    value: Union[KeyInputDisabled, KeyInputEnabled]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Key Input"
        json_schema_extra = {
            "shortDescription": "Enable or disable key input "
        }

class MethodMatch(Config):
    name: Literal["methodMatch"] = "methodMatch"
    value: Literal["match"] = "match"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "match"


class MethodSearch(Config):
    name: Literal["methodSearch"] = "methodSearch"
    value: Literal["search"] = "search"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "search"


class MethodFullmatch(Config):
    name: Literal["methodFullmatch"] = "methodFullmatch"
    value: Literal["fullmatch"] = "fullmatch"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "fullmatch"


class MethodFindall(Config):
    name: Literal["methodFindall"] = "methodFindall"
    value: Literal["findall"] = "findall"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "findall"


class MethodFinditer(Config):
    name: Literal["methodFinditer"] = "methodFinditer"
    value: Literal["finditer"] = "finditer"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "finditer"


class MethodSplit(Config):
    name: Literal["methodSplit"] = "methodSplit"
    value: Literal["split"] = "split"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    configMaxSplit: ConfigMaxSplit

    class Config:
        title = "split"


class MethodSub(Config):
    name: Literal["methodSub"] = "methodSub"
    value: Literal["sub"] = "sub"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    configReplacement: ConfigReplacement

    class Config:
        title = "sub"


class MethodSubn(Config):
    name: Literal["methodSubn"] = "methodSubn"
    value: Literal["subn"] = "subn"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    configReplacement: ConfigReplacement

    class Config:
        title = "subn"


class ConfigMethod(Config):
    """
    Select which Regex operation to apply to inputData.
    """

    name: Literal["configMethod"] = "configMethod"
    value: Union[
        MethodMatch,
        MethodSearch,
        MethodFullmatch,
        MethodFindall,
        MethodFinditer,
        MethodSplit,
        MethodSub,
        MethodSubn,
    ]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Regex Method"
        json_schema_extra = {
            "shortDescription": "Select Regex method (match, search, findall, split, sub, ...)",
        }

class RegexExecutorInputs(Inputs):
    inputData: InputData


class RegexExecutorConfigs(Configs):
    configFlagsMode: ConfigFlagsMode
    configKeyInputMode: ConfigKeyInputMode
    configPattern: ConfigPattern
    configMethod: ConfigMethod



class RegexExecutorOutputs(Outputs):
    outputData: OutputData



class RegexExecutorRequest(Request):
    inputs: Optional[RegexExecutorInputs]
    configs: RegexExecutorConfigs

    class Config:
        json_schema_extra = {
            "target": "configs",
        }


class RegexExecutorResponse(Response):
    outputs: RegexExecutorOutputs


class RegexExecutor(Config):
    name: Literal["Regex"] = "Regex"
    value: Union[RegexExecutorRequest, RegexExecutorResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Regex Toolkit"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }


class ConfigExecutor(Config):
    name: Literal["configExecutor"] = "configExecutor"
    value: Union[RegexExecutor]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Task"
        json_schema_extra = {
            "target": "value"
        }


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["Regex"] = "Regex"
