from pathlib import Path
from mediacontainer.media_container import MediaContainer

paths = [Path(f"release.part{i}.rar") for i in [1, 2, 10, 20, 3]]
containers = MediaContainer.from_paths(paths)
c = containers[0]
for f in c.archives:
    print(f.path.name)
