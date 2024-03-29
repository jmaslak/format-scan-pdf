# v1.4.2 - January 14, 2024 (Joelle Maslak)

 * Adjust deskew angle to 20 degrees max (rather than 10)

# v1.4.1 - January 14, 2024 (Joelle Maslak)

 * Correcting some build issues

# v1.4.0 - January 14, 2024 (Joelle Maslak)

 * Support run files (for batch mode)
 * Allow re-OCRing of already OCRed docs when no other changes are made.

# v1.3.0 - December 15, 2023 (Joelle Maslak)

 * Change default of deskew (and other image conversion) from 72 dpi to
   300 dpi

# v1.2.0 - August 26, 2023 (Joelle Maslak)

 * Provide options to not deskew first page (useful when the first page
   is cover art or similar)
 * Fix deskewing bug when deskewing is used with OCR

# v1.1.1 - July 19, 2023 (Joelle Maslak)

 * Shrink image size substantially
 * Don't crash if qpdf --linearize warns

# v1.1.0 - July 19, 2023 (Joelle Maslak)

 * Allow trimming of either left or right (or both) margins

# v1.0.1 - July 17, 2023 (Joelle Maslak)

 * Now linearizing PDFs to avoid history of updated tags (those could
   expose what tool was used to redact it). Note that no original
   metadata was exposed.

# v1.0.0 - July 17, 2023 (Joelle Maslak)

 * Added redaction capabilities

# v0.1.0 - July 8, 2023 (Joelle Maslak)

 * Provided a routine to crop off the rightmost 10% or 20% of the PDF
 * Used white instead of black for background in deskew
