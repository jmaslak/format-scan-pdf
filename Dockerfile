FROM ubuntu

RUN apt-get update && \
    apt-get -y install \
        git \
        graphicsmagick \
        libimage-exiftool-perl \
        mupdf-tools \
        ocrmypdf \
        parallel \
        pdftk \
        poppler-utils \
        python3-prompt-toolkit \
        qpdf
        
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN git clone https://github.com/jmaslak/deskew
WORKDIR /usr/src/deskew
RUN git checkout feature/ignore-blank-page
RUN apt-get -y install fpc && Scripts/compile.sh \
    && apt-get -y remove fpc git && apt-get -y autoremove

RUN ln -s /usr/src/deskew/Bin/deskew /usr/local/bin/.
COPY format-scan-pdf.py /usr/local/bin/format-scan-pdf.py

RUN mkdir -p /usr/pdf
WORKDIR /usr/pdf

ENTRYPOINT ["/usr/local/bin/format-scan-pdf.py"]
CMD ["-h"]

