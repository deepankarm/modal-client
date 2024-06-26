# Copyright Modal Labs 2022
from modal import App, Mount

app = App()


@app.function()
def num_mounts(_x):
    mount = Mount.from_local_python_packages("module_1")
    return len(mount.entries)
