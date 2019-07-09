from json import dumps
from math import ceil

from nonebot import CommandSession, on_command
from nonebot.permission import SUPERUSER

SPLIT_SIZE = 100


@on_command('exec', permission=SUPERUSER)
async def execute(session: CommandSession):
    execArgs = session.get('args')
    splitSize = execArgs.get('split', SPLIT_SIZE)
    await session.send('Send Args:%s' % dumps(execArgs, ensure_ascii=False))
    executeResult = getattr(session.bot, execArgs['exec'])
    returnValue = await executeResult(**execArgs)
    dumpdValue = dumps(
        returnValue, ensure_ascii=False, sort_keys=True, indent=4).split('\n')
    for i in range(ceil(len(dumpdValue) / splitSize)):
        msgSpice = dumpdValue[i * splitSize:(i + 1) * splitSize]
        sendMsg = '\n'.join(msgSpice)
        await session.send(sendMsg)


@execute.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.finish()
    argsSplited = strippedArgs.split('\n')
    argsList = {}
    for perArg in argsSplited:
        if not perArg.strip():
            continue
        key, value = perArg.strip().split('=')
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        argsList[key] = value
    session.state['args'] = argsList
