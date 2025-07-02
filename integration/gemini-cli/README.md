# Integration with gemini-cli

This guide assumes you have already locally installed:

- [gemini-cli](https://github.com/google-gemini/gemini-cli).
- and [docker engine](https://docs.docker.com/engine/install/)

## Running locally with stdio transport

MCP server can be [added](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md)
to gemini-cli by editing either `~/.gemini/settings.json` in your home directory
or `.gemini/settings.json` where `gemini` command is run.

To get started, there is `integration/gemini-cli/basic/.gemini/settings.json`
provided which can be used by:

```bash
# change to directory where .gemini is
cd integration/gemini-cli/basic

gemini
```

`gemini-cli` will start with `integration/gemini-cli/basic` directory as the context
and start `mcp-anon` in docker as a subprocess with the same context mounted as
its working directory. You can then ask gemini to start building anonymization
pipeline for `example.csv` inside the context like this:

```
Select example.csv for anonymization, then lay out the plan to do so.
```

This will eventually produce `pipeline.py` inside the current directory at the
end of the interaction.

### Prevent gemini from accessing datasource directly

In the previous example, `example.csv` is accessible by both gemini and
`mcp-anon` server. If gemini misbehave, it could try to read the data directly
and leak sensitive imformation to the LLM provider. To prevent this from
happening, we must place `example.csv` outside of working directory and
specifically mount it only inside `mcp-anon` server.

An example of this setup is in `integration/gemini-cli/secure`. To use, run:

```bash
cd integration/gemini-cli/secure
export ANON_TARGET=../basic
gemini
```

Gemini will still get current working directory `integration/gemini-cli/secure`
as its context. But now, `mcp-anon` will mount working directory at
`/opt/app/workdir/host` and mount target directory at `/opt/app/workdir/target`.
From here you can refer to the `example.csv` file in your chat with gemini as
`target/example.csv` and continue the same as before.

```
Select target/example.csv for anonymization, then lay out the plan to do so.
```

### Running in different working directory

You have to copy the MCP server configuration of
`integration/gemini-cli/secure/.gemini/settings.json` into
`~/.gemini/settings.json` and adjust the reference to `entrypoint.sh` so it
still points to the file `integration/gemini-cli/secure/.gemini/entrypoint.sh` in this repository.

TODO: we might write an installation script for this.

