#!/usr/bin/env python

__version__ = "2026.06.27"

import os

import rich
import logging
from logging.handlers import BufferingHandler
from pathlib import Path, PurePath
import typer
from yamlpath import YAMLPath
from yamlpath.commands.yaml_paths import get_search_term, search_for_paths
from yamlpath.enums import PathSeparators
from yamlpath.wrappers import ConsolePrinter
from typing import Annotated

from uetools.framework import AppContext, YAMLChainMap
from pyshell.core.filesystem import path_search_subpath_list
from uetools.unreal import InstallationRegistry, EngineLocation

#### SETUP CORE ####
console = rich.console.Console()
main_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[
#    RichHandler(rich_tracebacks=True),
    BufferingHandler(capacity=1000),])

app = typer.Typer(no_args_is_help=True)

@app.command()
def version():
    typer.echo(f"UETools version: {__version__}")

@app.command(help="Show current configuration")
def config(ctx: typer.Context):
    app_ctx: AppContext = ctx.obj
    console_printer = ConsolePrinter(YAMLChainMap.logging_args)
    search = YAMLPath(app_ctx.config.yaml_data)
    processor = app_ctx.config.yaml_processor
    yaml_data = app_ctx.config.yaml_data
    for k, v in yaml_data.items():
        console.print(f"{k}: {v}\n")
    search_term = get_search_term(console_printer,">0")
    # for path in search_for_paths(console_printer, processor, yaml_data, search_term):
    #      console.print(path)

# def path_search_subpath(path: Path, subpath: PurePath, found_dirs: list[Path], *, max_depth: int = 3, depth: int = 1):
# #    console.print(f"Checking for {str(subpath)} under {str(path)} at depth {depth} of {max_depth}...")
#     if (path / subpath).is_dir():
#         if found_dirs is None:
#             raise(ValueError("Return list found_dirs must be created by caller."))
#         else:
#             found_dirs.append(path)
# #        console.print(f"Found match number {len(found_dirs)} under {str(path)}")
#     else:
#         # Iterate subdirectories only if the current level is not an
#         # engine installation, and if we are not yet at max depth.
#         if depth < max_depth:
#             for subdir in path.iterdir():
#                 if (subdir.is_dir()):
#                     path_search_subpath(subdir, subpath, found_dirs, max_depth=max_depth, depth=depth+1)

@app.command(help="List installed Unreal Engine versions")
def engines(ctx: typer.Context, *,
            max_depth: Annotated[int, typer.Option(help="Directory recursion limit (not counting the bin_subpath levels)")] = 3,
            bin_subpath: Annotated[str, typer.Option(help="Binary path under engine install root, matched to detect the engine root")] = "Engine/Binaries"
    ):
    app_ctx: AppContext = ctx.obj
    dirs = app_ctx.config.yaml_data.get("uetools", []).get("paths", []).get("engine", []).get("installed", [])
    engines: list[Path] = []
#    engine_bin_subpath = PurePath(bin_subpath)
    paths: list[Path] = [Path(dir) for dir in dirs]
    console.print(f"Checking for engine installs under {", ".join(dirs)}...")
#    path_search_subpath_list(paths, engine_bin_subpath, engines, max_depth=max_depth)
    engine_locations: list[EngineLocation] = InstallationRegistry._load_from_dir_scan(paths, max_depth=max_depth)
    if len(engine_locations) > 0:
        console.print("Engine locations:")
        for engine in engine_locations:
            console.print(f"\t{str(engine.root)}\tVersion: {engine.version}")
    else:
        console.print("No engines found.")

@app.command(help="List information about Unreal Engine projects")
def projects(ctx: typer.Context,
             names: bool = typer.Option(False, help="List project names by parent directory"),
             details: bool = typer.Option(False, help="Show detailed information about projects (implies --list)"),
             engines: bool = typer.Option(False, help="List projects by engine version"),
    ):
    app_ctx: AppContext = ctx.obj
    dirs = app_ctx.config.yaml_data.get("uetools", []).get("paths", []).get("project", [])
    home = os.path.expanduser("~")
    if details:
        names = True
    by_engine = {}
    for dir in dirs:
        if dir.startswith("~"):
            dir = home + dir[1:]
        path: Path = Path(dir)
        if not path.is_dir():
            continue
        console.print(f"Checking for projects under {dir}...")
        for subdir in path.iterdir():
            uproject = subdir / (subdir.name + ".uproject")
            if uproject.is_file():
                project = subdir.name
                with open(uproject, "rt") as uproject_file:
                    for line in uproject_file:
                        line = line.replace('"', '').replace(',','').strip()
#                        console.print(f"Line: {line}")
                        if line.startswith('EngineAssociation'):
                            engine = line.split(':')[1].strip()
                            if by_engine.get(engine) is None:
                                by_engine[engine] = [ path / project ]
                            else:
                                by_engine[engine].append(path / project)
                            break
                    if names:
                        console.print(f"Unreal project: {project}:")
                        if details:
                            console.print(f"\tProject file: {uproject}")
                            console.print(f"\tEngine Version: {engine}")
                        console.print("")
        if engines:
            engine_versions = list(by_engine.keys())
            engine_versions.sort()
            for engine in engine_versions:
                console.print(f"Engine: {engine}:")
                projects = by_engine[engine]
                projects.sort()
                for project in projects:
                    console.print(f"\t{project}", markup=False, highlight=False)
                console.print("")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    # Build (but don’t enter) tge AppContext
    app_ctx = AppContext()
    app_ctx.config.load(AppContext.get_default_config_path())
    # Let Click enter it and ensure teardown happens after the command completes
    app_ctx = ctx.with_resource(app_ctx)
    # Make it accessible to subcommands
    ctx.obj = app_ctx

if __name__ == "__main__":
    app()
