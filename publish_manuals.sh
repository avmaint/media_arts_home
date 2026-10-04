#!/bin/bash
# Publish the manuals folder to the media arts home server.
# Uses the VPN hostname (uacts-g001) which is always reachable.

set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"

# Stage hand-authored source documents (source_documents/) into manuals/ first.
# PDFs already live in manuals/; this only adds/updates the generated HTML refs.
"$APP_DIR/assemble_documents.sh"

SRC="/Users/donert/Documents/UACTech/SystemDocumentation/github/media_arts_home/manuals/"
DEST="avuser@uacts-g001:/Users/avuser/media_arts_home/manuals/"

echo "Publishing manuals to $DEST ..."
rsync -avz --delete "$SRC" "$DEST"
echo "Done."
