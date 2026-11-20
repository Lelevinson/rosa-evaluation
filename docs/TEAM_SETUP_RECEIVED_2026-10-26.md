# rosa-llm: Team Setup

## 1. Prepare

- Python **3.12**, **uv**, and a working **ROSA / ROS 2 Jazzy** environment.
- Either your own ChatGPT account with model access, or a reachable Ollama server
  with a tool-capable model installed.

## 2. Install

Run inside your existing ROSA uv project; no package clone is needed:

```bash
uv add --marker "python_version >= '3.11'" "rosa-llm[langchain]==0.1.0"
```

The marker preserves ROSA's declared Python ≥3.9 range; the package runs only on
≥3.11. Omit `--marker "python_version >= '3.11'"` if your project already requires
≥3.11. Keep `==0.1.0` to select this release.

If the dependency and lockfile are already shared in your project, use
`uv sync --locked` instead.

## 3. Configure

Edit `.env` in the directory where you run your application. Choose one provider
and replace the model placeholder.

**Ollama:**

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=YOUR_INSTALLED_MODEL
```

**OpenAI through ChatGPT OAuth:**

```dotenv
LLM_PROVIDER=openai
OPENAI_MODEL=YOUR_AVAILABLE_MODEL
ROSA_LLM_REQUIRE_EXPLICIT_MODEL=true
```

For OpenAI, sign in once:

```bash
uv run rosa-llm login --provider openai
```

No OpenAI API key is used. Each teammate signs in separately; never share
credentials or commit `.env`.

## 4. Use in ROSA

Save as `your_script.py`. The same code works with either provider:

```python
from rosa import ROSA
from rosa_llm import create_client
from rosa_llm.langchain import ChatRosaLLM

with create_client() as client:
    model = ChatRosaLLM(client=client)
    agent = ROSA(ros_version=2, llm=model, streaming=False)
    print(agent.invoke("List the current ROS 2 nodes."))
```

`create_client()` reads `.env`; `with` keeps the client open during agent execution
and closes it afterward. ROSA executes the tools.

```bash
source /opt/ros/jazzy/setup.bash
uv run your_script.py
```

## WSL / Docker

Use an Ollama address reachable from your runtime. Inside Docker, `localhost`
means the container. Docker OAuth needs callback connectivity and persistent
private credential storage. The package image does not include ROSA or ROS.
See the [Docker setup](https://github.com/Lelevinson/rosa-llm-package#docker).
