def readConfig():
    from utils.configsReader import configsReader, touch, filePath
    configPath = filePath(__file__, 'config.yml')
    defaultPath = filePath(__file__, 'default.yml')
    return configsReader(touch(configPath), defaultPath)


Config = readConfig()