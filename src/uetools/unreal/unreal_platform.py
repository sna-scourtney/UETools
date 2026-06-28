from __future__ import annotations

from enum import StrEnum, Enum
from pathlib import Path


class UnrealPlatform(StrEnum):
    """
    Unreal Engine's canonical vocabulary for the platforms it supports,
    using the same names UE itself uses in config files and build tooling.
    """
    UNKNOWN  = "Unknown"
    WINDOWS  = "Windows"
    LINUX    = "Linux"
    MAC      = "Mac"
    ANDROID  = "Android"
    IOS      = "iOS"

    def is_editor_host(self) -> bool:
        """
        :return: True if the Unreal Editor can run on this platform.
        """
        return self in (UnrealPlatform.WINDOWS, UnrealPlatform.LINUX, UnrealPlatform.MAC)

    def to_unreal_name(self) -> str:
        """
        :return: The platform name as used in Unreal Engine configs (the enum
            value itself, since that is already the UE canonical name).
        """
        return self.value


class UEConfigSource(Enum):
    """
    Identifies a source of Unreal Engine configuration data by its role,
    abstracting away the underlying file path or storage mechanism. This
    leaves open the possibility of non-file sources (e.g. a database) in
    the future without changing the query API.

    Entries with per_version=True require an EngineLocation when queried,
    since their path includes the engine version number.
    """
    INSTALLATIONS   = (Path("Install.ini"),        False)
    EDITOR_SETTINGS = (Path("EditorSettings.ini"), True)

    def __init__(self, filename: Path, per_version: bool):
        self.filename    = filename
        self.per_version = per_version
