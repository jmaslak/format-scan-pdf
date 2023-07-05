FROM ubuntu

RUN apt-get update && \
    apt-get -y install \
        fpc \
        git \
        graphicsmagick \
        libimage-exiftool-perl \
        mupdf-tools \
        ocrmypdf \
        parallel \
        pdftk \
        poppler-utils \
        python3-prompt-toolkit
        
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN git clone https://github.com/jmaslak/deskew
WORKDIR /usr/src/deskew
RUN git checkout feature/ignore-blank-page
RUN Scripts/compile.sh

RUN ln -s /usr/src/deskew/Bin/deskew /usr/local/bin/.
COPY format-scan-pdf.py /usr/local/bin/format-scan-pdf.py

RUN mkdir -p /usr/pdf
WORKDIR /usr/pdf

ENTRYPOINT ["/usr/local/bin/format-scan-pdf.py"]
CMD ["-h"]

