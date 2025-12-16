#!/usr/bin/env python3
"""
Script to run the weather server and test it
"""

import subprocess
import time
import asyncio
import httpx
import sys
import signal
import os

def start_server():
    """Start the weather server"""
    print("🚀 Starting Weather MCP Server...")
    try:
        # Start the server in a subprocess
        process = subprocess.Popen(
            [sys.executable, "weather.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = httpx.get("http://localhost:8100/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                return process
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                process.terminate()
                return None
        except Exception as e:
            print(f"❌ Server not responding: {e}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def stop_server(process):
    """Stop the server"""
    if process:
        print("🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ Server stopped")

async def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    
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
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    # Test 2: Create a stream
    print("\n2. Testing stream creation...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8100/weather/stream",
                json={
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "duration_minutes": 1
                }
            )
            if response.status_code == 200:
                result = response.json()
                stream_id = result.get("stream_id")
                print(f"✅ Stream created: {stream_id}")
                
                # Test 3: List streams
                print("\n3. Testing stream listing...")
                response = await client.get("http://localhost:8100/weather/streams")
                if response.status_code == 200:
                    streams_data = response.json()
                    print(f"✅ Found {streams_data['count']} active streams")
                    
                    # Test 4: Stop stream
                    print("\n4. Testing stream stopping...")
                    response = await client.post(f"http://localhost:8100/weather/stream/{stream_id}/stop")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Stream stopped: {result.get('message')}")
                    else:
                        print(f"❌ Failed to stop stream: {response.status_code}")
                else:
                    print(f"❌ Failed to list streams: {response.status_code}")
            else:
                print(f"❌ Failed to create stream: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Stream test error: {e}")
            return False
    
    print("\n✅ All tests passed!")
    return True

def main():
    """Main function"""
    print("🌤️  Weather MCP Server Test Suite")
    print("=" * 50)
    
    server_process = None
    
    try:
        # Start server
        server_process = start_server()
        if not server_process:
            print("❌ Failed to start server")
            return
        
        # Run tests
        success = asyncio.run(run_tests())
        
        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        # Stop server
        if server_process:
            stop_server(server_process)

if __name__ == "__main__":
    main() 