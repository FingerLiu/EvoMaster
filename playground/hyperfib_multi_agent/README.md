# Auto Node Builder - Hyperfib Multi-Agent Playground

A multi-agent playground for automatically building hyper-fib workflow nodes using a 3-step agent pipeline.

## Overview

This playground implements the **Auto Node Builder** from the [hyper-fib scientific instrument agent platform](https://github.com/dptech-corp/hyper-fib). Given a node specification (input/output schemas), it automatically generates, implements, and validates the node code.

Three agents collaborate in a pipeline:

- **Planning Agent**: Analyzes the node requirement (input/output schema, dependencies) and creates a detailed development plan
- **Coding Agent**: Generates the node code based on the plan (`node.py`, `node_manifest.json`, `node_test.py`)
- **Validation Agent**: Verifies the generated code is correct, complete, and conforms to the schema specification

## Workflow

```
┌─────────────────────────┐
│  Node Specification     │  (input_schema, output_schema, description)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Planning Agent       │  Analyzes schemas, plans implementation
└───────────┬─────────────┘
            │ Development Plan
            ▼
┌─────────────────────────┐
│    Coding Agent         │  Generates node.py, node_manifest.json, node_test.py
└───────────┬─────────────┘
            │ Generated Code
            ▼
┌─────────────────────────┐
│   Validation Agent      │  Runs tests, validates output against schema
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Validated Node        │  Ready to deploy in hyper-fib workflow
└─────────────────────────┘
```

## Node Structure

A hyper-fib workflow node consists of:

| File | Description |
|------|-------------|
| `node_manifest.json` | Node metadata: name, description, input_schema, output_schema, dependencies |
| `node.py` | Implementation with `def run(inputs: dict) -> dict` entry function |
| `node_test.py` | Test script validating the node against its schema |

### Schema Format (JSON Schema)

```json
{
  "name": "ImageFormatConversion",
  "description": "Image format conversion node",
  "input_schema": {
    "type": "object",
    "properties": {
      "source_path": { "type": "string", "title": "Source file path" },
      "target_format": { "type": "string", "enum": ["png", "jpg", "tiff", "bmp"], "default": "png" }
    },
    "required": ["source_path", "target_format"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "output_path": { "type": "string" },
      "file_size": { "type": "integer" }
    }
  },
  "dependencies": ["Pillow"]
}
```

## Quick Start

### 1. Configure

Create a `.env` file in the project root:

```bash
GPUGEEK_API_KEY=your-api-key
GPUGEEK_BASE_URL=https://api.gpugeek.com/v1
GPUGEEK_MODEL=Vendor2/GPT-5.2
```

### 2. Run

```bash
# Build an ImageFormatConversion node
python run.py \
  --agent hyperfib_multi_agent \
  --config configs/hyperfib_multi_agent/gpugeek-example.yaml \
  --task "Build an ImageFormatConversion node with the following specification:
Input schema:
- source_path (string, required): Input image file path
- target_format (string, required, enum: png/jpg/tiff/bmp, default: png): Target format
- quality (integer, optional, range 1-100, default: 95): Output quality
- resize (object, optional): {width: integer, height: integer}

Output schema:
- output_path (string): Output file path
- file_size (integer): File size in bytes
- dimensions (object): {width: integer, height: integer}

Dependencies: Pillow"
```

### 3. View Results

```
runs/hyperfib_multi_agent_{timestamp}/
├── trajectories/       # Agent execution trajectories
├── logs/              # Execution logs
└── workspaces/task_0/ # Generated node files
    ├── node_manifest.json
    ├── node.py
    └── node_test.py
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `agents.planning.max_turns` | Max planning turns | `10` |
| `agents.planning.tools.builtin` | Planning tools (none needed) | `[]` |
| `agents.coding.max_turns` | Max coding turns | `50` |
| `agents.coding.tools.builtin` | Coding tools | `["*"]` |
| `agents.validation.max_turns` | Max validation turns | `30` |
| `agents.validation.tools.builtin` | Validation tools | `["*"]` |

## Directory Structure

```
playground/hyperfib_multi_agent/
├── core/
│   ├── __init__.py
│   ├── playground.py    # Main playground (3-agent setup)
│   └── exp.py           # Multi-agent experiment (plan -> code -> validate)
├── prompts/
│   ├── system_prompt.txt
│   ├── planning_system_prompt.txt
│   ├── planning_user_prompt.txt
│   ├── coding_system_prompt.txt
│   ├── coding_user_prompt.txt
│   ├── validation_system_prompt.txt
│   └── validation_user_prompt.txt
├── README.md
└── README_CN.md
```

## Related

- [EvoMaster Main README](../../README.md)
- [Minimal Multi-Agent Playground](../minimal_multi_agent/README.md)
- [hyper-fib Design Doc](https://github.com/dptech-corp/hyper-fib/blob/release/6/docs/scientific_instrument_agent_platform_design.md)
- [Configuration Examples](../../configs/)
