import nox


# Run unit tests and perform test coverage.
@nox.session(python=["3.8", "3.9"])
def tests(session: nox.sessions.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "report")


# Run flake8 linter.
@nox.session
def lint(session: nox.sessions.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("flake8", ".")


# # Run mypy type checker.
@nox.session
def typing(session: nox.sessions.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install")
    session.run("mypy", ".")
