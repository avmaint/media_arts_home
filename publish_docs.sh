#!/bin/bash
# Publish the Quarto _output folder to the media arts home server.
# Uses the VPN hostname (uacts-g001) which is always reachable.

set -e

SRC="/Users/donert/Documents/UACTech/SystemDocumentation/github/uactechdoc/_output/"
DEST="avuser@uacts-g001:/Users/avuser/media_arts_home/docs/"

echo "Publishing docs to $DEST ..."
rsync -avz --delete "$SRC" "$DEST"
echo "Done."
