#!/usr/bin/env python3
"""
Simple SSE client to test weather streaming
"""

import asyncio
import aiohttp
import json
import sys

async def test_sse_streaming(stream_id: str):
    """Test SSE streaming for a weather stream"""
    
    print(f"🌤️  Testing SSE streaming for stream: {stream_id}")
    print("=" * 60)
    
    url = f"http://localhost:8100/weather/stream/{stream_id}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"❌ Failed to connect to SSE stream: {response.status}")
                    return
                
                print(f"✅ Connected to SSE stream at {url}")
                print("📡 Receiving weather updates... (Press Ctrl+C to stop)")
                print("-" * 60)
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            timestamp = data.get('timestamp', 'Unknown')
                            status = data.get('status', 'Unknown')
                            
                            if status == 'connected':
                                print(f"🔗 {timestamp}: Stream connected")
                            elif status == 'expired':
                                print(f"⏰ {timestamp}: Stream expired")
                                break
                            elif 'conditions' in data:
                                conditions = data['conditions']
                                if 'error' in conditions:
                                    print(f"❌ {timestamp}: Error - {conditions['error']}")
                                else:
                                    temp = conditions.get('temperature', 'N/A')
                                    temp_unit = conditions.get('temperature_unit', '')
                                    wind_speed = conditions.get('wind_speed', 'N/A')
                                    description = conditions.get('description', 'Unknown')
                                    print(f"🌡️  {timestamp}: {temp}{temp_unit}°F, Wind: {wind_speed} mph, {description}")
                            else:
                                print(f"📊 {timestamp}: {status}")
                                
                        except json.JSONDecodeError:
                            print(f"⚠️  Invalid JSON: {line}")
                        except Exception as e:
                            print(f"❌ Error processing data: {e}")
                            
    except KeyboardInterrupt:
        print("\n⏹️  SSE streaming stopped by user")
    except Exception as e:
        print(f"❌ SSE streaming error: {e}")

async def create_stream_and_test():
    """Create a stream and test SSE streaming"""
    
    # First create a stream
    print("🚀 Creating weather stream for SSE testing...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8100/weather/stream",
                json={
                    "latitude": 40.7128,  # New York City
                    "longitude": -74.0060,
                    "duration_minutes": 2  # Short duration for testing
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    stream_id = result.get("stream_id")
                    print(f"✅ Stream created: {stream_id}")
                    
                    # Wait a moment for stream to initialize
                    await asyncio.sleep(1)
                    
                    # Test SSE streaming
                    await test_sse_streaming(stream_id)
                else:
                    print(f"❌ Failed to create stream: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error creating stream: {e}")

def main():
    """Main function"""
    print("🌤️  Weather SSE Streaming Test")
    print("Make sure the weather server is running on localhost:8100")
    print()
    
    try:
        asyncio.run(create_stream_and_test())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    print("\n✨ SSE test completed!")

if __name__ == "__main__":
    main() 