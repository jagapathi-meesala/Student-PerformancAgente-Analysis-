# Agent Architecture

The Student Performance Analysis Agent is built for modularity and framework independence.

## AgentCore
The central orchestrator that manages tool registration and execution. It contains no domain-specific business calculations and is entirely reusable.

## Contracts
- `AgentContract`: Defines the interface for the core agent.
- `ToolContract`: Defines how a deterministic tool must be structured (name, description, schema, execution).
- `AdapterContract`: Defines how external frameworks interact with the agent.

## Registry
The `DynamicToolRegistry` safely loads and stores `ToolContract` implementations. It prevents duplicate registrations and handles missing tool errors cleanly.

## Tools
Pure, isolated Python modules containing deterministic logic. These tools do not rely on LLMs or external network calls.

## Adapters
The portability layer. For example, `PortableAdapter` provides a bridge for any orchestrator (e.g., CrewAI, LangChain, AutoGen) to invoke the agent's tools using a generic dictionary payload, ensuring the core agent remains framework-independent.

## Testing and Extension
The agent is tested via Pytest, checking both valid logic and safety boundaries (e.g., preventing arbitrary code execution). To extend the agent, simply create a new tool implementing `ToolContract` and drop it into the `tools` directory.
