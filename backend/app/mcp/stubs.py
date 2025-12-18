"""Stub interfaces for MCP/A2A extensibility.

These interfaces define the contracts for future integration with:
- MCP (Model Context Protocol) for tool/plugin integration
- A2A (Agent-to-Agent) communication for lab experiment agents
- BER Data Lakehouse for data queries

For MVP, these are stubs. Implementation will be added in future phases.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MCPToolInterface(Protocol):
    """Interface for MCP tool integration.

    MCP tools allow the orchestrator to invoke capabilities
    provided by external systems through a standardized protocol.
    """

    async def list_tools(self) -> list[dict]:
        """List available tools from the MCP server.

        Returns:
            List of tool definitions with name, description, and input schema
        """
        ...

    async def invoke(self, tool_name: str, params: dict) -> dict:
        """Invoke a tool on the MCP server.

        Args:
            tool_name: Name of the tool to invoke
            params: Parameters to pass to the tool

        Returns:
            Tool execution result
        """
        ...


@runtime_checkable
class A2AAgentInterface(Protocol):
    """Interface for Agent-to-Agent communication.

    A2A allows the orchestrator to communicate with lab-specific
    experiment agents to delegate and coordinate tasks.
    """

    async def discover_agents(self) -> list[dict]:
        """Discover available agents in the network.

        Returns:
            List of agent descriptors with id, name, capabilities
        """
        ...

    async def send_task(self, agent_id: str, task: dict) -> str:
        """Send a task to an agent.

        Args:
            agent_id: ID of the target agent
            task: Task definition to send

        Returns:
            Task ID for tracking
        """
        ...

    async def get_result(self, task_id: str) -> dict:
        """Get the result of a submitted task.

        Args:
            task_id: ID of the task to query

        Returns:
            Task result including status and output
        """
        ...

    async def subscribe_to_updates(self, task_id: str, callback: callable) -> None:
        """Subscribe to updates for a task.

        Args:
            task_id: ID of the task to subscribe to
            callback: Function to call with updates
        """
        ...


@runtime_checkable
class DataLakehouseInterface(Protocol):
    """Interface for BER Data Lakehouse queries.

    Allows querying experimental data stored in the
    centralized data lakehouse for analysis and planning.
    """

    async def query(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute a query against the data lakehouse.

        Args:
            query: Query string (SQL-like or custom DSL)
            params: Optional query parameters

        Returns:
            Query results as list of records
        """
        ...

    async def get_dataset_info(self, dataset_id: str) -> dict:
        """Get metadata about a dataset.

        Args:
            dataset_id: ID of the dataset

        Returns:
            Dataset metadata including schema, size, provenance
        """
        ...

    async def list_datasets(
        self,
        filters: dict | None = None,
    ) -> list[dict]:
        """List available datasets.

        Args:
            filters: Optional filters (lab, experiment type, date range)

        Returns:
            List of dataset descriptors
        """
        ...


class MCPToolStub:
    """Stub implementation of MCP tool interface for development."""

    async def list_tools(self) -> list[dict]:
        """Return empty tool list (stub)."""
        return []

    async def invoke(self, tool_name: str, params: dict) -> dict:
        """Return stub response."""
        return {
            "status": "stub",
            "message": f"MCP tool '{tool_name}' not yet implemented",
        }


class A2AAgentStub:
    """Stub implementation of A2A interface for development."""

    async def discover_agents(self) -> list[dict]:
        """Return empty agent list (stub)."""
        return []

    async def send_task(self, agent_id: str, task: dict) -> str:
        """Return stub task ID."""
        return "stub-task-id"

    async def get_result(self, task_id: str) -> dict:
        """Return stub result."""
        return {
            "status": "stub",
            "message": "A2A communication not yet implemented",
        }

    async def subscribe_to_updates(self, task_id: str, callback: callable) -> None:
        """No-op stub."""
        pass


class DataLakehouseStub:
    """Stub implementation of Data Lakehouse interface for development."""

    async def query(self, query: str, params: dict | None = None) -> list[dict]:
        """Return empty results (stub)."""
        return []

    async def get_dataset_info(self, dataset_id: str) -> dict:
        """Return stub dataset info."""
        return {
            "status": "stub",
            "message": "Data Lakehouse not yet connected",
        }

    async def list_datasets(self, filters: dict | None = None) -> list[dict]:
        """Return empty dataset list (stub)."""
        return []


# Default stub instances for development
mcp_tool_stub = MCPToolStub()
a2a_agent_stub = A2AAgentStub()
data_lakehouse_stub = DataLakehouseStub()
