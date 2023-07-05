#!/bin/bash

#
# Copyright (C) 2023 Joelle Maslak
# All Rights Reserved - See License
#

doit() {
    docker buildx build --push --platform linux/arm/v7,linux/arm64/v8,linux/amd64 --tag jmaslak/format-scan-pdf .
}

doit "$@"


