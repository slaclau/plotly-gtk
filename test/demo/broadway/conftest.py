import pathlib
import subprocess


def pytest_configure(config):
    subprocess.run(["pkill", "gtk4-broadwayd"])
    subprocess.Popen(["/usr/bin/gtk4-broadwayd", ":5"])
    (pathlib.Path(__file__).parent / "results").mkdir(parents=True, exist_ok=True)


def pytest_unconfigure(config):
    subprocess.run(["pkill", "gtk4-broadwayd"])
