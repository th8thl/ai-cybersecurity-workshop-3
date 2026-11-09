"""Direct MCP retrieval with the same hidden-token pattern as Session 2."""
import asyncio
from getpass import getpass
import json
import os
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','support_portal.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from chatbot.mcp_client import discover,call,environment,connection
from security.mcp_authorization import use_access_token
from mcp import ClientSession,StdioServerParameters

async def forged_actor(token):
    params=StdioServerParameters(command=sys.executable,args=[str(root/'mcp_server/server.py')],env=environment(token))
    async with connection(params) as (reader,writer):
        async with ClientSession(reader,writer) as session:
            await session.initialize()
            response=await session.call_tool('search_knowledge',{'question':'billing','user_id':999})
            if not response.isError:raise RuntimeError('Forged user_id was unexpectedly accepted.')
            print('Caller-supplied user_id rejected by MCP schema.')

if __name__=='__main__':
    user=get_user_model().objects.get(username=input('Signed-in account name (alice or bob): ').strip())
    token=getpass('Paste this account’s knowledge-authorized token (hidden): ')
    with use_access_token(token):
        manifest=discover(user)
        print('Discovered tools:',[t['name'] for t in manifest['tools']])
        result=call(user,'search_knowledge',{'question':'billing statement','method':'keyword'})
        print(json.dumps(result,indent=2))
    asyncio.run(forged_actor(token))
