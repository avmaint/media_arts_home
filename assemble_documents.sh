#!/bin/bash
# Assemble hand-authored source documents into the manuals/ serving tree.
#
# Source of truth is source_documents/<category>/...  (tracked in git).
# This copies it into manuals/<category>/...  (gitignored build artifacts) so
# the Flask app serves them and publish_manuals.sh rsyncs them to production
# alongside the separately-managed vendor PDFs.
#
# Merge only -- no --delete -- so it never touches the PDFs already in manuals/.
set -e
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
rsync -a "$APP_DIR/source_documents/" "$APP_DIR/manuals/"
echo "Assembled source_documents/ into manuals/."
