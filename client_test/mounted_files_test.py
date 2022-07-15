import platform
import pytest
import subprocess
import sys
from pathlib import Path


@pytest.fixture
def venv_path(tmp_path):
    venv_path = tmp_path
    subprocess.run([sys.executable, "-m", "venv", venv_path, "--copies", "--system-site-packages"])
    # Install Modal and a tiny package in the venv.
    subprocess.run([venv_path / "bin" / "python", "-m", "pip", "install", "-e", "client"])
    subprocess.run([venv_path / "bin" / "python", "-m", "pip", "install", "--force-reinstall", "six"])
    yield venv_path


script_path = "pkg_a/script.py"


def test_mounted_files_script(test_dir):
    p = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        cwd=test_dir / Path("supports"),
        env={"PYTHONPATH": str(test_dir / Path("supports"))},
    )
    stdout = p.stdout.decode("utf-8")
    stderr = p.stderr.decode("utf-8")
    print("stdout: ", stdout)
    print("stderr: ", stderr)
    files = stdout.splitlines()

    assert len(files) == 7
    # Assert everything from `pkg_a` is in the output.
    assert any(["a.py" in f for f in files])
    assert any(["c.py" in f for f in files])
    assert not any(["d.py" in f for f in files])
    assert any(["e.py" in f for f in files])
    assert any(["script.py" in f for f in files])

    # Assert everything from `pkg_b` is in the output.
    assert any(["__init__.py" in f for f in files])
    assert any(["f.py" in f for f in files])
    assert any(["h.py" in f for f in files])

    # Assert nothing from `pkg_c` is in the output.
    assert not any(["i.py" in f for f in files])
    assert not any(["k.py" in f for f in files])


def test_mounted_files_package(test_dir):
    p = subprocess.run([sys.executable, "-m", "pkg_a.package"], cwd=test_dir / Path("supports"), capture_output=True)
    stdout = p.stdout.decode("utf-8")
    stderr = p.stderr.decode("utf-8")
    print("stdout: ", stdout)
    print("stderr: ", stderr)
    files = stdout.splitlines()

    assert len(files) == 11

    # Assert everything from `pkg_a` is in the output.
    assert any(["a.py" in f for f in files])
    assert any(["c.py" in f for f in files])
    assert any(["d.py" in f for f in files])
    assert any(["e.py" in f for f in files])
    assert any(["script.py" in f for f in files])
    assert any(["package.py" in f for f in files])

    # Assert everything from `pkg_b` is in the output.
    assert any(["__init__.py" in f for f in files])
    assert any(["f.py" in f for f in files])
    assert any(["h.py" in f for f in files])

    # Assert nothing from `pkg_c` is in the output.
    assert not any(["i.py" in f for f in files])
    assert not any(["k.py" in f for f in files])


@pytest.mark.skipif(platform.system() == "Windows", reason="venvs behave differently on Windows.")
def test_mounted_files_sys_prefix(test_dir, venv_path):
    # Run with venv activated, so it's on sys.prefix.
    p = subprocess.run(
        [venv_path / "bin" / "python", script_path],
        capture_output=True,
        cwd=test_dir,
    )
    stdout = p.stdout.decode("utf-8")
    stderr = p.stderr.decode("utf-8")
    print("stdout: ", stdout)
    print("stderr: ", stderr)
    files = stdout.splitlines()

    assert len(files) == 4
    assert any(["a.py" in f for f in files])
    assert any(["c.py" in f for f in files])
    assert not any(["d.py" in f for f in files])
    assert any(["e.py" in f for f in files])
    assert any(["script.py" in f for f in files])
