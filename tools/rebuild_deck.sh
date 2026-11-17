#!/bin/sh
# usage: tools/rebuild_deck.sh LIVE_DIR BUILD_DIR     (LIVE_DIR/project = a fresh read of the artifact)
set -e
LIVE=$1; BUILD=$2
rm -rf "$BUILD/project"; mkdir -p "$BUILD/project/slides"
cp "$LIVE/project/deck.json" "$BUILD/project/"
cp "$LIVE/project/slides/"*.html "$BUILD/project/slides/"
PY=/Users/sclaus/miniforge3/envs/fenicsx0.11/bin/python
$PY tools/ps_build.py "$BUILD/project/slides" >/dev/null
$PY tools/lecture_restructure.py "$BUILD"
