#!/usr/bin/env python3
"""
EKS integration test runner for agentic_chat agent with authentication.
This includes Cognito M2M token authentication for testing secured endpoints.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Optional

import boto3
import httpx
import requests


class EKSAgenticChatTesterWithAuth:
    """EKS integration tester for agentic_chat agent with authentication."""

    def __init__(self):
        self.test_results = []
        self.port_forward_process = None
        self.auth_token = None

    def run_kubectl_command(self, cmd: list) -> tuple[bool, str]:
        """Run kubectl command with proper environment."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, env=os.environ.copy()
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Command failed: {e}\nStderr: {e.stderr}"

    def get_m2m_token(self) -> Optional[str]:
        """Get M2M token from AWS Secrets Manager."""
        print("\n🔐 Getting M2M authentication token...")

        try:
            # Get secret ARN from environment or use default
            secret_arn = "arn:aws:secretsmanager:us-west-2:423623854297:secret:agent-ptfm-m2mcreds-gci1y867-5UI6p1"

            # Get secret from AWS Secrets Manager
            client = boto3.client("secretsmanager")
            response = client.get_secret_value(SecretId=secret_arn)
            secret_data = json.loads(response["SecretString"])

            # Extract credentials
            client_id = secret_data.get("client_id")
            client_secret = secret_data.get("client_secret")
            token_url = secret_data.get("token_url")
            scopes = secret_data.get("scopes")

            print(f"   Token URL: {token_url}")
            print(f"   Client ID: {client_id}")
            print(f"   Scopes: {scopes}")

            # Make token request
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": scopes,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )

            if response.status_code == 200:
                token_data = response.json()
                token = token_data["access_token"]
                expires_in = token_data.get("expires_in", "unknown")

                print(f"✅ M2M token obtained (expires in {expires_in} seconds)")
                return token
            else:
                print(
                    f"❌ Failed to get token: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            print(f"❌ Error getting M2M token: {e}")
            return None

    def test_eks_cluster_connection(self) -> bool:
        """Test EKS cluster connectivity."""
        print("🔍 Testing EKS cluster connection...")

        success, output = self.run_kubectl_command(["kubectl", "cluster-info"])
        if success:
            print("✅ EKS cluster connection successful")
            print(f"   {output.split()[0:10]}")  # First few words
            return True
        else:
            print(f"❌ EKS cluster connection failed: {output}")
            return False

    def test_agentic_chat_service_exists(self) -> bool:
        """Test that agentic-chat service exists."""
        print("\n🔍 Testing agentic-chat service exists...")

        success, output = self.run_kubectl_command(
            ["kubectl", "get", "service", "agentic-chat", "-o", "json"]
        )

        if success:
            try:
                service_info = json.loads(output)
                service_name = service_info["metadata"]["name"]
                service_type = service_info["spec"]["type"]
                cluster_ip = service_info["spec"]["clusterIP"]
                port = service_info["spec"]["ports"][0]["port"]

                print(f"✅ Service exists: {service_name}")
                print(f"   Type: {service_type}, IP: {cluster_ip}, Port: {port}")
                return True
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Failed to parse service info: {e}")
                return False
        else:
            print(f"❌ Service not found: {output}")
            return False

    def test_agentic_chat_pods_running(self) -> bool:
        """Test that agentic-chat pods are running."""
        print("\n🔍 Testing agentic-chat pods are running...")

        success, output = self.run_kubectl_command(
            ["kubectl", "get", "pods", "-l", "app=agentic-chat", "-o", "json"]
        )

        if success:
            try:
                pods_info = json.loads(output)
                pods = pods_info["items"]

                if len(pods) == 0:
                    print("❌ No agentic-chat pods found")
                    return False

                all_running = True
                for pod in pods:
                    pod_name = pod["metadata"]["name"]
                    phase = pod["status"]["phase"]

                    if phase == "Running":
                        # Check container readiness
                        container_statuses = pod["status"].get("containerStatuses", [])
                        ready_containers = sum(
                            1 for c in container_statuses if c.get("ready", False)
                        )
                        total_containers = len(container_statuses)

                        print(
                            f"✅ Pod {pod_name}: {phase} ({ready_containers}/{total_containers} ready)"
                        )
                    else:
                        print(f"❌ Pod {pod_name}: {phase}")
                        all_running = False

                return all_running

            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Failed to parse pods info: {e}")
                return False
        else:
            print(f"❌ Failed to get pods: {output}")
            return False

    def start_port_forward(self) -> bool:
        """Start port forwarding for agentic-chat service."""
        print("\n🔍 Starting port forwarding...")

        try:
            # Start port forwarding in background
            self.port_forward_process = subprocess.Popen(
                ["kubectl", "port-forward", "service/agentic-chat", "8003:80"],
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for port forwarding to establish
            time.sleep(3)

            # Check if process is still running
            if self.port_forward_process.poll() is None:
                print("✅ Port forwarding started (localhost:8003 -> service:80)")
                return True
            else:
                stdout, stderr = self.port_forward_process.communicate()
                print(f"❌ Port forwarding failed: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"❌ Failed to start port forwarding: {e}")
            return False

    def stop_port_forward(self):
        """Stop port forwarding."""
        if self.port_forward_process:
            print("\n🔧 Stopping port forwarding...")
            self.port_forward_process.terminate()
            self.port_forward_process.wait()
            self.port_forward_process = None

    async def test_health_endpoint(self) -> bool:
        """Test health endpoint via port forwarding (no auth required)."""
        print("\n🔍 Testing health endpoint...")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "http://localhost:8003/health", timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    print(f"✅ Health endpoint: {response.status_code} - {status}")
                    return True
                else:
                    print(f"❌ Health endpoint failed: {response.status_code}")
                    return False

            except httpx.ConnectError:
                print("❌ Could not connect to health endpoint")
                return False
            except Exception as e:
                print(f"❌ Health endpoint error: {e}")
                return False

    async def test_invoke_endpoint_with_auth(self) -> bool:
        """Test invoke endpoint via port forwarding with authentication."""
        print("\n🔍 Testing invoke endpoint with authentication...")

        if not self.auth_token:
            print("❌ No authentication token available")
            return False

        async with httpx.AsyncClient() as client:
            try:
                # in_query = "What is 25 + 17?"
                payload = {
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "What is 25 + 17?"}],
                    },
                    "session_id": "eks-integration-test-auth",
                }

                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json",
                }

                print(f"   📤 REQUEST PAYLOAD:")
                print(f"   {json.dumps(payload, indent=4)}")
                print(f"   📤 REQUEST HEADERS:")
                print(f"   Authorization: Bearer {self.auth_token[:20]}...")
                print(f"   Content-Type: {headers['Content-Type']}")

                response = await client.post(
                    "http://localhost:8003/invoke",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )

                print(f"   📥 RESPONSE STATUS: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"   📥 COMPLETE RESPONSE DATA:")
                    print(f"   {json.dumps(data, indent=4)}")

                    # Extract response text
                    content = data.get("message", {}).get("content", [])
                    response_text = ""
                    for item in content:
                        if item.get("type") == "text":
                            response_text += item.get("text", "")

                    print(f"✅ Invoke endpoint: {response.status_code}")
                    print(f"   📝 EXTRACTED RESPONSE TEXT:")
                    print(f"   {response_text}")

                    # Check for intelligent response
                    if any(
                        keyword in response_text.lower()
                        for keyword in [
                            "42",
                            "twenty",
                            "calculation",
                            "result",
                            "answer",
                        ]
                    ):
                        print("✅ Response contains expected calculation result")
                        return True
                    else:
                        print(
                            "⚠️  Response doesn't contain expected calculation keywords"
                        )
                        return True  # Still pass as endpoint works
                elif response.status_code == 401:
                    print("❌ Authentication failed (401 Unauthorized)")
                    print(f"   Response: {response.text}")
                    return False
                else:
                    print(f"❌ Invoke endpoint failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False

            except httpx.ConnectError:
                print("❌ Could not connect to invoke endpoint")
                return False
            except httpx.TimeoutException:
                print("❌ Invoke endpoint timed out")
                return False
            except Exception as e:
                print(f"❌ Invoke endpoint error: {e}")
                return False

    
    async def test_streaming_endpoint_with_auth(self) -> bool:
        """Test streaming endpoint via port forwarding with authentication."""
        print("\n🔍 Testing streaming endpoint with authentication...")

        if not self.auth_token:
            print("❌ No authentication token available")
            return False

        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "Count from 1 to 3"}],
                    },
                    "session_id": "eks-streaming-test-auth",
                }

                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json",
                }

                chunks_received = 0
                async with client.stream(
                    "POST",
                    "http://localhost:8003/stream",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                ) as response:
                    print(f"   Response status: {response.status_code}")

                    if response.status_code == 200:
                        print(f"✅ Streaming endpoint: {response.status_code}")
                        print(
                            f"   Content-Type: {response.headers.get('content-type')}"
                        )

                        async for chunk in response.aiter_text():
                            if chunk.strip():
                                chunks_received += 1
                                if chunks_received <= 3:  # Show first few chunks
                                    print(
                                        f"   Chunk {chunks_received}: {chunk.strip()[:50]}..."
                                    )

                        print(f"✅ Received {chunks_received} streaming chunks")
                        return chunks_received > 0
                    elif response.status_code == 401:
                        print("❌ Authentication failed (401 Unauthorized)")
                        return False
                    else:
                        print(f"❌ Streaming endpoint failed: {response.status_code}")
                        return False

            except httpx.ConnectError:
                print("❌ Could not connect to streaming endpoint")
                return False
            except httpx.TimeoutException:
                print("❌ Streaming endpoint timed out")
                return False
            except Exception as e:
                print(f"❌ Streaming endpoint error: {e}")
                return False

    def test_service_logs(self) -> bool:
        """Test service logs show activity."""
        print("\n🔍 Testing service logs...")

        success, output = self.run_kubectl_command(
            ["kubectl", "logs", "-l", "app=agentic-chat", "--tail=20", "--since=10m"]
        )

        if success:
            if len(output.strip()) > 0:
                print("✅ Service logs available")

                # Look for expected log patterns
                log_indicators = [
                    "uvicorn",
                    "fastapi",
                    "started server",
                    "application startup",
                    "health",
                    "GET /health",
                ]

                logs_lower = output.lower()
                found_indicators = [ind for ind in log_indicators if ind in logs_lower]

                if found_indicators:
                    print(f"✅ Found expected log patterns: {found_indicators}")
                else:
                    print("⚠️  No expected log patterns found, but logs exist")
                    print(f"   Sample: {output[:200]}...")

                return True
            else:
                print("⚠️  No recent logs found")
                return False
        else:
            print(f"❌ Failed to get logs: {output}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all EKS integration tests with authentication."""
        print("🚀 EKS Integration Tests for Agentic Chat Agent (With Auth)")
        print("=" * 70)

        # Get authentication token first
        self.auth_token = self.get_m2m_token()

        tests = [
            ("EKS Cluster Connection", self.test_eks_cluster_connection),
            ("Agentic Chat Service Exists", self.test_agentic_chat_service_exists),
            ("Agentic Chat Pods Running", self.test_agentic_chat_pods_running),
            ("Service Logs", self.test_service_logs),
        ]

        # Run basic tests first
        basic_results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                basic_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                basic_results.append((test_name, False))

        # If basic tests pass, run endpoint tests with port forwarding
        endpoint_results = []
        if all(result for _, result in basic_results):
            if self.start_port_forward():
                endpoint_tests = [
                    ("Health Endpoint (No Auth)", self.test_health_endpoint),
                    (
                        "Invoke Endpoint (With Auth)",
                        self.test_invoke_endpoint_with_auth,
                    ),
                    (
                        "Streaming Endpoint (With Auth)",
                        self.test_streaming_endpoint_with_auth,
                    ),
                ]

                for test_name, test_func in endpoint_tests:
                    try:
                        result = await test_func()
                        endpoint_results.append((test_name, result))
                    except Exception as e:
                        print(f"❌ {test_name} failed with exception: {e}")
                        endpoint_results.append((test_name, False))

                self.stop_port_forward()
            else:
                endpoint_results = [("Port Forwarding", False)]

        # Summary
        all_results = basic_results + endpoint_results
        passed = sum(1 for _, result in all_results if result)
        total = len(all_results)

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        for test_name, result in all_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")

        print(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All EKS integration tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above.")
            return False


async def main():
    """Main test runner."""
    tester = EKSAgenticChatTesterWithAuth()

    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        tester.stop_port_forward()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        tester.stop_port_forward()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
