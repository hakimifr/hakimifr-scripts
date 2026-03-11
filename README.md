# hakimifr-scripts

A collection of Python scripts that I use.

## Install

One of the script requires freethreaded Python build. It works without it,
but will be much slower than using freethreaded build. Therefore I recommend
using `uv` to install this scripts collection with the freethreaded Python:

```bash
UV_MANAGED_PYTHON=1 UV_PYTHON=3.14t uv tool install https://github.com/hakimifr/hakimifr-scripts.git
```

You can, install it via pip, but then the Python version is dependant with
the one installed in your system. Most likely it's the non-freethreaded build.

```bash
pip3 install git+https://github.com/hakimifr/hakimifr-scripts.git
```

