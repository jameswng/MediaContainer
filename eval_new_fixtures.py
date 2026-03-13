from pathlib import Path
from mediacontainer.media_container import MediaContainer

for fixture in ["multiple_episodes", "mixed_scrambled_and_clear", "ambiguous_splits"]:
    print(f"\n--- {fixture} ---")
    paths = [Path(line.strip()) for line in (Path("tests/fixtures") / f"{fixture}.dir").read_text().splitlines() if line.strip()]
    containers = MediaContainer.from_paths(paths)
    print(f"Container count: {len(containers)}")
    for i, c in enumerate(containers):
        print(f"  Container {i+1}: '{c.name}'")
        print(f"    files: {len(c.files)}")
        print(f"    scrambled: {c.scrambled}")
        print(f"    unaffiliated: {c.unaffiliated}")
        print(f"    archives: {len(c.archives)}")
        print(f"    playable: {len(c.playable)}")
        print(f"    split_media: {len(c.split_media)}")
        print(f"    misc: {len(c.misc)}")
