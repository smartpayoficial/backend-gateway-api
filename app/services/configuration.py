import os
from typing import List, Optional
from uuid import UUID

import httpx

from app.models.configuration import (
    ConfigurationCreate,
    ConfigurationDB,
    ConfigurationUpdate,
)

USER_SVC_URL = os.getenv("USER_SVC_URL", "http://localhost:8002")
CONFIGURATION_API_URL = f"{USER_SVC_URL}/api/v1/configurations"


async def create_configuration(
    config_in: ConfigurationCreate,
) -> Optional[ConfigurationDB]:
    """
    Create a new configuration in the database
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CONFIGURATION_API_URL, json=config_in.model_dump(mode="json")
        )
        if response.status_code == 201:
            return ConfigurationDB(**response.json())
        return None


async def get_configurations(key: Optional[str] = None) -> List[ConfigurationDB]:
    """
    Get all configurations from the database
    If key is provided, filter configurations by key (partial match)
    """
    params = {}
    if key:
        params["key"] = key

    async with httpx.AsyncClient() as client:
        response = await client.get(CONFIGURATION_API_URL, params=params)
        response.raise_for_status()
        return [ConfigurationDB(**item) for item in response.json()]


async def get_configuration(configuration_id: UUID) -> Optional[ConfigurationDB]:
    """
    Get a specific configuration by ID
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONFIGURATION_API_URL}/{configuration_id}")
        if response.status_code == 200:
            return ConfigurationDB(**response.json())
        return None


async def update_configuration(
    configuration_id: UUID, config_update: ConfigurationUpdate
) -> Optional[ConfigurationDB]:
    """
    Update a configuration by ID
    """
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{CONFIGURATION_API_URL}/{configuration_id}",
            json=config_update.model_dump(exclude_unset=True, mode="json"),
        )
        # Handle both 200 (with content) and 204 (no content) as success
        if response.status_code == 200:
            return ConfigurationDB(**response.json())
        elif response.status_code == 204:
            # For 204 No Content, we need to fetch the updated configuration
            return await get_configuration(configuration_id)
        return None


async def delete_configuration(configuration_id: UUID) -> bool:
    """
    Delete a configuration by ID
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{CONFIGURATION_API_URL}/{configuration_id}")
        return response.status_code == 204
