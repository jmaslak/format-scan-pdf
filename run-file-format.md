# .run file format

To bypass the command options, you can use a .run file (passed via
the --runfile option).

It contains the following options:

 * `remove_metadata` (yes / no) - Whether or not metadata should be
   removed
 * `rotate` (none, clockwise, anticlockwise, 180) - How to rotate pages in
   the document
 * `crop` (integer percent and either left, right, or center, I.E. "100
   center" is not to trim, "90 left" is to trim the right 10%.
 * `split` (no, all, skipfirst, skiplast, skipfirstlast) - Pages to
   vertically (after rotation) split into two pages
 * `remove_pages` (none, first, last, firstlast) - What pages to remove
   from the document
 * `deskew` (no, standard, standardskipfirst, 100, 100skipfirst, 200,
   200skipfirst) - How to deskew (standard means from margin to margin,
   while 100 means only the center 100 pixels are considered, likewise
   for 200; The skipfirst says to skip deskewing the first page)
 * `ocr` (yes / no) - Whether or not to add an OCR layer

The file is space deliminated.

# Example:

```
remove_metadata no
rotate none
crop 100center
split no
remove_pages none
deskew standard
ocr yes
```
