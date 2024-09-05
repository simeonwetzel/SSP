# Spatial Scope Parser (SSP) 

This tool is designed to extract spatial entities and scales from unstructured text input, using an LLM (Large Language Model) and the Open Source Photon geocoding service provided by [Komoot](https://photon.komoot.io/) that is based on OpenStreetMap (OSM). The tool outputs location names, types, and extents based on the user's query.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ssp-tool.git
   cd ssp-tool
2. Install the required dependencies:
   pip install -r requirements.txt

## How to Connect a LLM

To use this tool, you need to connect any Large Language Model (LLM) compatible with the langchain libary (see a list of available LLMs [here](https://python.langchain.com/v0.2/docs/integrations/chat/)). Below is an example of how to connect an LLM either using the OpenAI or the Groq API.

### OpenAI API Example
```python
import os
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = <YOUR_OPENAI_API_KEY>

# Initialize the LLM
llm = OpenAI(temperature=0)
```

### GROQ API Example
```python
import os 
from langchain_groq import ChatGroq

os.environ["OPENAI_API_KEY"] = <YOUR_KEY_GROQ_API_KEY>

# Initialize the LLM with Groq's Llama3 model
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
```

## Basic Usage

Once you have initialized your LLM, you can use the Spatial Scope Parser (SSP) tool to parse spatial queries from user input.

### Initialize the Parser

```python
from ssp import SSP

# Initialize the SSP tool with your chosen LLM
parser = SSP(llm)
```
### Parsing Spatial Scope
To extract spatial entities and scale from a user query, use the `parse_spatial_scope` method:

```python
user_query = "I need data for Berlin"
response = parser.parse_spatial_scope(user_query)
print(response)
```

### Example Output

```json
{
    "name": "Berlin",
    "country": "Deutschland",
    "type": "city",
    "extent": [13.088345, 52.6755087, 13.7611609, 52.3382448]
}
```

## Adanced Usage
The tool performs two key functions:

1. **Extract Spatial Entity & Scale**: Extract spatial entities such as city, country, or region, and determine the spatial scale (e.g., "Local", "City", "National").
2. **Query OSM for Coordinates**: Once a spatial entity is identified, the tool queries OpenStreetMap (OSM) to find the corresponding geographic details (name, country, type, extent).

### Querying OSM Directly

You can also query OSM directly using the `search_with_osm_query` method if you already know the spatial entity:

```python
query_dict = {'spatial': 'Berlin', 'scale': 'City'}
results = parser.search_with_osm_query(query_dict)
print(results)
```

### Example Outputs

```json
{
    "original_query": "Berlin",
    "scale": "City",
    "results": {
        "name": "Berlin",
        "country": "Deutschland",
        "type": "city",
        "extent": [13.088345, 52.6755087, 13.7611609, 52.3382448]
    }
}
```
## Limitations

One key limitation of this tool is its dependency on the Photon geocoding service provided by [Komoot](https://photon.komoot.io). In our tests, we have observed that most of the latency comes from querying this API. 

While Photon is an open-source service, the performance of the tool may vary based on the availability and response times of the public API. 

### How to Mitigate This Limitation

To have more control over the geocoding service and potentially improve latency, you can host the Photon API on your own resources. Since Photon is open source, you can deploy it locally or on a dedicated server. You can find detailed instructions and the code base in the [Photon GitHub repository](https://github.com/komoot/photon).

By hosting Photon yourself, you can:
- Optimize the server to meet your performance needs.
- Ensure availability and control over the service.
- Adjust the settings to fit your specific geocoding requirements.

## Notes
- The tool uses `aiohttp` for asynchronous API calls to OSM.
- Results are returned in JSON format, allowing easy integration into larger applications.
- The LLM is responsible for understanding the user query, while the OSM API is used for retrieving geographical information.

## Example Use Cases
- **Geospatial Data Applications**: Extract location-based information for mapping and data visualization.
- **Spatial Search**: Use the output of the parser as a search filter when searching for (meta)datasets
- **Natural Language Interfaces**: Use the tool to build chatbots or assistant applications that understand spatial queries.

Feel free to customize the LLM settings and query parsing logic to suit your specific use case.
