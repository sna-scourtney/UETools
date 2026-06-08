# UETools
Python tools for automating Unreal Engine workflows

These are tools I've created for my own use in Unreal Engine projects on Linux. While I do
try to avoid platform-specific code, these scripts are not currently tested on non-Linux
hosts. The code is shared as a starting point to make tools for your own needs and is not
intended as a finished, releasable product.

Refer to the [documentation section](./docs/) for information about
[notational conventions](./docs/Notation.md) and setting up a [development
environment](./docs/Development.md).

## Status Notice

**This code is at proof-of-concept status** and is not yet complete. The repository is being
made public to meet a commitment I made in a conference presentation, but "life happened" this
week and I haven't got the new code pushed yet. It's coming Real Soon Now, but you probably
don't want to clone this repo as it stands right now.

## Acknowledgments

Author: Scott Courtney, Sine Nomine Associates

The author gratefully acknowledges [Sine Nomine Associates](https://www.sinenomine.net)
for allowing a blend of custom work for the company with open source work I have done
on my own. It is wonderful to work for a company that strives to be
"good citizens" in the open source community.

## Disclaimer

Notwithstanding the preceding acknowledgment, this code is a personal
work product of the author and is not warranted or supported by Sine Nomine
Associates or its management. Opinions expressed in the documentation are
those of the author and not those of Sine Nomine Associates. Refer to the
[LICENSE](LICENSE) for legal terms of use.

## Contributing

Pull requests are welcome under the terms of the BSD 3-Clause Clear license (see
[LICENSE](LICENSE) for details). Acceptance of PRs depends on a variety of factors
including whether or not they are in keeping with my own plans for the code. If your PR
is not accepted, or is modified for acceptance, it's not personal.

This code is very much a work-in-progress (WIP). In particular, the code in this GitHub
repository is a subset of a larger Python tools framework that I am creating.
The framework will be released as open source under the same license as this
repository when it is ready. When that occurs, the UETools will be refactored to remove
functions provided by the enclosing framework.
