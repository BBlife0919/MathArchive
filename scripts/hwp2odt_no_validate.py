#!/usr/bin/env python3
"""HWP -> ODT converter that skips RelaxNG validation (workaround for strict validator rejecting valid-enough ODT)."""
import sys
from contextlib import closing
from functools import partial
from hwp5.hwp5odt import ODTTransform, open_odtpkg
from hwp5.xmlmodel import Hwp5File
from hwp5.utils import make_open_dest_file
from hwp5.cli import init_with_environ


def main():
    if len(sys.argv) != 3:
        print("usage: hwp2odt_no_validate.py <input.hwp> <output.odt>", file=sys.stderr)
        sys.exit(2)

    init_with_environ()

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    t = ODTTransform()
    t.relaxng_compile = None
    t.odf_validator = None
    t.embedbin = False

    with closing(Hwp5File(in_path)) as hwp5file:
        with partial(open_odtpkg, out_path)() as dest:
            t.transform_hwp5_to_package(hwp5file, dest)


if __name__ == "__main__":
    main()
