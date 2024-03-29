#!/bin/bash

#
# Copyright (C) 2023-2024 Joelle Maslak
# All Rights Reserved - See License
#

VERSION=v1.4.2

doit() {
    if [ "$SKIP_VERSION_CHECK" == "" ] ; then
        if grep -E "^$VERSION\$" .version >/dev/null ; then
            echo "You must update the version number in this script!" >&2
            exit 1
        fi
        if [ -f .version ] ; then
            if grep -E "^$VERSION\$" .version >/dev/null ; then
                echo "You must update the version number in this script!" >&2
                exit 1
            fi
        fi
        if grep -E "^\# $VERSION\s" Changes.md >/dev/null ; then
            # We are good!
            echo "Changelog is updated!"
        else
            echo "You must add a changelog entry!" >&2
            exit 1
        fi
    fi
    echo $VERSION >>.version
    git add .version
    git commit -a || exit 2
    git tag $VERSION
    git push

    docker buildx build --push --platform linux/arm/v7,linux/arm64/v8,linux/amd64 \
        --tag jmaslak/format-scan-pdf:latest \
        --tag jmaslak/format-scan-pdf:$VERSION \
        .
}

doit "$@"


