class GenericMCPInspector:
    def __init__(self):
        self.discovery_manager = GenericMCPDiscoveryManager()
    
    async def inspect_server(self, server_config: MCPServerConfig) -> Dict[str, Any]:
        """Inspect a single MCP server"""
        self.discovery_manager.add_server(server_config)
        
        try:
            capabilities = await self.discovery_manager.discover_server(server_config.name)
            return self._format_server_report(server_config.name, capabilities)
        except Exception as e:
            return {
                "server_name": server_config.name,
                "url": server_config.url,
                "error": str(e),
                "status": "failed"
            }
    
    async def inspect_multiple_servers(self, server_configs: List[MCPServerConfig]) -> Dict[str, Any]:
        """Inspect multiple MCP servers"""
        # Add all servers
        for config in server_configs:
            self.discovery_manager.add_server(config)
        
        # Discover all
        all_capabilities = await self.discovery_manager.discover_all_servers()
        
        # Format reports
        reports = {}
        for server_name, capabilities in all_capabilities.items():
            reports[server_name] = self._format_server_report(server_name, capabilities)
        
        # Add summary
        reports["_summary"] = self._generate_summary_report(all_capabilities)
        
        return reports
    
    def _format_server_report(self, server_name: str, capabilities: Dict[str, DiscoveredCapability]) -> Dict[str, Any]:
        """Format a report for a single server"""
        tools = {}
        resources = {}
        prompts = {}
        
        for cap_name, capability in capabilities.items():
            cap_info = {
                "name": capability.name,
                "description": capability.description,
                "schema": capability.schema,
                "metadata": capability.metadata
            }
            
            if capability.type == MCPCapabilityType.TOOLS:
                tools[cap_name] = cap_info
            elif capability.type == MCPCapabilityType.RESOURCES:
                resources[cap_name] = cap_info
            elif capability.type == MCPCapabilityType.PROMPTS:
                prompts[cap_name] = cap_info
        
        config = self.discovery_manager._server_configs.get(server_name)
        
        return {
            "server_name": server_name,
            "url": config.url if config else "unknown",
            "status": "success",
            "totals": {
                "tools": len(tools),
                "resources": len(resources),
                "prompts": len(prompts),
                "total": len(capabilities)
            },
            "capabilities": {
                "tools": tools,
                "resources": resources,
                "prompts": prompts
            }
        }
    
    def _generate_summary_report(self, all_capabilities: Dict[str, Dict[str, DiscoveredCapability]]) -> Dict[str, Any]:
        """Generate a summary report across all servers"""
        total_servers = len(all_capabilities)
        total_capabilities = sum(len(caps) for caps in all_capabilities.values())
        
        by_type = {
            "tools": 0,
            "resources": 0,
            "prompts": 0
        }
        
        for capabilities in all_capabilities.values():
            for capability in capabilities.values():
                if capability.type == MCPCapabilityType.TOOLS:
                    by_type["tools"] += 1
                elif capability.type == MCPCapabilityType.RESOURCES:
                    by_type["resources"] += 1
                elif capability.type == MCPCapabilityType.PROMPTS:
                    by_type["prompts"] += 1
        
        return {
            "total_servers": total_servers,
            "total_capabilities": total_capabilities,
            "capabilities_by_type": by_type,
            "servers": list(all_capabilities.keys())
        }
    
    async def print_inspection_report(self, server_configs: List[MCPServerConfig]):
        """Print a formatted inspection report"""
        print("=== Generic MCP Server Discovery Report ===\n")
        
        if len(server_configs) == 1:
            report = await self.inspect_server(server_configs[0])
            self._print_single_server_report(report)
        else:
            reports = await self.inspect_multiple_servers(server_configs)
            self._print_multiple_server_reports(reports)
    
    def _print_single_server_report(self, report: Dict[str, Any]):
        """Print report for a single server"""
        if report.get("status") == "failed":
            print(f"❌ Failed to inspect {report['server_name']}: {report.get('error')}")
            return
        
        print(f"Server: {report['server_name']}")
        print(f"URL: {report['url']}")
        print(f"Status: ✅ {report['status']}")
        print(f"Total Capabilities: {report['totals']['total']}")
        print(f"  - Tools: {report['totals']['tools']}")
        print(f"  - Resources: {report['totals']['resources']}")  
        print(f"  - Prompts: {report['totals']['prompts']}")
        
        # Print detailed capabilities
        for cap_type, capabilities in report['capabilities'].items():
            if capabilities:
                print(f"\n{cap_type.title()}:")
                for name, info in capabilities.items():
                    print(f"  - {name}: {info['description']}")
    
    def _print_multiple_server_reports(self, reports: Dict[str, Any]):
        """Print reports for multiple servers"""
        summary = reports.pop("_summary", {})
        
        print(f"Discovered {summary.get('total_capabilities', 0)} capabilities across {summary.get('total_servers', 0)} servers\n")
        
        for server_name, report in reports.items():
            print(f"--- {server_name} ---")
            self._print_single_server_report(report)
            print()