from __future__ import annotations

import rich
console = rich.get_console()

import json
from abc import ABC, abstractmethod
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path, PurePath
import platform

from uetools.unreal.unreal_platform import UnrealPlatform, UEConfigSource
from uetools.framework import path_search_subpath_list

BUILD_VERSION_PATH: PurePath = PurePath("Engine") / "Build" / "Build.version"
SAVED_CONFIG_PATH: PurePath  = PurePath("Saved") / "Config"
ENGINE_BINARIES_PATH: PurePath = PurePath("Engine") / "Binaries"
_DEFAULT_RECURSE_DEPTH: int = 3
_INI_INSTALL_SECTION: str = "Installations"


@dataclass(init=False)
class EngineLocation:
    """
    A single Unreal Engine installation: its version string and root directory.
    Version strings follow major.minor.patch convention (e.g. "5.7.4");
    patch defaults to 0 when absent from the registry entry.
    """
    version: str | None
    root: Path

    def __init__(self, root: Path, *,
                version: str | None = None,
                 major: int | None = None,
                 minor: int | None = None,
                 patch: int | None = None):
        if root is None or not root.is_dir():
            raise ValueError(f"Invalid root path {str(root)} (must be a directory).")
        self.root = root
        if version is None:
            major : int = major if major is not None else 0
            minor : int = minor if minor is not None else 0
            patch : int = patch if patch is not None else 0
            self.version = f"{major}.{minor}.{patch}"
            if self.version == "0.0.0":
                self.version = EngineLocation.version_from_root(self.root)
        else:
            self.version = version

    @property
    def major(self) -> int:
        if self.version is None:
            return 0
        return int(self.version.split('.')[0])

    @property
    def minor(self) -> int:
        if self.version is None:
            return 0
        return int(self.version.split('.')[1])

    @property
    def patch(self) -> int:
        if self.version is None:
            return 0
        parts = self.version.split('.')
        return int(parts[2]) if len(parts) > 2 else 0

    @staticmethod
    def version_from_root(root: Path) -> str | None:
        """
        Resolves the version string of a UE instance by reading
        Engine/Build/Build.version from the installation root. Returns None
        if the file is absent or malformed.
        """
        build_version = root / BUILD_VERSION_PATH
        if not build_version.is_file():
            return None
        try:
            data = json.loads(build_version.read_text())
            return f"{data['MajorVersion']}.{data['MinorVersion']}.{data['PatchVersion']}"
        except (KeyError, json.JSONDecodeError, OSError):
            return None

class InstallationRegistry(ABC):
    """
    Singleton registry of all Unreal Engine installations on the current host,
    and the authoritative source for reading any UE configuration file.

    Subclasses are named InstallationRegistry_<S>, where <S> is the exact
    string returned by platform.system() on that host (e.g.
    InstallationRegistry_Linux). Use for_host() to obtain an instance; it
    should be constructed once per app run and shared via UnrealConfiguration.
    """

    def __init__(self):
        self._locations: list[EngineLocation] = self._load()

    @classmethod
    def for_host(cls) -> InstallationRegistry:
        """
        Returns an InstallationRegistry for the current host platform.

        :raises NotImplementedError: No subclass exists for the current host.
        """
        system = platform.system()
        target = f"InstallationRegistry_{system}"
        for subclass in cls.__subclasses__():
            if subclass.__name__ == target:
                return subclass()
        raise NotImplementedError(
            f"No Unreal Engine installation registry support is available for "
            f"host platform '{system}'.")

    @classmethod
    @abstractmethod
    def unreal_platform(cls) -> UnrealPlatform:
        """
        :return: The UnrealPlatform constant for this subclass's host platform.
        """
        ...

    @classmethod
    @abstractmethod
    def config_dir(cls) -> Path:
        """
        :return: The directory containing Epic's global UE config files on this host.
        """
        ...

    @classmethod
    @abstractmethod
    def editor_config_subdir(cls) -> Path:
        """
        :return: The platform-specific subdirectory name within the per-version
            config path (e.g. Path("LinuxEditor"), Path("WindowsEditor")).
        """
        ...

    @property
    def locations(self) -> list[EngineLocation]:
        """
        :return: All registered Unreal Engine installations on this host.
        """
        return self._locations

    def read_ini(self, source: UEConfigSource, section: str, key: str,
                 location: EngineLocation | None = None) -> str | None:
        """
        Reads a single value from a UE configuration source.

        :param source: Which configuration source to read from.
        :param section: The INI section name.
        :param key: The key within that section.
        :param location: Required for per-version sources; identifies which
            engine installation's configuration to read.
        :return: The value string, or None if the source, section, or key
            is absent.
        :raises ValueError: A per-version source was given without a location.
        """
        if source.per_version:
            if location is None:
                raise ValueError(
                    f"{source.name} is a per-version config source and requires "
                    f"an EngineLocation.")
            path = (self.config_dir() / location.version / SAVED_CONFIG_PATH
                    / self.editor_config_subdir() / source.filename)
        else:
            path = self.config_dir() / source.filename

        if not path.is_file():
            return None

        # strict=False: UE INI files allow duplicate keys for array-type values.
        parser = ConfigParser(strict=False)
        # Preserve key case; ConfigParser lower-cases option names by default.
        parser.optionxform = str
        parser.read(path)
        return parser.get(section, key, fallback=None)

    @abstractmethod
    def _load(self) -> list[EngineLocation]:
        """
        Reads and parses the installation registry for this host, resolving
        any GUID-keyed entries to real version strings.
        """
        ...

    @staticmethod
    def locate_engines_from_dirs(paths: list[Path], *,
            max_depth: int = _DEFAULT_RECURSE_DEPTH,
            bin_subpath: PurePath = ENGINE_BINARIES_PATH) -> list[EngineLocation]:
        """
        This is an alternate way to locate UE installations, given a list of parent directories
        under which to search. The preferred method to find engines is using Unreal's own
        config file (see other methods in this class).

        :param dirs: list of top-level paths under which to search recursively
        :param max_depth: Maximum recursion depth, not counting the binary subpath
        :param bin_subpath: Subdirectory to engine binaries under a valid root, used for search matching
        :return: list (possibly empty) of EngineLocation objects
        """
        engines: list[Path] = []
        path_search_subpath_list(paths, bin_subpath, engines, max_depth=max_depth)
        engine_locations: list[EngineLocation] = [EngineLocation(engine) for engine in engines]
        return engine_locations

class InstallationRegistry_Linux(InstallationRegistry):
    """
    Reads the INI-format Install.ini registry used on Linux.
    Typical entry:      UE_5.7=/opt/unreal/5.7.4
    Source-build entry: {B4A3A5AA-...}=/opt/unreal/custom
    """

    @classmethod
    def unreal_platform(cls) -> UnrealPlatform:
        return UnrealPlatform.LINUX

    @classmethod
    def config_dir(cls) -> Path:
        return Path.home() / ".config" / "Epic" / "UnrealEngine"

    @classmethod
    def editor_config_subdir(cls) -> Path:
        return Path("LinuxEditor")

    def _load(self) -> list[EngineLocation]:
        registry_path = self.config_dir() / UEConfigSource.INSTALLATIONS.filename
        if not registry_path.is_file():
            return []

        # strict=False: UE INI files allow duplicate keys for array-type values.
        parser = ConfigParser(strict=False)
        # Preserve key case; ConfigParser lower-cases option names by default,
        # which would corrupt UE_ prefixes and GUID braces.
        parser.optionxform = str
        parser.read(registry_path)

        locations: list[EngineLocation] = []
        if not parser.has_section(_INI_INSTALL_SECTION):
            # Missing config section; leave the list empty
            return locations
        for key, value in parser[_INI_INSTALL_SECTION].items():
            root = Path(value.strip())
            if key.startswith('{'):
                # GUID key: source build registered without a version string.
                version = EngineLocation.version_from_root(root)
                if version is None:
                    continue
            else:
                version = key[len("UE_"):] if key.upper().startswith("UE_") else key
            locations.append(EngineLocation(version=version, root=root))

        return locations
