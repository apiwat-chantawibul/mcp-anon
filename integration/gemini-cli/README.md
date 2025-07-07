# Integration with gemini-cli

This guide assumes you have already locally installed:

- [gemini-cli](https://github.com/google-gemini/gemini-cli).
- and [docker engine](https://docs.docker.com/engine/install/)

## Running locally with stdio transport

MCP server can be [added](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md)
to gemini-cli by editing either `~/.gemini/settings.json` in your home directory
or `.gemini/settings.json` where `gemini` command is run.

To get started, there is `integration/gemini-cli/stdio/.gemini/settings.json`
provided which can be used by just changing to the directory where `.gemini` is
and run `gemini`.

```bash
cd integration/gemini-cli/stdio
gemini
```

`gemini-cli` will start with `integration/gemini-cli/stdio` directory as the
context and start `mcp-anon` in docker as a subprocess with the same context
mounted as `./pipeline` and example csv directory mounted as `./target`. You
can then ask gemini to start building anonymization pipeline for
`target/example.csv` like this:

```
Select target/example.csv for anonymization, then lay out the plan to do so.
```

In a completed MCP server implementation, the back-and-forth between user and AI
should eventually result in AI calling tools to create `pipeline.py`.

## Running with HTTP transport

To experiment with HTTP transport, we have to start to `mcp-anon` as a separate
process first.

```bash
cd integration/gemini-cli/http
bash start-mcp-anon-with-http.sh
```

This will show the log of mcp-anon server too.
Then, in a separate terminal, we can run gemini.

```bash
cd integration/gemini-cli/http
gemini
```

