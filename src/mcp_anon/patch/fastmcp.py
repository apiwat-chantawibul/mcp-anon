from typing import override

import jsonref
from fastmcp import FastMCP
from fastmcp.utilities.json_schema import compress_schema


def patch_schema(schema):
    return compress_schema(
        jsonref.replace_refs(
            schema,
            proxies = False,
        )
    )


class PatchedFastMCP(FastMCP):

    # Workaround issue where some MCP-client refuses to accept `$ref` in json schema.
    # - [Claude-code used to have the problem.](https://github.com/jlowin/fastmcp/pull/1427)
    # - Gemini-cli have the problem due to [`hasValidTypes` check](https://github.com/google-gemini/gemini-cli/blob/a31830a3cb16584ec0448d6a23da27947ac9e72c/packages/core/src/tools/mcp-client.ts#L576)
    @override
    def tool(self, *args, **kwargs):
        _tool = super().tool(*args, **kwargs)
        _tool.parameters = patch_schema(_tool.parameters)
        _tool.output_schema = patch_schema(_tool.output_schema)
        return _tool

