# LGSCO POC Scripts

This directory contains scripts for managing and exporting case documents from an Azure AI Search index. Since direct integration is not yet available, this uses Microsoft's recommended way to extract search index data to use as source for a different indexing process.

## Files

- `config.sh`: Configuration file containing endpoint, admin key, and index name. See `config.sh.example`
- `case-export.sh`: Script to export case documents from the Azure AI Search index to local storage.
- `prepare-case-data.py`: Script to clean and prepare case data from the output above, before uploading to Azure Blob Storage.

## Usage

1. **Configuration**:
   - Create a `config.sh` file with the appropriate values for your Azure AI Search service.

2. **Export Case Documents**:
   - Run `case-export.sh` to export case documents from the Azure AI Search index to the local `data/export_from_index` directory.

```bash
./case-export.sh
```

3. **Prepare Case Data**:
   - Run `prepare-case-data.py` to ensure data is in the right format for consumption. The output will be in the `data/processed-case-files` directory.

```bash
python3 prepare-case-data.py
```

4. **Upload to Azure Blob Storage**:
   - Upload the processed case files to Azure Blob Storage. You can use Azure CLI or any other preferred method to upload the files.

```bash
az storage blob upload-batch -d <your-container-name> -s data/processed-case-files --account-name <your-storage-account-name>
```

5. **Process Using Azure OpenAI**:
   - Once the data is uploaded, a function will automatically pick up each case document, process it using Azure OpenAI, and output **events** to blob storage. For more details, refer to the [lgsco-event-extraction repository](https://github.com/xSolutions365/lgsco-event-extraction).

## Output

- The exported indexed documents will be available in the `data/export_from_index` directory.
- The processed case files will be available in the `data/processed-case-files` directory.
- The final processed events will be available in Azure Blob Storage.

## Notes

- Ensure that the `config.sh` file is properly configured before running the export script.
- The `azureblob-index-partitions.json` file is generated during the export process and contains partition information for the index.
- The `.gitignore` file is used to exclude the `data` directory and `config.sh` from version control.
