
from sdks.novavision.src.helper.package import PackageHelper
from components.Regex.src.models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor, RegexExecutorOutputs, RegexExecutorResponse, RegexExecutor, OutputData


def build_response_regex(context):
    outputData = OutputData(value=context.outputData)
    regexExecutorOutputs = RegexExecutorOutputs(outputData=outputData)
    regexExecutorResponse = RegexExecutorResponse(outputs=regexExecutorOutputs)
    regexExecutor = RegexExecutor(value=regexExecutorResponse)
    executor = ConfigExecutor(value=regexExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
