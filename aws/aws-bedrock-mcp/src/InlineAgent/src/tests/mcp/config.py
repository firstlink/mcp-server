from dotenv import load_dotenv
import os
from pathlib import Path

from mcp import StdioServerParameters

from InlineAgent import AgentAppConfig

config = AgentAppConfig()

print(str(Path.home()))

cost_server_params = StdioServerParameters(
    command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "-e", "AWS_ACCESS_KEY_ID",
        "-e", "AWS_SECRET_ACCESS_KEY", 
        # "-e", "AWS_DEFAULT_REGION",
        "-e", "AWS_REGION", 
        "-v", f"{str(Path.home())}/.aws:/root/.aws:ro",
        "acuvity/mcp-server-aws-cost-explorer:latest",
    ],
    env={
        "AWS_PROFILE": "mcp-server",
        "AWS_ACCESS_KEY_ID": "REMOVED_AWS_ACCESS_KEY",
        "AWS_SECRET_ACCESS_KEY": "REMOVED_AWS_SECRET_KEY",
        "AWS_REGION": "us-east-1",
        # "BEDROCK_LOG_GROUP_NAME": config.BEDROCK_LOG_GROUP_NAME,
    },
)

perplexity_server_params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "-e", "PERPLEXITY_API_KEY", "mcp/perplexity-ask"],
    env={"PERPLEXITY_API_KEY": "REMOVED_PERPLEXITY_API_KEY"},
)