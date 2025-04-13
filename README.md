# Document Analysis Tool

## Overview
This tool uses AI to automatically extract structured information from software license and service agreements. It parses contract text and organizes key details into a structured format using Pydantic models and Google's Generative AI.

## Features
- Extracts contract metadata (title, dates, references)
- Identifies parties involved in the agreement
- Extracts software product details (name, version, features)
- Captures service details and SLAs
- Identifies payment milestones and financial terms
- Extracts licensing terms and restrictions
- Identifies deliverables and timelines
- Flags important compliance and risk information

## Requirements
- Python 3.8+
- pydantic
- pydantic-ai
- google-generativeai
- Google API key with access to Gemini models

## Installation

1. Clone this repository or download the source files

2. Install required dependencies:
   ```
   pip install pydantic pydantic-ai google-generativeai
   ```

3. Set up your Google API key as an environment variable:
   ```
   export GOOGLE_API_KEY="your_api_key_here"
   ```

## Usage

### Basic Usage

```python
from simple_contract_analysis_v1 import extract_contract_data_from_text, ContractAnalysisResult

# Your contract text
contract_text = """YOUR CONTRACT TEXT HERE"""

# Extract structured data
result = extract_contract_data_from_text(contract_text)

# Print the result as JSON
if result:
    print(result.model_dump_json(indent=2))
else:
    print("Failed to extract contract info.")
```

### Running the Sample

The script includes a sample contract for testing. To run it:

```
python simple_contract_analysis_v1.py
```

## Data Model Structure

The tool uses a hierarchical Pydantic model structure:

- `ContractAnalysisResult`: The main model containing all extracted information
  - Basic metadata (title, dates, references)
  - Lists of complex nested models:
    - `SoftwareProductDetail`: Information about software products
    - `ServiceDetail`: Information about included services
    - `PaymentMilestoneDetail`: Payment schedule information
    - `PenaltyDetail`: Information about penalties
    - `SLADetail`: Service level agreement details
    - `DeliverableDetail`: Information about deliverables

## Customization

You can customize the extraction by modifying the Pydantic models in the script:

1. Add or remove fields from the `ContractAnalysisResult` class
2. Modify the nested models to capture different information
3. Adjust field descriptions to improve AI extraction accuracy

## Troubleshooting

### API Key Issues

If you see a warning about the API key not being found, make sure you've set the `GOOGLE_API_KEY` environment variable correctly.

### Recursion Errors

The tool specifically catches recursion errors that can occur with complex nested models. If you encounter this error:

1. Try simplifying the model structure by commenting out some of the complex nested fields
2. Reduce the depth of nested models
3. Use simpler field types where possible

### Validation Errors

If the extraction fails with validation errors, the AI might not be correctly identifying all required fields. Consider:

1. Making more fields optional with `Optional[Type]`
2. Providing better field descriptions to guide the AI
3. Simplifying the model structure

## License

This tool is provided for educational and demonstration purposes.
