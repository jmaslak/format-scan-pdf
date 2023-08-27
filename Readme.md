# What this program does

This is a Linux console (terminal) application.

This Docker image is a text mode console application that will, through
menus, allow you to "fix" broken PDF files.  By broken, I mean files
that may have quality issues (but are valid PDFs).  For instance, the
file may need the pages rotated, pages split into two pages (I.E. two
pages of a book scanned into one page of a PDF), first and/or last pages
removed from the PDF, pages "de-skewed" (I.E. text is at an angle that
isn't a proper 90 degrees), and may need OCR (optical character
recognition, to allow copy/highlighting/search) added.

This is intended to be used on scanned images of printed text. Using it
on anything else may give surprising and/or incorrect output.

It also has some basic redaction capability, where it will convert, if
requested, the document to images and back to PDF, and remove many PDF
tags from the output file. This is not industrial-grade redaction, but
should help increase the chance that a PDF only contains what you want
it to contain.

This docker image has many dependencies, see the format-scan-pdf.py file
which lists them.  Normal users will not need to concern themselves with
these dependencies, as they will be part of the image.

# Upgrading Docker Image

```
docker pull jmaslak/format-scan-pdf
```

# Executing

Something along the lines of, without installing anything from this
repo:
```
docker run -it --user $(id -u):$(id -g) -v ~/pdf:/usr/pdf jmaslak/format-scan-pdf in.pdf out.pdf
```

This will download the image from Docker Hub.

The `~/pdf` directory must already exist (you can name it something
else, but whatever it is called, it needs to be passed to the Docker
run command and it will be shared with the Docker image.  Files read and
written will be read and written as your user ID and primary group ID.
This directory will be where your input and output files are written.

If you want to use the standard `~/pdf` directory, you can use the
`format-scan-pdf.sh` script to execute Docker.  Just pass it the
filenames (relative to the `~/pdf` directory) of the input and output
PDF filenames.  It will download the Docker Hub image as needed.

# Prerequisites

You will need Docker installed and working, and your user able to start
Docker images.  Normally, this requires your user in the `docker` group.

# Building

The `build.sh` will create a local docker image based on the included
`Dockerfile`.

Note that the `format-pdf-scan.sh` script will reference
`jmaslak/format-pdf-scan.sh` and thus probably shouldn't be used for
local development!

