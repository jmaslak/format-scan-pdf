#!/bin/bash

#
# Copyright (C) 2023 Joelle Maslak
# All Rights Reserved - See License
#

doit() {
    docker pull jmaslak/format-scan-pdf:latest
}

doit "$@"


