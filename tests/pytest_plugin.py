import os


def pytest_load_initial_conftests(early_config, parser, args):
    """Configure test runs."""
    # set env variable
    os.environ['LEAFLETS_TEST'] = 'test.py'
