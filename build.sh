#!/bin/bash

#
# Copyright (C) 2023 Joelle Maslak
# All Rights Reserved - See License
#

doit() {
    docker build -t format-scan-pdf .
}

doit "$@"


