#!/usr/bin/env python3
"""
Test script for the improved weather MCP server
"""

import asyncio
import httpx
import json
from typing import AsyncGenerator

async def test_weather_stream():
    """Test the weather streaming functionality"""
    
    # Test coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060
    
    print("🌤️  Testing Weather MCP Server")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8100/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data['message']}")
                print(f"   Active streams: {health_data['active_streams']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    # Test 2: Create a weather stream
    print("\n2. Creating weather stream...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8100/weather/stream",
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "duration_minutes": 5  # Short duration for testing
                }
            )
            if response.status_code == 200:
                result = response.json()
                stream_id = result.get("stream_id")
                print(f"✅ Weather stream created successfully: {stream_id}")
                print(f"   Message: {result.get('message')}")
                
                # Store stream_id for later tests
                return stream_id
            else:
                print(f"❌ Failed to create stream: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Stream creation error: {e}")
    
    return None

async def test_stream_management(stream_id: str):
    """Test stream management functionality"""
    if not stream_id:
        print("❌ No stream ID available for testing")
        return
    
    print(f"\n3. Testing stream management for stream: {stream_id[:8]}...")
    
    # Test 3: List active streams
    print("   Listing active streams...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8100/weather/streams")
            if response.status_code == 200:
                streams_data = response.json()
                print(f"   ✅ Found {streams_data['count']} active streams")
                for sid, config in streams_data['streams'].items():
                    print(f"      Stream: {sid[:8]}... at {config['location']}")
            else:
                print(f"   ❌ Failed to list streams: {response.status_code}")
        except Exception as e:
            print(f"   ❌ List streams error: {e}")
    
    # Test 4: Test SSE streaming (simplified)
    print("   Testing SSE streaming...")
    print("   (This would require a proper SSE client implementation)")
    print(f"   Stream endpoint: GET /weather/stream/{stream_id}")
    
    # Test 5: Stop the stream
    print("   Stopping stream...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"http://localhost:8100/weather/stream/{stream_id}/stop")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Stream stopped successfully: {result.get('message')}")
            else:
                print(f"   ❌ Failed to stop stream: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Stop stream error: {e}")

async def test_mcp_tools():
    """Test MCP tools via HTTP"""
    
    print("\n4. Testing MCP tools...")
    
    # Test forecast tool via MCP messages endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8100/messages/",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "get_forecast",
                        "arguments": {
                            "latitude": 40.7128,
                            "longitude": -74.0060
                        }
                    }
                },
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                print("✅ Forecast tool call successful")
                print(f"   Result: {result.get('result', {}).get('content', '')[:100]}...")
            else:
                print(f"❌ Forecast tool failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Forecast tool error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Weather MCP Server Tests")
    print("Make sure the server is running on localhost:8100")
    print()
    
    try:
        # Test 1 & 2: Health check and stream creation
        stream_id = asyncio.run(test_weather_stream())
        
        # Test 3: Stream management
        asyncio.run(test_stream_management(stream_id))
        
        # Test 4: MCP tools
        asyncio.run(test_mcp_tools())
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    print("\n✨ Tests completed!")

if __name__ == "__main__":
    main() 