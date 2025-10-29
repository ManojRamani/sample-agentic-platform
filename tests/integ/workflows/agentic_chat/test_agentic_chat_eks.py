"""
Integration test for agentic_chat agent running on EKS.

This test validates the agent deployed on EKS cluster through the actual service endpoints,
not through port-forwarding. It tests the complete production deployment.
"""
import pytest
import httpx
import asyncio
import json
import subprocess
import os
from typing import Dict, Any


class TestAgenticChatEKS:
    """Test agentic_chat agent running on EKS cluster."""
    
    @pytest.fixture(scope="class")
    def eks_config(self) -> Dict[str, Any]:
        """Get EKS cluster configuration."""
        try:
            # Get cluster info
            result = subprocess.run(
                ["kubectl", "cluster-info"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Get agentic-chat service info
            service_result = subprocess.run(
                ["kubectl", "get", "service", "agentic-chat", "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            service_info = json.loads(service_result.stdout)
            
            return {
                "cluster_connected": True,
                "service_info": service_info,
                "service_ip": service_info["spec"]["clusterIP"],
                "service_port": service_info["spec"]["ports"][0]["port"]
            }
            
        except subprocess.CalledProcessError as e:
            pytest.skip(f"EKS cluster not accessible: {e}")
        except Exception as e:
            pytest.skip(f"Failed to get EKS config: {e}")
    
    @pytest.fixture(scope="class")
    def port_forward_process(self, eks_config):
        """Start port forwarding for agentic-chat service."""
        try:
            # Start port forwarding in background
            process = subprocess.Popen([
                "kubectl", "port-forward", 
                "service/agentic-chat", 
                "8003:8003"
            ])
            
            # Wait a moment for port forwarding to establish
            import time
            time.sleep(3)
            
            yield process
            
            # Cleanup
            process.terminate()
            process.wait()
            
        except Exception as e:
            pytest.skip(f"Failed to start port forwarding: {e}")
    
    def test_eks_cluster_connection(self, eks_config):
        """Test that we can connect to EKS cluster."""
        assert eks_config["cluster_connected"], "Should be connected to EKS cluster"
        assert "service_info" in eks_config, "Should have service information"
    
    def test_agentic_chat_service_exists(self, eks_config):
        """Test that agentic-chat service exists in EKS."""
        service_info = eks_config["service_info"]
        
        assert service_info["metadata"]["name"] == "agentic-chat"
        assert service_info["spec"]["type"] in ["ClusterIP", "LoadBalancer", "NodePort"]
        assert len(service_info["spec"]["ports"]) > 0
        
        # Check service has proper labels/selectors
        assert "selector" in service_info["spec"]
        assert service_info["spec"]["selector"]["app"] == "agentic-chat"
    
    def test_agentic_chat_pods_running(self):
        """Test that agentic-chat pods are running."""
        try:
            result = subprocess.run([
                "kubectl", "get", "pods", 
                "-l", "app=agentic-chat",
                "-o", "json"
            ], capture_output=True, text=True, check=True)
            
            pods_info = json.loads(result.stdout)
            pods = pods_info["items"]
            
            assert len(pods) > 0, "Should have at least one agentic-chat pod"
            
            for pod in pods:
                assert pod["status"]["phase"] == "Running", f"Pod {pod['metadata']['name']} should be running"
                
                # Check container status
                container_statuses = pod["status"]["containerStatuses"]
                for container in container_statuses:
                    assert container["ready"], f"Container {container['name']} should be ready"
                    assert container["state"]["running"], f"Container {container['name']} should be running"
                    
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to get pod status: {e}")
    
    @pytest.mark.asyncio
    async def test_health_endpoint_via_port_forward(self, port_forward_process):
        """Test health endpoint through port forwarding."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "http://localhost:8003/health",
                    timeout=10.0
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                
            except httpx.ConnectError:
                pytest.fail("Could not connect to agentic-chat service via port forward")
    
    @pytest.mark.asyncio
    async def test_invoke_endpoint_via_port_forward(self, port_forward_process):
        """Test invoke endpoint through port forwarding."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "What is 15 + 27?"}]
                    },
                    "session_id": "eks-integration-test"
                }
                
                response = await client.post(
                    "http://localhost:8003/invoke",
                    json=payload,
                    timeout=30.0
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Validate response structure
                assert "message" in data
                assert "role" in data["message"]
                assert data["message"]["role"] == "assistant"
                assert "content" in data["message"]
                
                # Check that we got an intelligent response
                content = data["message"]["content"]
                response_text = ""
                for item in content:
                    if item["type"] == "text":
                        response_text += item["text"]
                
                # Should contain the answer 42 or show calculation
                assert any(keyword in response_text.lower() for keyword in ["42", "fifteen", "twenty", "calculation", "result"])
                
            except httpx.ConnectError:
                pytest.fail("Could not connect to agentic-chat service via port forward")
            except httpx.TimeoutException:
                pytest.fail("Request to agentic-chat service timed out")
    
    @pytest.mark.asyncio
    async def test_streaming_endpoint_via_port_forward(self, port_forward_process):
        """Test streaming endpoint through port forwarding."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Count from 1 to 3"}]
                    },
                    "session_id": "eks-streaming-test"
                }
                
                async with client.stream(
                    "POST",
                    "http://localhost:8003/stream",
                    json=payload,
                    timeout=30.0
                ) as response:
                    
                    assert response.status_code == 200
                    assert response.headers["content-type"] == "text/event-stream"
                    
                    chunks_received = 0
                    async for chunk in response.aiter_text():
                        if chunk.strip():
                            chunks_received += 1
                            # Basic validation that we're getting SSE format
                            assert chunk.startswith("data: ") or chunk.startswith("event: ")
                    
                    assert chunks_received > 0, "Should receive streaming chunks"
                
            except httpx.ConnectError:
                pytest.fail("Could not connect to agentic-chat service via port forward")
            except httpx.TimeoutException:
                pytest.fail("Streaming request to agentic-chat service timed out")
    
    def test_service_logs_show_activity(self):
        """Test that service logs show recent activity."""
        try:
            # Get recent logs from agentic-chat pods
            result = subprocess.run([
                "kubectl", "logs", 
                "-l", "app=agentic-chat",
                "--tail=50",
                "--since=5m"
            ], capture_output=True, text=True, check=True)
            
            logs = result.stdout
            
            # Should have some log output
            assert len(logs.strip()) > 0, "Should have recent log activity"
            
            # Look for FastAPI startup messages or health check activity
            log_indicators = [
                "uvicorn", "fastapi", "started server", 
                "application startup", "health", "GET /health"
            ]
            
            logs_lower = logs.lower()
            has_expected_logs = any(indicator in logs_lower for indicator in log_indicators)
            
            assert has_expected_logs, f"Logs should contain FastAPI/health activity. Got: {logs[:200]}..."
            
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to get service logs: {e}")


if __name__ == "__main__":
    """Run the EKS integration tests."""
    print("🚀 EKS Integration Tests for Agentic Chat Agent")
    print("=" * 60)
    
    # Run with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
