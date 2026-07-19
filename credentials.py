"""Central Swag Labs credentials — single source of truth.

These are the public saucedemo.com demo accounts (not real secrets), kept in one place
instead of scattered across the codebase. Committed so tests, CI, and the demo all run.
If you ever point this system at a private site, move these to an env/.env file and
gitignore it (see config/__init__.py for the OpenRouter key pattern).
"""
PASSWORD = "secret_sauce"
DEFAULT_USER = "standard_user"

# Buggy demo users used to inject failures in the break matrix (all share PASSWORD).
USERS = [
    "standard_user",              # control — clean happy path
    "problem_user",               # broken selectors / missing elements
    "performance_glitch_user",    # slow loads → timeout
    "error_user",                 # checkout / flow errors
    "locked_out_user",            # cannot log in
]
