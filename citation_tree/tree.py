import requests
from typing import Any
from loguru import logger
# Define the paper search endpoint URL

api_key = "HobCCUlhe84IQ95Pa5z0a4sZ3yfTDQDlZVi9i5Qi"


def search_paper(query: str, api_url: str, api_key: str) -> dict[str, Any] | None:
    query_params = {"query": query, "limit": 1, "fields": "title,year,paperId"}
    response = requests.get(api_url, params=query_params)

    if response.status_code == 200:
        return response.json()["data"][0]
    else:
        msg = (
            f"Search failed: {response.status_code}: {response.text}" f"Query: {query}"
        )
        logger.error(msg)
        return None


def get_paper_data(paper_id: str, api_url: str, api_key: str) -> dict[str, Any] | None:
    url = api_url + paper_id
    paper_data_query_params = {"fields": "title,year,abstract,authors.name"}

    response = requests.get(url, params=paper_data_query_params)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            f"Paper Details Request failed with status code {response.status_code}: {response.text}"
        )
        return None


def get_paper_citations(
    paper_id: str, api_url: str, api_key: str
) -> dict[str, Any] | None:
    headers = {"x-api-key": api_key}
    url = f"{api_url}/{paper_id}/citations"

    response = requests.get(
        url,
        headers=headers,
        params={"fields": "title,year", "limit": 10},
    )

    if response.status_code == 200:
        return response.json()["data"]
    else:
        logger.error(
            f"Paper Citations Request failed with status code {response.status_code}: {response.text}"
        )
        return None


query_params = {"query": "OneFormer", "limit": 3}
api_url = "https://api.semanticscholar.org/graph/v1"
paper_url = f"{api_url}/paper"
search_url = f"{paper_url}/search"

search_response = search_paper("OneFormer", search_url, api_key)

if search_response is not None:
    paper_id = search_response["paperId"]

    paper_citations = get_paper_citations(paper_id, paper_url, api_key)
else:
    # Handle potential errors or non-200 responses
    print(
        f"Relevance Search Request failed with status code {search_response.status_code}: {search_response.text}"
    )
