import pathlib
import subprocess


def pytest_runtest_setup(item):
    print(f"pytest_runtest_setup({item}")


def pytest_configure(config):
    print("Configure")
    subprocess.run(["pkill", "gtk4-broadwayd"])
    subprocess.Popen(["/usr/bin/gtk4-broadwayd", ":5"])
    (pathlib.Path(__file__).parent / "results").mkdir(parents=True, exist_ok=True)


def pytest_unconfigure(config):
    print("Unconfigure")
    subprocess.run(["pkill", "gtk4-broadwayd"])
