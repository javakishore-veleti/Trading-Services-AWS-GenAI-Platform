#!/usr/bin/env bash
# Start each model engine from its own compose file.
# vLLM and SGLang need an NVIDIA GPU.
# OLLAMA_ENABLED=false (the default) starts a proxy named ollama that forwards to the host.
# OLLAMA_ENABLED=true starts the Ollama container under that same name.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

has_nvidia=0
if docker info 2>/dev/null | grep -Eqi 'nvidia'; then
  has_nvidia=1
fi

if [ "$has_nvidia" -eq 1 ]; then
  echo "Starting vLLM. The first model download can take a long time."
  docker compose -f "$LOCAL_DIR/vLLM/docker-compose.yaml" up -d
  echo "Starting SGLang. The first model download can take a long time."
  docker compose -f "$LOCAL_DIR/SGLang/docker-compose.yaml" up -d
else
  echo "vLLM was not started. vllm/vllm-openai:v0.10.2 needs an NVIDIA GPU, and this machine does not have one."
  echo "SGLang was not started. lmsysorg/sglang:latest needs an NVIDIA GPU, and this machine does not have one."
fi

if [ "$OLLAMA_ENABLED" = "true" ]; then
  echo "Stopping the Ollama proxy so the container can take the name ollama."
  docker compose -f "$LOCAL_DIR/OllamaProxy/docker-compose.yaml" down
  echo "Starting the Ollama container. The model pull continues after the server is listening."
  docker compose -f "$LOCAL_DIR/Ollama/docker-compose.yaml" up -d
else
  echo "Ollama container was not started. OLLAMA_ENABLED is false."
  echo "Stopping the Ollama container so the proxy can take the name ollama. Its model volume is kept."
  docker compose -f "$LOCAL_DIR/Ollama/docker-compose.yaml" down
  echo "Starting the Ollama proxy. LiteLLM still calls http://ollama:11434, which forwards to the host."
  docker compose -f "$LOCAL_DIR/OllamaProxy/docker-compose.yaml" up -d
fi

if [ "$has_nvidia" -eq 1 ]; then
  echo "vLLM OpenAI API:"
  echo "http://127.0.0.1:${VLLM_PORT}/v1"
  echo "SGLang OpenAI API:"
  echo "http://127.0.0.1:${SGLANG_PORT}/v1"
fi
echo "Ollama API, from LiteLLM:"
echo "http://ollama:11434"
echo "Ollama API, on this computer:"
echo "http://127.0.0.1:${OLLAMA_PORT}"
