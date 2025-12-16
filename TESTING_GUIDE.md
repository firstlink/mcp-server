# Weather MCP Server Testing Guide

## Overview
This guide explains how to test the improved weather MCP server and troubleshoot common issues.

## Quick Start

### 1. Start the Server
```bash
python weather.py
```

The server will start on `http://localhost:8100`

### 2. Run Basic Tests
```bash
python test_weather_stream.py
```

### 3. Test SSE Streaming
```bash
python test_sse_client.py
```

### 4. Run Complete Test Suite
```bash
python run_and_test.py
```

## Available Endpoints

### Health Check
```bash
curl http://localhost:8100/health
```
**Response:**
```json
{
  "message": "MCP SSE server is running!",
  "active_streams": 0,
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Create Weather Stream
```bash
curl -X POST http://localhost:8100/weather/stream \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "duration_minutes": 60
  }'
```
**Response:**
```json
{
  "status": "success",
  "stream_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Weather stream started with ID: 550e8400-e29b-41d4-a716-446655440000. Duration: 60 minutes"
}
```

### List Active Streams
```bash
curl http://localhost:8100/weather/streams
```
**Response:**
```json
{
  "streams": {
    "550e8400-e29b-41d4-a716-446655440000": {
      "location": {"latitude": 40.7128, "longitude": -74.0060},
      "created_at": "2024-01-15T10:30:00.123456",
      "last_update": "2024-01-15T10:30:30.123456",
      "active": true
    }
  },
  "count": 1
}
```

### Stop Stream
```bash
curl -X POST http://localhost:8100/weather/stream/550e8400-e29b-41d4-a716-446655440000/stop
```
**Response:**
```json
{
  "status": "success",
  "message": "Stream 550e8400-e29b-41d4-a716-446655440000 stopped"
}
```

### SSE Streaming
```bash
curl -N http://localhost:8100/weather/stream/550e8400-e29b-41d4-a716-446655440000
```
**Response (Server-Sent Events):**
```
data: {"status": "connected", "stream_id": "550e8400-e29b-41d4-a716-446655440000"}

data: {"timestamp": "2024-01-15T10:30:30.123456", "stream_id": "550e8400-e29b-41d4-a716-446655440000", "location": {"latitude": 40.7128, "longitude": -74.0060}, "conditions": {"temperature": 72, "temperature_unit": "F", "wind_speed": 8, "wind_direction": 180, "relative_humidity": 65, "description": "Partly cloudy"}, "status": "active"}

data: {"timestamp": "2024-01-15T10:31:00.123456", "stream_id": "550e8400-e29b-41d4-a716-446655440000", "location": {"latitude": 40.7128, "longitude": -74.0060}, "conditions": {"temperature": 73, "temperature_unit": "F", "wind_speed": 9, "wind_direction": 185, "relative_humidity": 64, "description": "Partly cloudy"}, "status": "active"}
```

## MCP Tools

### Get Forecast
```bash
curl -X POST http://localhost:8100/messages \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Start Weather Stream (MCP Tool)
```bash
curl -X POST http://localhost:8100/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "start_weather_stream",
      "arguments": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "duration_minutes": 60
      }
    }
  }'
```

## JavaScript SSE Client Example

```javascript
// Connect to weather stream
const eventSource = new EventSource('/weather/stream/550e8400-e29b-41d4-a716-446655440000');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Weather update:', data);
    
    if (data.status === 'connected') {
        console.log('Stream connected');
    } else if (data.status === 'expired') {
        console.log('Stream expired');
        eventSource.close();
    } else if (data.conditions) {
        const conditions = data.conditions;
        console.log(`Temperature: ${conditions.temperature}${conditions.temperature_unit}°F`);
        console.log(`Wind: ${conditions.wind_speed} mph ${conditions.wind_direction}°`);
        console.log(`Description: ${conditions.description}`);
    }
};

eventSource.onerror = function(event) {
    console.error('SSE error:', event);
    eventSource.close();
};
```

## Troubleshooting

### Common Issues

#### 1. Server Won't Start
**Error:** `Address already in use`
**Solution:** 
```bash
# Find and kill process using port 8100
lsof -ti:8100 | xargs kill -9
# Or use a different port
python weather.py --port 8101
```

#### 2. Connection Refused
**Error:** `Connection refused`
**Solution:**
- Make sure the server is running: `python weather.py`
- Check if the port is correct: `http://localhost:8100`
- Verify no firewall is blocking the connection

#### 3. Weather Data Not Available
**Error:** `Unable to fetch forecast data for this location`
**Solution:**
- Check if the coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)
- Verify internet connection
- The NWS API only works for US locations

#### 4. SSE Stream Not Working
**Error:** `Stream ID not found`
**Solution:**
- Make sure the stream was created successfully
- Check if the stream has expired
- Verify the stream ID is correct

#### 5. MCP Tools Not Responding
**Error:** `Method not found`
**Solution:**
- Check if the tool name is correct
- Verify the JSON-RPC format
- Make sure the server is using the correct MCP app

### Debug Mode

To run the server with debug logging:
```bash
python weather.py --log-level debug
```

### Testing Different Locations

```bash
# New York City
curl -X POST http://localhost:8100/weather/stream \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "duration_minutes": 5}'

# Los Angeles
curl -X POST http://localhost:8100/weather/stream \
  -H "Content-Type: application/json" \
  -d '{"latitude": 34.0522, "longitude": -118.2437, "duration_minutes": 5}'

# Chicago
curl -X POST http://localhost:8100/weather/stream \
  -H "Content-Type: application/json" \
  -d '{"latitude": 41.8781, "longitude": -87.6298, "duration_minutes": 5}'
```

## Performance Testing

### Load Testing
```bash
# Test multiple concurrent streams
for i in {1..10}; do
  curl -X POST http://localhost:8100/weather/stream \
    -H "Content-Type: application/json" \
    -d "{\"latitude\": 40.7128, \"longitude\": -74.0060, \"duration_minutes\": 1}" &
done
wait
```

### Memory Usage
```bash
# Monitor memory usage
ps aux | grep weather.py
```

## Integration Testing

### With MCP Client
```python
from mcp.client.sse import sse_client
from mcp import ClientSession

async def test_mcp_client():
    async with sse_client(url="http://localhost:8100/sse") as (in_stream, out_stream):
        async with ClientSession(in_stream, out_stream) as session:
            # Initialize
            info = await session.initialize()
            print(f"Connected to {info.serverInfo.name}")
            
            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Call forecast tool
            result = await session.call_tool("get_forecast", {
                "latitude": 40.7128,
                "longitude": -74.0060
            })
            print(f"Forecast: {result.content}")

# Run the test
import asyncio
asyncio.run(test_mcp_client())
```

## Expected Test Results

### Successful Test Run
```
🌤️  Testing Weather MCP Server
==================================================

1. Testing health endpoint...
✅ Health check passed: MCP SSE server is running!
   Active streams: 0

2. Creating weather stream...
✅ Weather stream created successfully: 550e8400-e29b-41d4-a716-446655440000
   Message: Weather stream started with ID: 550e8400-e29b-41d4-a716-446655440000. Duration: 5 minutes

3. Testing stream management for stream: 550e8400...
   Listing active streams...
   ✅ Found 1 active streams
      Stream: 550e8400... at {'latitude': 40.7128, 'longitude': -74.006}
   Testing SSE streaming...
   (This would require a proper SSE client implementation)
   Stream endpoint: GET /weather/stream/550e8400-e29b-41d4-a716-446655440000
   Stopping stream...
   ✅ Stream stopped successfully: Stream 550e8400-e29b-41d4-a716-446655440000 stopped

4. Testing MCP tools...
✅ Forecast tool call successful
   Result: Tonight: Temperature: 45°F Wind: 5 mph NW Forecast: Clear skies with light winds...

✨ Tests completed!
```

## Next Steps

1. **Production Deployment**: Add authentication, rate limiting, and monitoring
2. **Caching**: Implement Redis caching for weather data
3. **Multiple Providers**: Add fallback weather data sources
4. **WebSocket Support**: Add real-time bidirectional communication
5. **Metrics**: Add Prometheus metrics collection
6. **Documentation**: Generate API documentation with OpenAPI/Swagger 