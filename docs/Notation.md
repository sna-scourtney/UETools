# Notational Conventions

These conventions apply to the documentation for UETools.
Any exceptions are noted in the accompanying text.

## Placeholder Text

In many cases the text of a command or output is a placeholder
for a value that you must substitute. These are enclosed in
curly brackets ("{}") and provide an arbitrary (but hopefully descriptive)
placeholder name, for example:

    $ python3 -m pip install {python_package}

An exception to this is Linux environment variables which are
also enclosed in curly brackets but are preceded by a dollar
sign ("$"), for example:

    $ export PYTHONPATH=${PYTHONPATH}:{python_package_path}

In this case the string "${PYTHONPATH}" retrieves the contents
of the environment variable PYTHONPATH, and the string
"{python_package_path}" is a placeholder for the actual path
you wish to append. Type the environment variable name and
its enclosing dollar sign and brackets literally as shown,
but substitute your own package path (without the curly
brackets) for "{python_package_path}".[^placeholders]

## File Paths

File paths use the Linux convention of forward slashes ("/"),
which works on Mac as well. On Windows, use backslashes ("\\").
Also note that Linux and Mac do not have drive letters, so
add those if you need to on Windows.

Paths beginning with a tilde ("~") are relative to the user's
home directory, for example:

    $ cd ~/MyProject/

indicates a directory "MyProject" in the user's home directory.
Again, substitute if needed for your system.

## Shell commands

Unless otherwise noted, all shell commands are assumed to be
for Linux under the bash, ash, zsh, or similar shell.

### Operating System Shell

Commands to be run as a normal user are prefixed with the
traditional "$" prompt, which you do not type. This is to
clarify the beginning of a command in case your viewer
wraps lines.

Example:

    $ ls -l /usr/local/src/

Commands that must be run as a superuser ("root" on Linux)
are prefixed with the "#" prompt. On Linux, you can run these
commands by typing "sudo" before the command, from a regular
user account.

Example:

    # mkdir /usr/local/src/MyProject

would be run from a root shell, or can be run from a regular
user account with:

    $ sudo mkdir /usr/local/src/MyProject

The "sudo" command requires your regular user account to be
authorized in the system configuration. Refer to the "sudo"
documentation for more information.

### Custom Application Shells

In cases where these tools provide a custom shell, the commands
are prefixed with a shell-specific prompt which will usually
be of the form _shell-name_>, for example:

    UETools> help

Subshells (that is, a shell within another shell) are by default
separated by a slash ("/") similar to file paths. For example,
a "Build" subshell within "UETools" would look like this:

    UETools/Build> help --verbose

The library functions for custom shells allow you to change the
prompt format and trailing character, but this documentation
assumes the default unless noted otherwise.

### Command Line Options

Command line arguments and options follow POSIX conventions unless
otherwise noted. Single-letter options are prefixed with a single
hyphen ("-"), while multi-letter options are prefixed with two
hyphens ("--").

[^placeholders]: Unfortunately, Markdown does not seem to have a good way
 to apply markdown inside a code block. This is for the very
 good reason of not "accidentally" picking markout from code
 syntax, but it does mean placeholders are problematic.]
