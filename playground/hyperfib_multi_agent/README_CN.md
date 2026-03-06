# Auto Node Builder - Hyperfib 多智能体 Playground

用于自动构建 hyper-fib 工作流节点的多智能体 Playground。

## 概述

本 Playground 实现了 [hyper-fib 科学仪器智能体平台](https://github.com/dptech-corp/hyper-fib) 中的 **Auto Node Builder**。给定节点规格（输入/输出 Schema），自动生成、实现并验证节点代码。

三个智能体以流水线方式协作：

- **Planning Agent**: 分析节点需求（输入/输出 Schema、依赖），制定详细的开发计划
- **Coding Agent**: 根据计划生成节点代码（`node.py`、`node_manifest.json`、`node_test.py`）
- **Validation Agent**: 验证生成的代码是否正确、完整、符合 Schema 规范

## 工作流程

```
┌─────────────────────────┐
│      节点规格描述       │  (input_schema, output_schema, description)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    Planning Agent       │  分析 Schema，规划实现方案
└───────────┬─────────────┘
            │ 开发计划
            ▼
┌─────────────────────────┐
│    Coding Agent         │  生成 node.py, node_manifest.json, node_test.py
└───────────┬─────────────┘
            │ 生成的代码
            ▼
┌─────────────────────────┐
│   Validation Agent      │  运行测试，验证输出符合 Schema
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│     验证通过的节点      │  可部署到 hyper-fib 工作流
└─────────────────────────┘
```

## 节点结构

一个 hyper-fib 工作流节点由以下文件组成：

| 文件 | 说明 |
|------|------|
| `node_manifest.json` | 节点元数据：name, description, input_schema, output_schema, dependencies |
| `node.py` | 实现代码，包含 `def run(inputs: dict) -> dict` 入口函数 |
| `node_test.py` | 测试脚本，验证节点输出符合 output_schema |

### Schema 格式（JSON Schema）

```json
{
  "name": "ImageFormatConversion",
  "description": "图片格式转换节点",
  "input_schema": {
    "type": "object",
    "properties": {
      "source_path": { "type": "string", "title": "源文件路径" },
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

## 快速开始

### 1. 配置

在项目根目录创建 `.env` 文件：

```bash
GPUGEEK_API_KEY=your-api-key
GPUGEEK_BASE_URL=https://api.gpugeek.com/v1
GPUGEEK_MODEL=Vendor2/GPT-5.2
```

### 2. 运行

```bash
# 构建 ImageFormatConversion 节点
python run.py \
  --agent hyperfib_multi_agent \
  --config configs/hyperfib_multi_agent/gpugeek-example.yaml \
  --task "构建一个 ImageFormatConversion 节点，规格如下：
输入 Schema:
- source_path (string, 必填): 输入图片文件路径
- target_format (string, 必填, 枚举: png/jpg/tiff/bmp, 默认: png): 目标格式
- quality (integer, 可选, 范围 1-100, 默认: 95): 输出质量
- resize (object, 可选): {width: integer, height: integer}

输出 Schema:
- output_path (string): 输出文件路径
- file_size (integer): 文件大小(bytes)
- dimensions (object): {width: integer, height: integer}

依赖包: Pillow"
```

### 3. 查看结果

```
runs/hyperfib_multi_agent_{timestamp}/
├── trajectories/       # Agent 执行轨迹
├── logs/              # 执行日志
└── workspaces/task_0/ # 生成的节点文件
    ├── node_manifest.json
    ├── node.py
    └── node_test.py
```

## 配置选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `agents.planning.max_turns` | 规划最大轮数 | `10` |
| `agents.planning.tools.builtin` | 规划工具（无需工具） | `[]` |
| `agents.coding.max_turns` | 编码最大轮数 | `50` |
| `agents.coding.tools.builtin` | 编码工具 | `["*"]` |
| `agents.validation.max_turns` | 验证最大轮数 | `30` |
| `agents.validation.tools.builtin` | 验证工具 | `["*"]` |

## 目录结构

```
playground/hyperfib_multi_agent/
├── core/
│   ├── __init__.py
│   ├── playground.py    # 主 Playground（三智能体设置）
│   └── exp.py           # 多智能体实验（规划 -> 编码 -> 验证）
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

## 相关文档

- [EvoMaster 主 README](../../README.md)
- [Minimal Multi-Agent Playground](../minimal_multi_agent/README_CN.md)
- [hyper-fib 设计文档](https://github.com/dptech-corp/hyper-fib/blob/release/6/docs/scientific_instrument_agent_platform_design.md)
- [配置示例](../../configs/)
