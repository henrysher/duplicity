"""Automatically loaded on py.test runs"""

def pytest_configure(config):
    """Hook for collecting and handling py.test options, and for doing other
    broad test setup procedures such as creating a temporary working dir."""

    print config.mktemp('duplicity').chdir()

