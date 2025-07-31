#!/usr/bin/env python3
"""
Script to swap value and description fields in existing configurations.
This script will update all configurations in the database to match the new format
where the longer text is in the value field and the shorter label is in the description field.
"""
import asyncio
import os
import sys
from uuid import UUID

import httpx
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ConfigurationUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


async def get_all_configurations() -> List[Dict[str, Any]]:
    """Get all configurations from the database"""
    user_svc_url = os.getenv("USER_SVC_URL", "http://localhost:8002")
    config_api_url = f"{user_svc_url}/api/v1/configurations"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(config_api_url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error getting configurations: {e}")
        return []


async def update_configuration(configuration_id: UUID, update_data: ConfigurationUpdate) -> bool:
    """Update a configuration in the database"""
    user_svc_url = os.getenv("USER_SVC_URL", "http://localhost:8002")
    config_api_url = f"{user_svc_url}/api/v1/configurations/{configuration_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                config_api_url, 
                json=update_data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error updating configuration {configuration_id}: {e}")
        return False


async def swap_value_and_description():
    """Swap value and description fields for all configurations"""
    configs = await get_all_configurations()
    
    if not configs:
        print("No configurations found or error getting configurations")
        return
    
    print(f"Found {len(configs)} configurations to update")
    
    # Default configurations we want to update
    default_keys = ["blocked_message", "blocked_sim", "payment_message", "payment_reminder"]
    
    success_count = 0
    for config in configs:
        config_id = config.get("configuration_id")
        key = config.get("key")
        
        if key not in default_keys:
            print(f"Skipping non-default configuration: {key}")
            continue
            
        value = config.get("value")
        description = config.get("description")
        
        # Check if value is shorter than description (indicating old format)
        if value and description and len(value) < len(description):
            print(f"Updating configuration: {key} (ID: {config_id})")
            
            # Create update with swapped fields
            update_data = ConfigurationUpdate(
                value=description,
                description=value
            )
            
            # Update the configuration
            success = await update_configuration(config_id, update_data)
            if success:
                success_count += 1
                print(f"Successfully updated {key}")
            else:
                print(f"Failed to update {key}")
        else:
            print(f"Configuration {key} already has correct format or is empty")
    
    print(f"Updated {success_count} configurations")


if __name__ == "__main__":
    asyncio.run(swap_value_and_description())
