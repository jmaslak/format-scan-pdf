#!/bin/bash

#
# Copyright (C) 2023 Joelle Maslak
# All Rights Reserved - See License
#

doit() {
    docker build -t jmaslak/format-scan-pdf .
}

doit "$@"


