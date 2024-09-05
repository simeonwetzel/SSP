import asyncio
import aiohttp
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain.tools import tool

class SpatialEntity(BaseModel):
    original_query: str = Field(description="Get original query as prompted by the user")
    spatial: str = Field(description="Get the spatial entity. Can be a location or place or a region")
    scale: str = Field(description="Get the spatial scale")

class AnswerSchema(BaseModel):
    result: str = Field(description="JSON representation of the paresed spatial entity")

class SSP:
    def __init__(self, llm):
        # Set up a parser and inject instructions into the prompt template.
        self.spatial_context_prompt_parser = JsonOutputParser(pydantic_object=SpatialEntity)
        self.spatial_context_prompt = PromptTemplate(
            template="""
            You are an expert in geography and spatial data. 
            Your task is to extract from a query spatial entities such as city, country or region names.
            Also determine the spatial scale ("Local", "City", "Regional", "National", "Continental", "Global") from the given query.

            Output:{format_instructions}\n{query}\n""",
            input_variables=["query"],
            partial_variables={"format_instructions": self.spatial_context_prompt_parser.get_format_instructions()},
        )

        self.osm_picker_prompt_parser = JsonOutputParser(pydantic_object=AnswerSchema)
        self.osm_picker_prompt = PromptTemplate(
            template="""
            You are an expert in geography and spatial data. 
            Your task is to pick from the results list the best matching candidate according to the query.
            If the original query includes a country information, consider this in your selection.
            If also consider the type. E.g. if user asks for a 'river' also pick the corresponding result.

            **Simply output the result in JSON format without further explanations**

            Also consider the scale: {scale}
            Query: {original_query}
            Results: {results}
            Output:""",
            input_variables=["original_query", "scale", "results"]
        )

        # LLM instance for executing queries
        self.llm = llm

    async def query_osm_async(self, query_dict: dict):
        nominatim_url = "https://photon.komoot.io/api"
        query = query_dict['spatial']
        params = {"q": query,
              "limit": 5}
        url = f"{nominatim_url}?q={params['q']}&limit={params['limit']}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    results = await response.json()
                    simplified_results = [
                        {
                            "name": res["properties"].get("name"),
                            "country": f"{res['properties'].get('country')}",
                            "type": res["properties"].get("type"),
                            "extent": res["properties"].get("extent")
                        }
                        for res in results.get("features", [])
                    ]
                    return {"results": simplified_results}
                else:
                    return {"error": "Failed to query Nominatim"}

    def search_with_osm_query(self, query_dict: dict):
        """
        Use query and search in OSM
        """
        # query_dict = {'spatial': spatial, 'scale': scale}
        results = asyncio.run(self.query_osm_async(query_dict))
        return {"original_query": query_dict.get("original_query"), 
                "scale": query_dict.get("scale"), 
                "results": results}

    def parse_spatial_scope(self, user_query: str):
        # Create the spatial context chain
        spatial_context_chain = (
            self.spatial_context_prompt
            | self.llm
            | self.spatial_context_prompt_parser
            | self.search_with_osm_query
            | self.osm_picker_prompt
            | self.llm
            | self.osm_picker_prompt_parser
        )

        # Invoke the chain with the user query
        response = spatial_context_chain.invoke({"query": user_query})
        return response
