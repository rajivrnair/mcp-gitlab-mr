import asyncio
from fastmcp import Client

client = Client("gitlab_mr.py")

async def test_list_mr():
    async with client:
        print("Testing list_mr() with default parameters...")
        result = await client.call_tool("list_mr", {})
        print("Result:", result)
        print()
        
        print("Testing list_mr() with state='all' and filter_by='created_by_me'...")
        result = await client.call_tool("list_mr", {
            "state": "all", 
            "filter_by": "created_by_me"
        })
        print("Result:", result)
        print()
        
        print("Testing list_mr() with state='opened' and filter_by='assigned_to_me'...")
        result = await client.call_tool("list_mr", {
            "state": "opened", 
            "filter_by": "assigned_to_me"
        })
        print("Result:", result)

asyncio.run(test_list_mr())