from os import get_terminal_size

BANNER = r'''
                    ______    ____        __  __                ____        __      _    _______
  _________  ____  / / __ \  / __ \__  __/ /_/ /_  ____  ____  / __ )____  / /_    | |  / /__  /
 / ___/ __ \/ __ \/ / / / / / /_/ / / / / __/ __ \/ __ \/ __ \/ __  / __ \/ __/____| | / / /_ < 
/ /__/ /_/ / /_/ / / /_/ / / ____/ /_/ / /_/ / / / /_/ / / / / /_/ / /_/ / /_/_____/ |/ /___/ / 
\___/\____/\____/_/\___\_\/_/    \__, /\__/_/ /_/\____/_/ /_/_____/\____/\__/      |___//____/  
                                /____/                                                          
'''
COPYRIGHT = r'''
Copyright © 2019-2020 mnixry,All Rights Reserved
Project: https://github.com/mnixry/coolQPythonBot'''

if __name__ == '__main__':
    from app import initApp,nonebot
    consoleWidth = get_terminal_size().columns
    if max(len(i) for i in BANNER.splitlines()) <= consoleWidth:
        for line in BANNER.splitlines():
            blankSize = (consoleWidth-len(line)) // 2
            print(' '*blankSize+line)
    print(COPYRIGHT)
    print('='*consoleWidth)
    initApp()
    nonebot.run()
