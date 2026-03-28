#!/usr/bin/env python3
"""
Test script to verify nanobot agent cron functionality.

This script tests the agent's ability to:
1. Create scheduled health checks using the cron tool
2. List scheduled jobs
3. Execute observability queries periodically

Requirements:
- Nanobot agent running on VM
- Flutter web client accessible
- Environment configured with LLM API key and nanobot endpoints
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx


class NanobotTester:
    """Test harness for nanobot agent capabilities."""

    def __init__(self, gateway_url: str = "http://localhost:18790"):
        """Initialize tester with nanobot gateway URL."""
        self.gateway_url = gateway_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def test_agent_tools(self) -> dict[str, Any]:
        """Test that agent has expected tools available."""
        results = {
            "test": "agent_tools",
            "status": "pending",
            "tools_found": [],
            "tools_missing": [],
        }

        try:
            # The gateway should expose agent tools via API
            # This assumes nanobot exposes an endpoint like /api/agent/tools
            response = await self.client.get(f"{self.gateway_url}/api/agent/tools")

            if response.status_code == 200:
                tools = response.json()
                expected_tools = [
                    "cron",
                    "mcp_lms_lms_health",
                    "mcp_obs_logs_search",
                    "mcp_obs_logs_error_count",
                    "mcp_obs_traces_list",
                    "mcp_obs_traces_get",
                ]

                tool_names = [t.get("name", "") for t in tools]

                for expected in expected_tools:
                    if expected in tool_names:
                        results["tools_found"].append(expected)
                    else:
                        results["tools_missing"].append(expected)

                results["status"] = "success" if not results["tools_missing"] else "partial"
            else:
                results["status"] = "failed"
                results["error"] = f"HTTP {response.status_code}"

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results

    async def test_cron_job_creation(self) -> dict[str, Any]:
        """Test creating a cron job via agent message."""
        results = {
            "test": "cron_job_creation",
            "status": "pending",
            "request": None,
            "response": None,
        }

        try:
            # Send message asking agent to create a health check job
            message = {
                "content": (
                    "Create a health check job for this session that runs every 5 minutes. "
                    "Each run should check for LMS backend errors in the last 5 minutes using the obs tools. "
                    "If there are errors, include the error count and most recent error message in a report. "
                    "Otherwise, confirm the system is healthy."
                )
            }

            results["request"] = message

            # Try posting to agent message endpoint
            response = await self.client.post(
                f"{self.gateway_url}/api/agent/message",
                json=message,
            )

            if response.status_code in (200, 201):
                results["status"] = "success"
                results["response"] = response.json()
            else:
                results["status"] = "failed"
                results["response"] = {
                    "status_code": response.status_code,
                    "text": response.text[:500],
                }

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results

    async def test_list_jobs(self) -> dict[str, Any]:
        """Test listing scheduled cron jobs."""
        results = {
            "test": "list_jobs",
            "status": "pending",
            "request": None,
            "response": None,
        }

        try:
            message = {"content": "List all scheduled cron jobs for this session."}
            results["request"] = message

            response = await self.client.post(
                f"{self.gateway_url}/api/agent/message",
                json=message,
            )

            if response.status_code in (200, 201):
                results["status"] = "success"
                results["response"] = response.json()
            else:
                results["status"] = "failed"
                results["response"] = {
                    "status_code": response.status_code,
                    "text": response.text[:500],
                }

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)

        return results

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all tests and return results."""
        print("🧪 Starting nanobot cron functionality tests...")
        print()

        results = {
            "timestamp": str(Path.ctime(Path(__file__))),
            "gateway_url": self.gateway_url,
            "tests": [],
        }

        # Test 1: Check available tools
        print("Test 1/3: Checking available agent tools...")
        tool_results = await self.test_agent_tools()
        results["tests"].append(tool_results)
        print(f"  Status: {tool_results['status']}")
        if tool_results["tools_found"]:
            print(f"  Found: {', '.join(tool_results['tools_found'][:3])}...")
        if tool_results["tools_missing"]:
            print(f"  Missing: {', '.join(tool_results['tools_missing'][:3])}...")
        print()

        # Test 2: Create cron job
        print("Test 2/3: Testing cron job creation...")
        cron_results = await self.test_cron_job_creation()
        results["tests"].append(cron_results)
        print(f"  Status: {cron_results['status']}")
        if cron_results.get("response"):
            content = cron_results["response"].get("content", "")
            print(f"  Agent response: {content[:100]}...")
        print()

        # Test 3: List jobs
        print("Test 3/3: Testing job listing...")
        list_results = await self.test_list_jobs()
        results["tests"].append(list_results)
        print(f"  Status: {list_results['status']}")
        if list_results.get("response"):
            content = list_results["response"].get("content", "")
            print(f"  Agent response: {content[:100]}...")
        print()

        # Summary
        passed = sum(1 for t in results["tests"] if t["status"] == "success")
        total = len(results["tests"])
        print(f"✅ Tests passed: {passed}/{total}")

        return results


async def main():
    """Run tests against nanobot agent."""
    gateway_url = os.environ.get("NANOBOT_GATEWAY_URL", "http://localhost:18790")

    tester = NanobotTester(gateway_url)

    try:
        results = await tester.run_all_tests()

        # Save results to file
        output_file = Path(__file__).parent.parent / "test-agent-cron-results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Test results saved to {output_file}")

        # Exit with appropriate code
        failed = sum(1 for t in results["tests"] if t["status"] != "success")
        return 0 if failed == 0 else 1

    finally:
        await tester.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
