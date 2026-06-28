from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UnrealProject:
    """
    Encapsulates a single Unreal Engine project, as described by its .uproject
    file. Parses the file on construction and exposes its contents as typed
    properties.

    The .uproject format is JSON. Only the fields relevant to this tooling are
    currently exposed; the full parsed content is available via the raw
    property if other fields are needed.
    """
    uproject_path: Path

    def __post_init__(self):
        if not self.uproject_path.is_file():
            raise FileNotFoundError(
                f"No .uproject file found at: {self.uproject_path}")
        try:
            self._data: dict = json.loads(
                self.uproject_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse .uproject file at {self.uproject_path}: {e}") from e

    @property
    def name(self) -> str:
        """
        :return: The project name, derived from the .uproject filename stem.
        """
        return self.uproject_path.stem

    @property
    def directory(self) -> Path:
        """
        :return: The project root directory (parent of the .uproject file).
        """
        return self.uproject_path.parent

    @property
    def engine_association(self) -> str | None:
        """
        :return: The EngineAssociation value from the .uproject file, typically
            a version string (e.g. "5.7") or a GUID for source builds. None if
            the field is absent.
        """
        return self._data.get('EngineAssociation')

    @property
    def raw(self) -> dict:
        """
        :return: The full parsed contents of the .uproject file.
        """
        return self._data
