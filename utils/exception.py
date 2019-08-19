class BaseBotError(Exception):
    def __init__(self, reason: str = None, trace: str = None):
        self.reason = str(reason) if reason else None
        self.trace = str(trace).upper() if trace else None
        super().__init__(reason)


class BotNetworkError(BaseBotError):
    pass


class BotProgramError(BaseBotError):
    pass


class BotNotFoundError(BotProgramError):
    pass


class BotRequestError(BotNetworkError):
    pass


class BotMessageError(BotNetworkError):
    pass


class BotPermissionError(BotProgramError):
    pass


class BotDisabledError(BotProgramError):
    pass
