from os import get_terminal_size

import nonebot

from utils.config import NONEBOT_CONFIG
from utils.log import logger

COPYRIGHT = r"""<g>
    ____                     _ ____        __ 
   /  _/___ __  ______ ___  (_) __ )____  / /_
   / //_  // / / / __ `__ \/ / __  / __ \/ __/
 _/ /  / // /_/ / / / / / / / /_/ / /_/ / /_  
/___/ /___|__,_/_/ /_/ /_/_/_____/\____/\__/  
</g><e>
<b>Copyright © 2020 mixmoe, All Rights Reserved</b>
Project: <u>https://github.com/mixmoe/IzumiBot</u></e>"""  # noqa:W291

if __name__ == "__main__":
    width, height = get_terminal_size()
    COPYRIGHT = (
        "\n".join([i.center(width) for i in COPYRIGHT.splitlines()])
        + "\n"
        + "=" * width
    )
    logger.warning(COPYRIGHT)
    nonebot.init(**NONEBOT_CONFIG)
    nonebot.run()
