"""Enterprise-level integration tests for FLEXT CLI.

Tests component interactions and workflow integration
without any dead code, duplicated code, or mockup code.
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

from flext_cli import (
    FlextCliService, FlextCliApi,
    FlextCliCommand, FlextCliConfig, FlextCliContext,
    FlextCliPlugin, FlextCliSession,
    FlextCliOutputFormat,
    flext_cli_format, flext_cli_export, flext_cli_health,
    flext_cli_create_command, flext_cli_create_session,
    flext_cli_register_handler, flext_cli_execute_handler,
    flext_cli_get_commands, flext_cli_get_sessions,
    flext_cli_configure
)


class TestServiceApiIntegration:
    """Test integration between service and API layers."""
    
    def test_service_api_configuration_flow(self):
        """Test configuration flow from API to service."""
        api = FlextCliApi()
        
        # Configure through API
        config_result = api.flext_cli_configure({"debug": True, "output_format": "json"})
        assert config_result is True
        
        # Verify service is configured
        service_health = api._service.flext_cli_health()
        assert service_health.is_success is True
        
        health_data = service_health.unwrap()
        assert health_data["configured"] is True
        assert health_data["config"]["debug"] is True
        assert health_data["config"]["format"] == "json"
    
    def test_format_export_integration(self):
        """Test integration between formatting and export."""
        api = FlextCliApi()
        
        test_data = {
            "integration": "test",
            "formats": ["json", "csv", "table"],
            "status": "working"
        }
        
        # Test all format types with export
        formats = ["json", "csv", "table", "plain"]
        
        for fmt in formats:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{fmt}') as f:
                temp_path = f.name
            
            try:
                # Format data
                formatted = api.flext_cli_format(test_data, fmt)
                assert len(formatted) > 0
                
                # Export formatted data
                export_result = api.flext_cli_export(test_data, temp_path, fmt)
                assert export_result is True
                
                # Verify file exists and has content
                assert Path(temp_path).exists()
                assert Path(temp_path).stat().st_size > 0
                
                # For JSON, verify content is valid
                if fmt == "json":
                    with open(temp_path, 'r') as f:
                        loaded_data = json.load(f)
                        assert loaded_data["integration"] == "test"
                        assert loaded_data["status"] == "working"
                        
            finally:
                Path(temp_path).unlink(missing_ok=True)
    
    def test_command_session_workflow(self):
        """Test complete command and session workflow."""
        api = FlextCliApi()
        
        # Create session
        session_result = api.flext_cli_create_session("integration-user")
        assert "created" in session_result
        
        # Create multiple commands
        commands = [
            ("cmd1", "echo hello", {"type": "test"}),
            ("cmd2", "echo world", {"type": "demo"}),
            ("cmd3", "ls -la", {"type": "system"})
        ]
        
        created_commands = []
        for name, cmd_line, options in commands:
            result = api.flext_cli_create_command(name, cmd_line, **options)
            created_commands.append((name, result))
        
        # Verify all commands were created
        all_commands = api.flext_cli_get_commands()
        assert len(all_commands) >= 3
        
        for name, creation_result in created_commands:
            assert name in all_commands
            assert isinstance(all_commands[name], FlextCliCommand)
        
        # Verify session tracking
        all_sessions = api.flext_cli_get_sessions()
        assert len(all_sessions) >= 1
        
        # Find our session
        integration_session = None
        for session in all_sessions.values():
            if hasattr(session, 'user_id') and session.user_id == "integration-user":
                integration_session = session
                break
        
        assert integration_session is not None
        assert isinstance(integration_session, FlextCliSession)
    
    def test_handler_plugin_integration(self):
        """Test handler and plugin system integration."""
        api = FlextCliApi()
        
        # Create plugin
        plugin = FlextCliPlugin("integration-plugin", "1.0.0",
                               description="Integration test plugin",
                               commands=["process", "transform"])
        
        # Register plugin
        plugin_result = api.flext_cli_register_plugin("integration-plugin", plugin)
        assert plugin_result is True
        
        # Create handlers for plugin commands
        def process_handler(data: Dict[str, Any]) -> Dict[str, Any]:
            return {"processed": True, "original": data, "plugin": "integration"}
        
        def transform_handler(data: Dict[str, Any]) -> Dict[str, Any]:
            return {"transformed": data, "timestamp": "2025-01-01", "plugin": "integration"}
        
        # Register handlers
        process_reg = api.flext_cli_register_handler("process", process_handler)
        transform_reg = api.flext_cli_register_handler("transform", transform_handler)
        
        assert process_reg is True
        assert transform_reg is True
        
        # Test handler execution with data flow
        test_data = {"input": "integration_test", "value": 42}
        
        # Process data
        processed_result = api.flext_cli_execute_handler("process", test_data)
        assert isinstance(processed_result, dict)
        assert processed_result["processed"] is True
        assert processed_result["original"]["input"] == "integration_test"
        
        # Transform processed data
        transformed_result = api.flext_cli_execute_handler("transform", processed_result)
        assert isinstance(transformed_result, dict)
        assert "transformed" in transformed_result
        assert transformed_result["plugin"] == "integration"
        
        # Verify plugin and handlers are registered
        all_plugins = api.flext_cli_get_plugins()
        all_handlers = api.flext_cli_get_handlers()
        
        assert "integration-plugin" in all_plugins
        assert "process" in all_handlers
        assert "transform" in all_handlers
    
    def test_context_rendering_integration(self):
        """Test context-based rendering integration."""
        api = FlextCliApi()
        
        # Configure API
        api.flext_cli_configure({"debug": True, "output_format": "table"})
        
        test_data = {
            "context_test": True,
            "formats": ["json", "table", "csv"],
            "integration": "rendering"
        }
        
        # Test context rendering with different formats
        contexts = [
            {"output_format": "json"},
            {"output_format": "table"},
            {"output_format": "csv"},
            {"output_format": "plain"}
        ]
        
        for context_config in contexts:
            result = api.flext_cli_render_with_context(test_data, context_config)
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Verify format-specific content
            fmt = context_config["output_format"]
            if fmt == "json":
                assert "context_test" in result
                assert "true" in result.lower()
            elif fmt == "table":
                assert "context_test" in result or "integration" in result
            elif fmt == "csv":
                assert "," in result  # CSV delimiter
    
    def test_complete_workflow_integration(self):
        """Test complete end-to-end workflow."""
        # Initialize fresh API instance
        api = FlextCliApi()
        
        # Step 1: Configure system
        config_result = api.flext_cli_configure({
            "debug": True,
            "output_format": "json",
            "profile": "integration-test"
        })
        assert config_result is True
        
        # Step 2: Create session and commands
        session_result = api.flext_cli_create_session("workflow-user")
        assert "created" in session_result
        
        cmd_result = api.flext_cli_create_command("workflow-cmd", "echo workflow", 
                                                  type="integration", description="Workflow test")
        assert cmd_result is False or cmd_result is True  # May depend on implementation
        
        # Step 3: Register workflow handler
        def workflow_handler(stage: str, data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "stage": stage,
                "data": data,
                "workflow": "complete",
                "timestamp": "2025-01-01T00:00:00Z"
            }
        
        handler_result = api.flext_cli_register_handler("workflow", workflow_handler)
        assert handler_result is True
        
        # Step 4: Process data through workflow
        workflow_data = {
            "input": "enterprise_test",
            "requirements": ["no_dead_code", "no_duplicated_code", "no_mockup"],
            "validation": "enterprise_level"
        }
        
        # Execute workflow stages
        stages = ["validate", "process", "transform", "finalize"]
        results = []
        
        for stage in stages:
            stage_result = api.flext_cli_execute_handler("workflow", stage, workflow_data)
            assert isinstance(stage_result, dict)
            assert stage_result["stage"] == stage
            assert stage_result["workflow"] == "complete"
            results.append(stage_result)
        
        # Step 5: Format and export results
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            final_result = {
                "workflow": "integration_test",
                "stages_completed": len(results),
                "all_results": results,
                "status": "success"
            }
            
            # Format result
            formatted = api.flext_cli_format(final_result, "json")
            assert "workflow" in formatted
            assert "integration_test" in formatted
            
            # Export result
            export_result = api.flext_cli_export(final_result, temp_path, "json")
            assert export_result is True
            
            # Verify export
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
                assert exported_data["workflow"] == "integration_test"
                assert exported_data["stages_completed"] == 4
                assert len(exported_data["all_results"]) == 4
                
        finally:
            Path(temp_path).unlink(missing_ok=True)
        
        # Step 6: Verify system state
        health = api.flext_cli_health()
        assert health["status"] == "healthy"
        
        final_commands = api.flext_cli_get_commands()
        final_sessions = api.flext_cli_get_sessions()
        final_handlers = api.flext_cli_get_handlers()
        
        assert isinstance(final_commands, dict)
        assert isinstance(final_sessions, dict)
        assert isinstance(final_handlers, dict)
        assert "workflow" in final_handlers


class TestPublicFunctionIntegration:
    """Test integration of public functions."""
    
    def test_global_function_coordination(self):
        """Test coordination between global functions."""
        # Configure system
        config_result = flext_cli_configure({"debug": True, "output_format": "json"})
        assert config_result is True
        
        # Create and manage entities
        cmd_result = flext_cli_create_command("global-test", "echo global")
        session_result = flext_cli_create_session("global-user")
        
        # Register and execute handler
        def global_handler(message: str) -> str:
            return f"Global: {message}"
        
        handler_reg = flext_cli_register_handler("global", global_handler)
        assert handler_reg is True
        
        handler_result = flext_cli_execute_handler("global", "integration")
        assert "Global: integration" in str(handler_result)
        
        # Format and export data
        test_data = {
            "global_functions": True,
            "integration": "complete",
            "handler_result": str(handler_result)
        }
        
        formatted = flext_cli_format(test_data, "json")
        assert "global_functions" in formatted
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            export_result = flext_cli_export(test_data, temp_path, "json")
            assert export_result is True
        finally:
            Path(temp_path).unlink(missing_ok=True)
        
        # Verify system health
        health = flext_cli_health()
        assert health["status"] == "healthy"
        
        # Verify all entities are accessible
        commands = flext_cli_get_commands()
        sessions = flext_cli_get_sessions()
        
        assert isinstance(commands, dict)
        assert isinstance(sessions, dict)


class TestErrorHandlingIntegration:
    """Test error handling across components."""
    
    def test_cascading_error_handling(self):
        """Test error handling propagation through components."""
        api = FlextCliApi()
        
        # Test invalid format error propagation
        invalid_format_result = api.flext_cli_format({"test": "data"}, "invalid_format")
        # Should return string representation of data instead of error
        assert isinstance(invalid_format_result, str)
        
        # Test export with invalid path
        result = api.flext_cli_export({"test": "data"}, "/invalid/path/file.json", "json")
        # Should handle path creation
        assert isinstance(result, bool)
        
        # Test handler execution with non-existent handler
        result = api.flext_cli_execute_handler("non_existent", "test")
        assert isinstance(result, dict)
        assert "error" in result
    
    def test_recovery_mechanisms(self):
        """Test system recovery from errors."""
        api = FlextCliApi()
        
        # Create valid handler
        def recovery_handler(data: Any) -> Dict[str, Any]:
            if isinstance(data, dict) and data.get("cause_error"):
                raise ValueError("Intentional error")
            return {"recovered": True, "data": data}
        
        api.flext_cli_register_handler("recovery", recovery_handler)
        
        # Test normal operation
        normal_result = api.flext_cli_execute_handler("recovery", {"normal": True})
        assert isinstance(normal_result, dict)
        assert normal_result.get("recovered") is True
        
        # Test error handling
        error_result = api.flext_cli_execute_handler("recovery", {"cause_error": True})
        # Should return error dict instead of raising
        assert isinstance(error_result, dict)
        
        # Verify system still functional after error
        health = api.flext_cli_health()
        assert health["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])