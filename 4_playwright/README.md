## Playwright Notes:

Requirement: The app is expected to be running at http://127.0.0.1:4181/

As of now, running with headless=False is still failing on Linux.
But the tests can be run in headless=True mode

```
# To run in DEBUG mode
# This won't work in Linux as of now, this command is for Bash Shell on Windows
> PWDEBUG=1 python -m pytest
```
```
# To run in PRODUCTION mode
> python -m pytest
```
```
# Code Generation
> python -m playwright codegen
```