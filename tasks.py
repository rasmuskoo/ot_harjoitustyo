"""Invoke tasks for running the application and quality checks."""

import subprocess
import sys

from invoke import task


@task
def start(context):
    """Start the desktop application."""
    del context
    subprocess.run([sys.executable, "-u", "-m", "src.main"], check=False)


# Codex generated code begins
@task
def gui(context):
    """Start the Tkinter application."""
    del context
    subprocess.run([sys.executable, "-u", "-m", "src.gui.app"], check=False)


# Codex generated code ends
@task
def test(context):
    """Run the test suite with pytest."""
    context.run("pytest src/tests")


@task(name="coverage-report")
def coverage_report(context):
    """Generate an HTML coverage report based on test execution."""
    context.run("coverage run -m pytest src/tests")
    context.run("coverage html")
    print("Coverage report generated at htmlcov/index.html")


@task
def lint(context):
    """Run pylint for application code."""
    context.run(
        "PYLINTHOME=.pylint.d pylint --rcfile=.pylintrc "
        "src/main.py src/entities src/repositories src/services src/gui"
    )
