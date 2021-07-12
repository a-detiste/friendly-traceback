"""
With the exceptions of the functions that are specific to the console,
this module contains all the functions that are part of the public API.
While Friendly-traceback is still considered to be in beta stage,
we do attempt to avoid creating incompatibility for the functions
here when introducing changes.

The goal is to be even more careful to avoid introducing incompatibilities
when reaching beta stage, and planning to be always backward compatible
starting at version 1.0 -- except possibly for the required minimal
Python version.

Friendly-traceback is currently compatible with Python versions 3.6
or newer.

If you find that some additional functionality would be useful to
have as part of the public API, please let us know.
"""
import sys

valid_version = sys.version_info.major >= 3 and sys.version_info.minor >= 6

if not valid_version:  # pragma: no cover
    print("Python 3.6 or newer is required.")
    sys.exit()

del valid_version
__version__ = "0.3.164"


# ===========================================

import inspect
import warnings as _warnings
from pathlib import Path

from . import debug_helper
from . import editors_helpers
from . import base_formatters
from .config import session
from . import path_info
from .ft_gettext import current_lang

# Ensure that warnings are not shown to the end user, as they could
# cause confusion.  Eventually, we might want to interpret them like
# we do for Exceptions.
_warnings.simplefilter("ignore")
del _warnings


def exclude_file_from_traceback(full_path):
    """Exclude a file from appearing in a traceback generated by
    Friendly.  Note that this does not apply to
    the true Python traceback obtained using "debug_tb".
    """
    path_info.exclude_file_from_traceback(full_path)


def exclude_directory_from_traceback(dir_name):
    """Exclude all files found in a given directory, including sub-directories,
    from appearing in a traceback generated by Friendly.
    Note that this does not apply to the true Python traceback
    obtained using "debug_tb".
    """
    path_info.exclude_directory_from_traceback(dir_name)


def explain_traceback(redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
    information about a given exception than a standard traceback.
    Note that this excludes ``SystemExit`` and ``KeyboardInterrupt``
    which are re-raised.

    By default, the output goes to ``sys.stderr`` or to some other stream
    set to be the default by another API call. However, if::

       redirect = some_stream

    is specified, the output goes to that stream, but without changing
    the global settings.

    If the string ``"capture"`` is given as the value for ``redirect``, the
    output is saved and can be later retrieved by ``get_output()``.
    """
    session.explain_traceback(redirect=redirect)


def get_output(flush=True):
    """Returns the result of captured output as a string which can be
    written anywhere desired.

    By default, flushes all the captured content.
    However, this can be overridden if desired.
    """
    return session.get_captured(flush=flush)


def install(lang=None, redirect=None, include="explain", _debug=None):
    """
    Replaces ``sys.excepthook`` by friendly's own version.
    Intercepts, and provides an explanation for all Python exceptions except
    for ``SystemExist`` and ``KeyboardInterrupt``.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        include: controls the amount of information displayed.
        See set_include() for details.
    """
    if _debug is not None:
        debug_helper.DEBUG = _debug
    session.install(lang=lang, redirect=redirect, include=include)


def is_installed():
    """Returns True if Friendly is installed, False otherwise."""
    return session.installed


def uninstall():
    """Resets sys.excepthook to Python's default."""
    session.uninstall()


def run(
    filename,
    lang=None,
    include=None,
    args=None,
    console=True,
    formatter="repl",
    redirect=None,
    ipython_prompt=True,
):  # sourcery skip: move-assign
    """Given a filename (relative or absolute path) ending with the ".py"
    extension, this function uses the
    more complex ``exec_code()`` to run a file.

    If console is set to ``False``, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True`` (the default), the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currently only ``'en'`` (default) and ``'fr'``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised; the default is ``"friendly_tb"`` if console
    is set to ``True``, otherwise it is ``"explain"``

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...

    """
    _ = current_lang.translate
    if include is None:
        include = "friendly_tb" if console else "explain"
    if args is not None:
        sys.argv = [filename, *list(args)]
    else:
        filename = Path(filename)
        if not filename.is_absolute():
            frame = inspect.stack()[1]
            # This is the file from which run() is called
            run_filename = Path(frame[0].f_code.co_filename)
            run_dir = run_filename.parent.absolute()
            filename = run_dir.joinpath(filename)

        if not filename.exists():
            print(_("The file {filename} does not exist.").format(filename=filename))
            return

    session.install(lang=lang, include=include, redirect=redirect)
    session.set_formatter(formatter)

    module_globals = editors_helpers.exec_code(
        path=filename, lang=lang, include=include
    )
    if console:  # pragma: no cover
        start_console(
            local_vars=module_globals,
            formatter=formatter,
            banner="",
            include=include,
            ipython_prompt=ipython_prompt,
        )
    else:
        return module_globals


def set_formatter(formatter=None):
    """Sets the default formatter. If no argument is given, the default
    formatter is used.
    """
    session.set_formatter(formatter=formatter)


def start_console(  # pragma: no cover
    local_vars=None,
    formatter="repl",
    include="friendly_tb",
    lang="en",
    banner=None,
    displayhook=None,
    ipython_prompt=True,
):
    """Starts a Friendly console."""
    from . import ft_console

    ft_console.start_console(
        local_vars=local_vars,
        formatter=formatter,
        include=include,
        lang=lang,
        banner=banner,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )


# =========================================================================
# Below, we have many set_X()/get_X() pairs. The only reason why we include
# the get_X() type of functions is to make it possible to make some
# temporary changes, i.e.
#
#     saved = get_x()
#     set_X(something)
#     do_something()
#     set_X(saved)
# =========================================================================


def set_lang(lang="en"):
    """Sets the language to be used for the display.

    If no translations exist for that language, the original
    English strings will be used.
    """
    session.set_lang(lang=lang)


def get_lang():
    """Returns the current language that had been set for translations.

    Note that the value returned may not reflect truly what is being
    see by the end user: if the translations do not exist for that language,
    the default English strings are used.
    """
    return session.lang


def _include_choices():
    """Prints the available choices for arguments to set_include()"""
    choices = [repr(key) for key in base_formatters.items_groups if key != "header"]
    return ",\n        ".join(choices)


def set_include(include):
    """Specifies the information to include in the traceback.

    The allowed values are:

        {choices}
    """
    session.set_include(include)


if set_include.__doc__ is not None:  # protect against -OO optimization
    set_include.__doc__ = set_include.__doc__.format(choices=_include_choices())


def get_include():
    """Retrieves the value used to determine what to include in the
    traceback. See ``set_include()`` for details.
    """
    return session.get_include()


def set_stream(redirect=None):
    """Sets the stream to which the output should be directed.

    If the string ``"capture"`` is given as argument, the
    output is saved and can be later retrieved by ``get_output()``.

    If no argument is given, the default stream (stderr) is set.
    """
    session.set_redirect(redirect=redirect)


def get_stream():
    """Returns the value of the current stream used for output."""
    return session.write_err
