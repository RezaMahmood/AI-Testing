import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class GenericMCPDiscoveryManager:
    """Generic singleton manager for MCP server discovery"""
    _instance: Optional['GenericMCPDiscoveryManager'] = None
    _lock = threading.Lock()
    _discovery_lock = asyncio.Lock()
    
    def __new__(cls) -> 'GenericMCPDiscoveryManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = False
            self._discovered_capabilities: Dict[str, Dict[str, DiscoveredCapability]] = {}
            self._server_configs: Dict[str, MCPServerConfig] = {}
            self._discovery_complete: Dict[str, bool] = {}
    
    def add_server(self, config: MCPServerConfig):
        """Add an MCP server configuration for discovery"""
        self._server_configs[config.name] = config
        self._discovery_complete[config.name] = False
        if config.name not in self._discovered_capabilities:
            self._discovered_capabilities[config.name] = {}
    
    def remove_server(self, server_name: str):
        """Remove an MCP server configuration"""
        self._server_configs.pop(server_name, None)
        self._discovery_complete.pop(server_name, None)
        self._discovered_capabilities.pop(server_name, None)
    
    async def discover_server(self, server_name: str) -> Dict[str, DiscoveredCapability]:
        """Discover capabilities for a specific server"""
        if server_name not in self._server_configs:
            raise ValueError(f"Server '{server_name}' not configured")
        
        async with self._discovery_lock:
            if not self._discovery_complete.get(server_name, False):
                await self._discover_server_capabilities(server_name)
                self._discovery_complete[server_name] = True
        
        return self._discovered_capabilities[server_name].copy()
    
    async def discover_all_servers(self) -> Dict[str, Dict[str, DiscoveredCapability]]:
        """Discover capabilities for all configured servers"""
        results = {}
        
        for server_name in self._server_configs.keys():
            try:
                results[server_name] = await self.discover_server(server_name)
            except Exception as e:
                print(f"❌ Failed to discover server '{server_name}': {e}")
                results[server_name] = {}
        
        return results
    
    async def _discover_server_capabilities(self, server_name: str):
        """Internal method to discover capabilities from an MCP server"""
        config = self._server_configs[server_name]
        print(f"🔍 Discovering capabilities for MCP server: {server_name} ({config.url})")
        
        client = GenericMCPClient(config.url, server_name)
        
        try:
            async with client:
                capabilities = await client.discover_server_capabilities()
                
                # Process discovered tools
                for tool_name, tool_info in capabilities.get("tools", {}).items():
                    capability = DiscoveredCapability(
                        name=tool_name,
                        type=MCPCapabilityType.TOOLS,
                        description=tool_info.get("description", ""),
                        schema=tool_info.get("inputSchema", {}),
                        server_name=server_name,
                        metadata=tool_info
                    )
                    self._discovered_capabilities[server_name][tool_name] = capability
                
                # Process discovered resources
                for resource_id, resource_info in capabilities.get("resources", {}).items():
                    capability = DiscoveredCapability(
                        name=resource_id,
                        type=MCPCapabilityType.RESOURCES,
                        description=resource_info.get("description", ""),
                        schema=resource_info.get("schema", {}),
                        server_name=server_name,
                        metadata=resource_info
                    )
                    self._discovered_capabilities[server_name][resource_id] = capability
                
                # Process discovered prompts
                for prompt_name, prompt_info in capabilities.get("prompts", {}).items():
                    capability = DiscoveredCapability(
                        name=prompt_name,
                        type=MCPCapabilityType.PROMPTS,
                        description=prompt_info.get("description", ""),
                        schema=prompt_info.get("arguments", {}),
                        server_name=server_name,
                        metadata=prompt_info
                    )
                    self._discovered_capabilities[server_name][prompt_name] = capability
                
                server_capability_count = len(self._discovered_capabilities[server_name])
                print(f"✅ Discovered {server_capability_count} capabilities from {server_name}")
                
        except Exception as e:
            print(f"❌ Failed to discover capabilities from {server_name}: {e}")
            raise
    
    def get_discovered_capabilities(self, server_name: str = None) -> Dict[str, Dict[str, DiscoveredCapability]]:
        """Get discovered capabilities for a server or all servers"""
        if server_name:
            if not self._discovery_complete.get(server_name, False):
                raise RuntimeError(f"Server '{server_name}' not yet discovered. Call discover_server() first.")
            return {server_name: self._discovered_capabilities[server_name].copy()}
        
        # Return all discovered capabilities
        result = {}
        for srv_name, capabilities in self._discovered_capabilities.items():
            if self._discovery_complete.get(srv_name, False):
                result[srv_name] = capabilities.copy()
        
        return result
    
    def get_all_tools(self) -> Dict[str, DiscoveredCapability]:
        """Get all discovered tools from all servers"""
        all_tools = {}
        for server_name, capabilities in self._discovered_capabilities.items():
            if self._discovery_complete.get(server_name, False):
                for cap_name, capability in capabilities.items():
                    if capability.type == MCPCapabilityType.TOOLS:
                        # Prefix with server name to avoid conflicts
                        prefixed_name = f"{server_name}__{cap_name}"
                        all_tools[prefixed_name] = capability
        return all_tools
    
    def get_server_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all configured servers"""
        info = {}
        for server_name, config in self._server_configs.items():
            info[server_name] = {
                "url": config.url,
                "discovered": self._discovery_complete.get(server_name, False),
                "capability_count": len(self._discovered_capabilities.get(server_name, {})),
                "capabilities": list(self._discovered_capabilities.get(server_name, {}).keys())
            }
        return info
    
    def reset_discovery(self, server_name: str = None):
        """Reset discovery state for a server or all servers"""
        with self._lock:
            if server_name:
                self._discovery_complete[server_name] = False
                self._discovered_capabilities[server_name] = {}
            else:
                self._discovery_complete.clear()
                self._discovered_capabilities.clear()
    
    def is_discovery_complete(self, server_name: str = None) -> bool:
        """Check if discovery is complete for a server or all servers"""
        if server_name:
            return self._discovery_complete.get(server_name, False)
        return all(self._discovery_complete.values()) if self._discovery_complete else False