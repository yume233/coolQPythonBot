import nonebot
import config
import os
import re

PLUGINS_DIR = 'plugins'
PYTHON_MOUDLE_REGEXP = r'^([a-zA-Z]\w*)\.py$'


# def __cleanSpacesInList(theList: list):
#     while '' in theList:
#         theList.remove('')
#     return theList


# def scanPythonFiles(workDir: str, programDir: str = os.getcwd()):
#     theRE = re.compile(PYTHON_MOUDLE_REGEXP)
#     pluginsList = []
#     for path, subdir, file in os.walk(workDir):
#         relPath = os.path.relpath(path,workDir)
#         for perFile in file:
#             if theRE.match(perFile):
#                 fullFilePath = os.path.join(path,perFile)
#                 moudleName = __cleanSpacesInList(theRE.split(perFile))[0]
#                 packageName = relPath.replace('.','').replace('/','.') + '.' + moudleName
#                 pluginsList.append((fullFilePath,packageName))
#     return pluginsList


# def getPluginList(workDir: str = os.getcwd()):
#     pluginsDir = os.path.join(workDir, PLUGINS_DIR)
#     pluginsList = []
#     for pluginPath in os.listdir(pluginsDir):
#         if os.path.isdir(pluginPath):
#             pluginName = os.path.split(pluginPath)[1]
#             pluginPackageName = PLUGINS_DIR + '.' + pluginName
#             pluginsList.append((pluginPath, pluginPackageName))
#     return pluginsList


if __name__ == "__main__":
    nonebot.init(config)
    pluginsFullDir = os.path.join(os.getcwd(),PLUGINS_DIR)
    nonebot.load_plugins(pluginsFullDir,PLUGINS_DIR)
    nonebot.run(host='127.0.0.1', port=8000)
