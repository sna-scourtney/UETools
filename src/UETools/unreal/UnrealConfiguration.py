from __future__ import annotations

from pathlib import Path

from UETools.unreal.UnrealPlatform import UEConfigSource
from UETools.unreal.InstallationRegistry import EngineLocation, InstallationRegistry
from UETools.unreal.UnrealProject import UnrealProject


class UnrealConfiguration:
    """
    Top-level interface to the local Unreal Engine configuration. Coordinates
    access to engine installation locations, editor settings, and project
    search paths, insulating the rest of the application from platform-specific
    file locations and formats.

    Construct once per app run; the underlying InstallationRegistry is a
    singleton by convention.
    """

    def __init__(self):
        self._registry = InstallationRegistry.for_host()

    @property
    def locations(self) -> list[EngineLocation]:
        """
        :return: All registered Unreal Engine installations on this host.
        """
        return self._registry.locations

    def engine_for_version(self, version: str) -> EngineLocation | None:
        """
        Returns the EngineLocation for the given version string, or None if
        that version is not registered on this host.

        :param version: Version string as it appears in Install.ini (e.g. "5.7").
        """
        return next((loc for loc in self._registry.locations if loc.version == version), None)

    def engine_for_project(self, project: UnrealProject) -> EngineLocation | None:
        """
        Returns the EngineLocation associated with the given project, by
        reading its EngineAssociation and looking it up in the registry.

        :param project: The project whose engine location to find.
        :return: The matching EngineLocation, or None if the associated engine
            version is not registered on this host.
        """
        association = project.engine_association
        if association is None:
            return None
        return self.engine_for_version(association)

    def project_search_paths(self) -> list[Path]:
        """
        Returns the union of CreatedProjectPaths across all per-version
        EditorSettings.ini files. Reading all versions and taking the union
        is necessary because Epic does not guarantee this value is replicated
        identically across engine versions.

        :return: Deduplicated list of parent directories to search for projects.
        """
        seen: set[Path] = set()
        paths: list[Path] = []
        for loc in self._registry.locations:
            raw = self._registry.read_ini(
                UEConfigSource.EDITOR_SETTINGS,
                '/Script/UnrealEd.EditorSettings',
                'CreatedProjectPaths',
                location=loc,
            )
            if raw:
                path = Path(raw)
                if path not in seen:
                    seen.add(path)
                    paths.append(path)
        return paths

    def read_ini(self, source: UEConfigSource, section: str, key: str,
                 location: EngineLocation | None = None) -> str | None:
        """
        Reads a single value from a UE configuration source, without the
        caller needing to know any file paths.

        :param source: Which configuration source to read from.
        :param section: The INI section name.
        :param key: The key within that section.
        :param location: Required for per-version sources.
        :return: The value string, or None if absent.
        """
        return self._registry.read_ini(source, section, key, location)
