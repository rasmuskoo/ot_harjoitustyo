"""Invoke tasks for running the application and quality checks."""

from invoke import task


@task
def start(context):
    """Start the desktop application."""
    context.run("python -m src.main", pty=True)


@task
def test(context):
    """Run the test suite with pytest."""
    context.run("pytest src/tests", pty=True)


@task(name="coverage-report")
def coverage_report(context):
    """Generate an HTML coverage report based on test execution."""
    context.run("coverage run -m pytest src/tests", pty=True)
    context.run("coverage html", pty=True)
    print("Coverage report generated at htmlcov/index.html")
