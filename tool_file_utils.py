import os
import re

def split_upper_camel_case(text: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)

def format_generated_tool_filename(text: str, prefix: str = "generated") -> str:
    text = split_upper_camel_case(text)
    text = text.replace(" ", "_")
    text = text.replace("__", "_")
    text = text.lower()
    return f"{prefix}_{text}.py"

def create_generated_tools_directory(generated_tool_dir: str = "./generated_tools") -> str:
    os.makedirs(generated_tool_dir, exist_ok=True)
    return generated_tool_dir