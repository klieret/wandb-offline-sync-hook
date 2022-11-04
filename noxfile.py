from __future__ import annotations

import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".[testing,ray]")
    session.run("pytest", *session.posargs)
