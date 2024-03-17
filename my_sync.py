import os
import shutil
from pathlib import Path
from typing import Dict

from sync import hash_file


def sync(source: str, dest: str):
    # IO
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # biz
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # apply action
    for action, *paths in actions:
        if action == 'copy':
            shutil.copyfile(*paths)
        if action == 'move':
            shutil.move(*paths)
        if action == 'delete':
            os.remove(paths[0])


# IO
def read_paths_and_hashes(root: str) -> Dict[str, Path]:
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn

    return hashes


# biz
def determine_actions(
        src_hashes: Dict[str, Path],
        dst_hashes: Dict[str, Path],
        src_folder: str,
        dst_folder: str,
):
    for sha, filename in src_hashes.items():
        if sha not in dst_hashes:
            sourcepath = Path(src_folder) / filename
            destpath = Path(dst_folder) / filename
            yield 'copy', sourcepath, destpath

        elif dst_hashes[sha] != filename:
            olddestpath = Path(dst_folder) / dst_hashes[sha]
            newdestpath = Path(dst_folder) / filename
            yield 'move', olddestpath, newdestpath

    for sha, filename in dst_hashes.items():
        if sha not in src_hashes:
            yield 'delete', dst_folder / filename
