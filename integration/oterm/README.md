# How to use

## Start ollama service

Make sure the working directory is `integration/oterm`.
The start ollama service in background using:

```bash
docker compose up -d ollama
```

## Download model into ollama

While `ollama` service is running in the background, run:

```bash
docker compose exec ollama \
  ollama pull gemma3:1b
```

The pulled model will persist in `.ollama` directory in working directory.
Model name might be changed as needed.

## Run oterm

```bash
docker compose run --build -i -t --rm oterm
```

