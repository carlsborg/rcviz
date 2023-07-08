import nox

@nox.session(python=["3.7","3.8", "3.9","3.10"])
def test(session):
    session.install(".")
    session.install("pytest")
    session.run("pytest")

