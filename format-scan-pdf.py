#!/usr/bin/env python3

#
# Copyright (C) 2023 Joelle Maslak
# All Rights Reserved - See License
#

# USAGE: format-scan-pdf.py <source.pdf> <destination.pdf>

#
# DEPENDENCIES (all must be in your PATH):
#
#   deskew -> Available via https://galfar.vevb.net/wp/projects/deskew/
#   exiftool -> Available on Ubuntu in the libimage-exiftool-perl package
#   gm --> Available on Ubuntu in the graphicsmagick package
#   mutool --> Available on Ubuntu in the mupdf-tools package
#   ocrmypdf --> Available on Ubuntu in the ocrmypdf package
#   parallel --> Available on Ubuntu in the parallel package
#   pdftk --> Available on Ubuntu in the pdftk package
#   pdftoppm --> Available on Ubuntu in the poppler-utils package
#   prompt_toolkit --> Available on Ubuntu in the python3-prompt-toolkit package
#   qpdf - Available on Ubuntu in the qpdf package
#

import argparse
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

from prompt_toolkit.shortcuts import radiolist_dialog, yes_no_dialog


def parse_arguments():
    """Get arguments from command line."""
    parser = argparse.ArgumentParser(description="Make scanned PDFs more usable")
    parser.add_argument('infile', help="Input filename")
    parser.add_argument('outfile', help="Output filename")

    args = parser.parse_args()
    return args


def rotate(fn_in, fn_out):
    """Prompt user for rotation info and rotate document."""
    choice = radiolist_dialog(
        title="File Rotation",
        text="Indicate how the document should be rotated",
        values=[
            ("None", "None"),
            ("1-endeast", "Clockwise"),
            ("1-endwest", "Anti-Clockwise"),
            ("1-endsouth", "180 Degrees"),
        ],
    ).run()

    if choice is None:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "None":
        shutil.copy(fn_in, fn_out)
    else:
        subprocess.check_call(["pdftk", fn_in, "cat", choice, "output", fn_out])


def split_pages(fn_in, fn_out, tmpdir):
    """Split pages in scan."""
    choice = radiolist_dialog(
        title="Page Split",
        text="Do you want to split each input page into two output pages?",
        values=[
            ("no", "No"),
            ("all", "Split all pages"),
            ("skipfirst", "Split all but FIRST page"),
            ("skiplast", "Split all but LAST page"),
            ("skipfirstlast", "Split all but FIRST and LAST page"),
        ],
    ).run()

    if not choice:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "no":
        shutil.copy(fn_in, fn_out)
    elif choice == "all":
        subprocess.check_call(["mutool", "poster", "-x", "2", fn_in, fn_out])
    elif choice == "skipfirst":
        fn_first = os.path.join(tmpdir, "work-first.pdf")
        fn_middle = os.path.join(tmpdir, "work-middle.pdf")
        fn_split = os.path.join(tmpdir, "work-split.pdf")
        subprocess.check_call(["pdftk", fn_in, "cat", "1", "output", fn_first])
        subprocess.check_call(["pdftk", fn_in, "cat", "2-end", "output", fn_middle])
        subprocess.check_call(["mutool", "poster", "-x", "2", fn_middle, fn_split])
        subprocess.check_call(["pdftk", fn_first, fn_split, "cat", "output", fn_out])
    elif choice == "skiplast":
        fn_middle = os.path.join(tmpdir, "work-middle.pdf")
        fn_last = os.path.join(tmpdir, "work-last.pdf")
        fn_split = os.path.join(tmpdir, "work-split.pdf")
        subprocess.check_call(["pdftk", fn_in, "cat", "1-r2", "output", fn_middle])
        subprocess.check_call(["pdftk", fn_in, "cat", "r1", "output", fn_last])
        subprocess.check_call(["mutool", "poster", "-x", "2", fn_middle, fn_split])
        subprocess.check_call(["pdftk", fn_split, fn_last, "cat", "output", fn_out])
    elif choice == "skipfirstlast":
        fn_first = os.path.join(tmpdir, "work-first.pdf")
        fn_middle = os.path.join(tmpdir, "work-middle.pdf")
        fn_last = os.path.join(tmpdir, "work-last.pdf")
        fn_split = os.path.join(tmpdir, "work-split.pdf")
        subprocess.check_call(["pdftk", fn_in, "cat", "1", "output", fn_first])
        subprocess.check_call(["pdftk", fn_in, "cat", "2-r2", "output", fn_middle])
        subprocess.check_call(["pdftk", fn_in, "cat", "r1", "output", fn_last])
        subprocess.check_call(["mutool", "poster", "-x", "2", fn_middle, fn_split])
        subprocess.check_call(["pdftk", fn_first, fn_split, fn_last, "cat", "output", fn_out])


def remove_pages(fn_in, fn_out):
    """Remove pages in scan."""
    choice = radiolist_dialog(
        title="Remove Pages",
        text="Indicate which pages should be removed from the output",
        values=[
            ("None", "None"),
            ("2-end", "First Page"),
            ("1-r2", "Last Page"),
            ("2-r2", "First and Last Page"),
        ],
    ).run()

    if not choice:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "None":
        shutil.copy(fn_in, fn_out)
    else:
        subprocess.check_call(["pdftk", fn_in, "cat", choice, "output", fn_out])


def crop(fn_in, fn_out, tmpdir):
    """Prompt user to remove some right margin."""
    choice = radiolist_dialog(
        title="Remove Right Margin",
        text="Do you want to remove some right margin from the document?\n" +
             "(note this causes loss of everything but the image of te PDF)",
        values=[
            ("no", "No"),
            ("10", "Remove right 10%"),
            ("20", "Remove right 20%"),
        ],
    ).run()

    if choice is None:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "no":
        shutil.copy(fn_in, fn_out)
    else:
        base = os.path.join(tmpdir, "images")
        subprocess.check_call([f"pdftoppm -cropbox -jpeg {fn_in} {base}"], shell=True)
        if choice == "10":
            keep = "90"
        else:
            keep = "80"
        subprocess.check_call(["parallel gm convert {} -crop " + keep + "%x100% {}.new.jpg ::: " +
                               f"{base}-*[0-9].jpg"], shell=True)
        subprocess.check_call([f"gm convert {base}-*.new.jpg {fn_out}"], shell=True)


def deskew(fn_in, fn_out, tmpdir):
    """Prompt user to determine if they want deskewing and, if so, deskew it."""
    choice = radiolist_dialog(
        title="Deskew",
        text="Do you want to deskew the document?\n" +
             "(note this causes loss of everything but the image of te PDF)",
        values=[
            ("no", "No"),
            ("standard", "Standard Deskew"),
            ("100", "100 Pixel Margin Deskew"),
            ("200", "200 Pixel Margin Deskew"),
        ],
    ).run()

    if choice is None:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "no":
        shutil.copy(fn_in, fn_out)
    else:
        base = os.path.join(tmpdir, "images")
        subprocess.check_call([f"pdftoppm -cropbox -jpeg {fn_in} {base}"], shell=True)
        if choice == "standard":
            subprocess.check_call(["parallel deskew -b ffffff -m 100 -o {}.new.jpg {} ::: " +
                                   f"{base}-*[0-9].jpg"], shell=True)
        else:
            margins = f"{choice},{choice},{choice},{choice}"
            subprocess.check_call(["parallel deskew -b ffffff -m 100 -r " + margins +
                                   " -o {}.new.jpg {} ::: " + f"{base}-*[0-9].jpg"], shell=True)
        subprocess.check_call([f"gm convert {base}-*.new.jpg {fn_out}"], shell=True)


def remove_hidden(fn_in, fn_out, tmpdir):
    """Prompt user to remove hidden layers, metadata, etc."""
    choice = radiolist_dialog(
        title="Deskew",
        text="Do you want to remove/redact everything invisible from this file?\n\nNote:\n" +
             "  - This will remove all text layers (OCR can re-add SOME of that).\n" +
             "  - This functions by converting pages to images and back to PDF.\n" +
             "  - You may still leak some data, such as the use of this tool.\n" +
             "  - If you are doing something sensitive, verify this worked successfully!",
        values=[
            ("no", "No"),
            ("yes", "Yes"),
        ],
    ).run()

    if choice is None:
        print("Exiting without changes.")
        sys.exit()
    elif choice == "no":
        shutil.copy(fn_in, fn_out)
        return False
    else:
        base = os.path.join(tmpdir, "images")
        subprocess.check_call([f"pdftoppm -cropbox -jpeg {fn_in} {base}"], shell=True)
        subprocess.check_call([f"gm convert {base}-*.jpg {fn_out}"], shell=True)
        return True


def ocr(fn_in, fn_out):
    """Prompt user to determine if they want OCR and, if so, OCR it."""
    choice = yes_no_dialog(
        title="OCR",
        text="Perform Optical Character Recognition?",
    ).run()

    if not choice:
        shutil.copy(fn_in, fn_out)
    else:
        subprocess.check_call(["ocrmypdf", "-d", fn_in, fn_out])


def restore_metadata(fn_in, fn_out):
    """Reset metadata in PDF file."""
    author = subprocess.check_output(["exiftool", fn_in, "-Author", "-s"]).decode()
    publisher = subprocess.check_output(["exiftool", fn_in, "-Publisher", "-s"]).decode()
    title = subprocess.check_output(["exiftool", fn_in, "-Title", "-s"]).decode()

    subprocess.check_call(["exiftool", fn_out, f"-Author={author}", "-overwrite_original"])
    subprocess.check_call(["exiftool", fn_out, f"-Publisher={publisher}", "-overwrite_original"])
    subprocess.check_call(["exiftool", fn_out, f"-Title={title}", "-overwrite_original"])


def remove_metadata(fn_in, fn_out):
    """Remove metadata in PDF file."""
    subprocess.check_call(["exiftool", fn_in, "-all:all=", "-overwrite_original"])
    subprocess.check_call(["qpdf", "--linearize", fn_in, fn_out])


def main():
    """Main application function."""
    args = parse_arguments()

    tmpdir = tempfile.TemporaryDirectory()

    fn_in = args.infile
    fn_tmp1 = os.path.join(tmpdir.name, "work1.pdf")
    fn_tmp2 = os.path.join(tmpdir.name, "work2.pdf")
    fn_out = args.outfile

    shutil.copy(fn_in, fn_tmp1)

    hide_metadata = remove_hidden(fn_tmp1, fn_tmp2, tmpdir.name)
    shutil.copy(fn_tmp2, fn_tmp1)

    rotate(fn_tmp1, fn_tmp2)
    shutil.copy(fn_tmp2, fn_tmp1)

    crop(fn_tmp1, fn_tmp2, tmpdir.name)
    subprocess.check_call(["pdftk", fn_tmp2, "cat", "output", fn_tmp1])

    split_pages(fn_tmp1, fn_tmp2, tmpdir.name)
    shutil.copy(fn_tmp2, fn_tmp1)

    remove_pages(fn_tmp1, fn_tmp2)
    shutil.copy(fn_tmp2, fn_tmp1)

    deskew(fn_tmp1, fn_tmp2, tmpdir.name)
    shutil.copy(fn_tmp2, fn_tmp1)

    ocr(fn_tmp1, fn_tmp2)
    shutil.copy(fn_tmp2, fn_tmp1)

    if hide_metadata:
        remove_metadata(fn_tmp1, fn_out)
    else:
        shutil.copy(fn_tmp1, fn_out)
        restore_metadata(fn_in, fn_out)


if __name__ == "__main__":
    main()
