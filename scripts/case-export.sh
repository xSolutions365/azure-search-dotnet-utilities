# This script exports the case documents from the Case Documents index in Azure AI Search into local storage.

#!/bin/bash

# Source the configuration file
source ./config.sh

# Get the current time in UTC
now=$(date -u +"%Y-%m-%dT%H:%M:%S.0000000+00:00")

# Calculate the start time (5 days ago) using BSD date's -v option
start_time=$(date -u -v -5d +"%Y-%m-%dT%H:%M:%S.0000000+00:00")

# Export the variables
export LOWER_BOUND="$start_time"
export UPPER_BOUND="$now"

# Print the dates
echo "LOWER_BOUND: $LOWER_BOUND"
echo "UPPER_BOUND: $UPPER_BOUND"

# Run partition-index
dotnet run -- partition-index \
  --endpoint "$ENDPOINT" \
  --admin-key "$ADMIN_KEY" \
  --index-name "$CASE_DOCUMENTS_INDEX_NAME" \
  --field-name "metadata_storage_last_modified" \
  --lower-bound "$LOWER_BOUND" \
  --upper-bound "$UPPER_BOUND"

# ***CRITICAL VERIFICATION STEP***
cat azureblob-index-partitions.json

# Check the exit code.  If it's non-zero, there was an error.
if [[ $? -ne 0 ]]; then
  echo "Error: partition-index likely failed.  Check the output above."
  exit 1
fi

# Create the output directory (if it doesn't exist)
mkdir -p ./data/export_from_index
chmod u+w ./data/export_from_index

# Run export-partitions
dotnet run -- export-partitions \
  --partition-path "./azureblob-index-partitions.json" \
  --admin-key "$ADMIN_KEY" \
  --export-path "$(pwd)/data/export_from_index" \
  --include-field "case_id" \
  --include-field "metadata_storage_file_extension" \
  --include-field "metadata_storage_name" \
  --include-field "metadata_storage_path" \
  --include-field "merged_content" \
  --include-field "metadata_storage_last_modified"

echo "Export process completed. Check ./data/export_from_index for output files."