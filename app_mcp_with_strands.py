import asyncio
import copy
import glob
import json
import os, logging
import time
from contextlib import ExitStack
from pathlib import Path
from typing import cast, get_args

import boto3
import nest_asyncio
import streamlit as st
import yaml
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.models.openai import OpenAIModel

from strands.tools.mcp import MCPClient
from strands.tools.mcp.mcp_agent_tool import MCPAgentTool
from strands.types.content import ContentBlock, Message, Messages
from strands.types.media import ImageFormat
from strands_tools import current_time, http_request

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

nest_asyncio.apply()

# Enables Strands debug log level
logging.getLogger("strands").setLevel(logging.INFO)

# Sets the logging format and streams logs to stderr
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

os.environ["DEV"] = "true"

format = {"image": list(get_args(ImageFormat))}

builtin_tools = [current_time, http_request]


async def streaming(stream):
    """
    Asynchronous generator function that processes streaming data and generates text or tool usage information.

    Args:
        stream: Streaming response from the agent

    Yields:
        str: Formatted string of text data or tool usage information
    """
    async for event in stream:
        # If the event contains data, output it as text
        if "data" in event:
            # Output text
            data = event["data"]
            yield data
        # If the event contains a message, extract and output tool usage information
        elif "message" in event:
            # Output ToolUse
            message: Message = event["message"]
            # Extract tool usage information from message content
            for content in message["content"]:
                if "toolUse" in content.keys():
                    yield f"\n\n🔧 Using tool:\n```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```\n\n"
                if "toolResult" in content.keys():
                    yield f"\n\n🔧 Tool result:\n```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```\n\n"


async def main():
    """
    Main function for the Streamlit application. Handles chat interface setup,
    model initialization, user input processing, and chat history management.

    Returns:
        None
    """
    st.title("客服分析助手")

    with open("config/config.json", "r") as f:
        config = json.load(f)

    models = config["models"]
    bedrock_region = config["bedrock_region"]

    def select_chat(chat_history_file):
        st.session_state.chat_history_file = chat_history_file
    
    with st.sidebar:
        with st.expander(":gear: config", expanded=True):
            st.selectbox("LLM model", models.keys(), key="model_id")
            st.checkbox("Enable prompt cache", value=True, key="enable_prompt_cache")

            chat_history_dir = st.text_input(
                "chat_history_dir", value=config["chat_history_dir"]
            )

            st.text_input(
                "mcp_config_file",
                value=config["mcp_config_file"],
                key="mcp_config_file",
            )

            with open(st.session_state.mcp_config_file, "r") as f:
                mcp_config = json.load(f)["mcpServers"]

            if "multiselect_mcp_tools" not in st.session_state:
                with st.spinner("Tool loading..."):
                    mcp_tools: list[MCPAgentTool] = []
                    with ExitStack() as stack:
                        for _, server_config in mcp_config.items():
                            server_parameter = StdioServerParameters(
                                command=server_config["command"],
                                args=server_config["args"],
                                env=server_config["env"]
                                if "env" in server_config
                                else None,
                            )
                            mcp_client = MCPClient(
                                lambda param=server_parameter: stdio_client(
                                    server=param
                                )
                            )
                            stack.enter_context(mcp_client)
                            mcp_tools.extend(mcp_client.list_tools_sync())
                    
                    st.session_state.mcp_tools = mcp_tools
                    st.session_state.multiselect_mcp_tools = [
                        tool.tool_name for tool in mcp_tools
                    ]

            st.pills(
                "MCP Tool",
                st.session_state.multiselect_mcp_tools,
                selection_mode="multi",
                default=st.session_state.multiselect_mcp_tools,
                key="selected_mcp_tools",
            )

        st.button(
            "New Chat",
            on_click=select_chat,
            args=(f"{chat_history_dir}/{int(time.time())}.yaml",),
            use_container_width=True,
            type="primary",
        )

    if "chat_history_file" not in st.session_state:
        st.session_state["chat_history_file"] = (
            f"{chat_history_dir}/{int(time.time())}.yaml"
        )
    chat_history_file = st.session_state.chat_history_file

    if Path(chat_history_file).exists():
        with open(chat_history_file, mode="rt") as f:
            yaml_msg = yaml.safe_load(f)
            messages: Messages = yaml_msg
    else:
        messages: Messages = []

    for message in messages:
        for content in message["content"]:
            with st.chat_message(message["role"]):
                if "text" in content:
                    st.write(content["text"])
                elif "image" in content:
                    st.image(content["image"]["source"]["bytes"])

                if "toolUse" in content.keys():
                    st.write(f"\n\n🔧 Using tool:\n```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```\n\n")
                if "toolResult" in content.keys():
                    st.write(f"\n\n🔧 Tool result:\n```json\n{json.dumps(content, indent=2, ensure_ascii=False)}\n```\n\n")


    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.write(prompt)
        # Use ExitStack to manage variable number of clients
        with ExitStack() as stack:
            mcp_tools: list[MCPAgentTool] = []

            for server_name, server_config in mcp_config.items():
                server_parameter = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config["env"] if "env" in server_config else None,
                )
                mcp_client = MCPClient(
                    lambda param=server_parameter: stdio_client(server=param)
                )
                stack.enter_context(mcp_client)  # type: ignore
                mcp_tools.extend(mcp_client.list_tools_sync())

            the_mcp_tools = [
                tool
                for tool in mcp_tools
                if tool.tool_name in st.session_state.selected_mcp_tools
            ]

            from tidb_strands_agent import universal_search
            tools = [universal_search] + the_mcp_tools + builtin_tools
            
            if st.session_state.model_id == "deepseek-ai/DeepSeek-V3":
                SILICONFLOW_KEY = os.getenv("SILICONFLOW_KEY")
                the_model = OpenAIModel(
                    client_args = {
                        "api_key": SILICONFLOW_KEY,
                        "base_url": "https://api.siliconflow.cn/v1"
                    },
                    model_id = "deepseek-ai/DeepSeek-V3",
                )
                print('Using DeepSeek-V3 model')
            else:
                the_model = BedrockModel(
                    model_id=st.session_state.model_id,
                    boto_session=boto3.Session(region_name="us-east-1")
                )
            
            agent = Agent(
                model=the_model,
                system_prompt="""你是一个客服助手！
                如果需要回答客服、订单、商品等数据相关问题，可以查询TiDB来回答。
                查询TiDB中的数据时，对于vector类型的记录，不需要在结果中返回该字段，而且可以针对有vector类型字段的表进行语义搜索。
                """,
                messages=messages,
                callback_handler=None,
                tools=tools,
            )

            agent_stream = agent.stream_async(prompt)

            with st.chat_message("assistant"):
                st.write_stream(streaming(agent_stream))

            with open(chat_history_file, mode="wt") as f:
                yaml.safe_dump(agent.messages, f, allow_unicode=True)

    with st.sidebar:
        history_files = glob.glob(os.path.join(chat_history_dir, "*.yaml"))  # type: ignore

        for h in sorted(history_files, reverse=True)[:20]:  # latest 20
            st.button(h, on_click=select_chat, args=(h,), use_container_width=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
