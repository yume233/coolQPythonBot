from datetime import timedelta
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

import confuse

CONFIG_DIR = Path(".") / "configs"
DEFAULT_DIR = CONFIG_DIR / "default"


_T = TypeVar("_T")


class ConfigSubView(confuse.Subview):
    def get(self, template: Optional[Type[_T]] = None) -> _T:
        return super().get(template=template or confuse.REQUIRED)  # type:ignore

    def as_str(self) -> str:
        return super().as_str()  # type:ignore

    def as_number(self) -> int:
        return super().as_number()  # type:ignore

    def as_bool(self) -> bool:
        return self.get(bool)  # type:ignore

    def as_path(self) -> Path:
        return super().as_path()  # type:ignore

    def as_dict(self) -> dict:
        return self.get(dict)  # type:ignore

    def as_iterable(self, serializer: Optional[Type[_T]] = None) -> _T:
        value = self.get(list)
        return value if serializer is None else serializer(value)  # type:ignore

    def __getitem__(self, key: str):
        return self.__class__(self, key)


class AppConfig(confuse.Configuration):
    def __init__(self, name: str, path: Path, default: Optional[Path] = None):
        self._config_path = path
        self._config = self._config_path / (name + ".yml")
        self._default = None if (default is None) else (default / (name + ".yml"))
        super().__init__(name)

    def config_dir(self) -> str:
        Path(self._config_path).mkdir(exist_ok=True, parents=True)
        return str(self._config_path)

    def user_config_path(self) -> str:
        return str(self._config)

    def _add_default_source(self):
        if self._default is None:
            return
        assert self._default.is_file()
        data = confuse.load_yaml(self._default, loader=self.loader)
        self.add(confuse.ConfigSource(data, filename=str(self._default), default=True))

    def _add_user_source(self):
        if not Path(self._config).is_file():
            Path(self._config).write_bytes(self._default.read_bytes())
        data = confuse.load_yaml(self._config, loader=self.loader)
        self.add(confuse.ConfigSource(data, filename=str(self._config), default=True))

    def __getitem__(self, key: str) -> ConfigSubView:
        return ConfigSubView(self, key)


class BotConfig(AppConfig):
    def __init__(
        self, name: str, path: Optional[Path] = None, default: Optional[Path] = None
    ):
        super().__init__(name, path or CONFIG_DIR, default=default or DEFAULT_DIR)


class PluginConfig(BotConfig):
    pass


Config = BotConfig("bot")
VERSION: str = Config["general"]["version"].as_str()

NONEBOT_CONFIG: Dict[str, Any] = {
    "driver": Config["server"]["driver"].as_str(),
    "host": IPv4Address(Config["server"]["listen"].as_str()),
    "port": Config["server"]["port"].as_number(),
    "debug": Config["general"]["debug"].as_bool(),
    "api_root": Config["upstream"]["api_root"].as_dict(),
    "api_timeout": Config["upstream"]["api_timeout"].as_number(),
    "access_token": Config["upstream"]["access_token"].get(),
    "secret": Config["upstream"]["secret"].get(),
    "superusers": Config["bot"]["superusers"].as_iterable(set),
    "nickname": Config["bot"]["nickname"].as_iterable(set),
    "command_start": Config["bot"]["command_start"].as_iterable(set),
    "command_sep": Config["bot"]["command_sep"].as_iterable(set),
    "session_expire_timeout": timedelta(
        seconds=Config["bot"]["session_expire_timeout"].as_number()
    ),
}
