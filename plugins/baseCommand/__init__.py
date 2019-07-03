from nonebot import on_command, CommandSession


@on_command('execute', aliases=('command', 'commands', '执行', '指令'))
async def execute(session: CommandSession):
    command = session.get(
        'command', prompt='What Command Would You Want to Execute?')
    result = await runCommand(command)
    await session.send(result)


@execute.args_parser
async def _(session: CommandSession):
    strippedArgs = session.current_arg_text.strip()
    if not strippedArgs:
        session.pause('No Commands Can Be Execute!')
    else:
        session.state['command'] = strippedArgs


async def runCommand(command) -> str:
    return 'Disabled!'