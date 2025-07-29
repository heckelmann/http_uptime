# HTTP Uptime Monitor for Home Assistant

A Home Assistant HACS integration for monitoring HTTP endpoint status codes with configurable SSL verification and custom headers support.

## Features

- Monitor multiple HTTP endpoints
- Configurable SSL certificate verification
- Custom HTTP methods (GET, POST, PUT, DELETE, HEAD, OPTIONS)
- Configurable timeout and update intervals
- Custom headers support
- Expected status code validation
- SSL certificate expiration monitoring
- Response time tracking
- Up/Down status as sensor entities

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/http_uptime` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

The integration can be configured through the Home Assistant UI:

1. Go to Configuration → Integrations
2. Click the "+" button to add a new integration
3. Search for "HTTP Uptime Monitor"
4. Fill in the configuration form:
   - **Name**: A friendly name for this endpoint
   - **URL**: The HTTP(S) endpoint to monitor
   - **Method**: HTTP method to use (default: GET)
   - **Timeout**: Request timeout in seconds (default: 10)
   - **Update Interval**: How often to check the endpoint in seconds (default: 60)
   - **Verify SSL**: Whether to verify SSL certificates (default: true)
   - **Expected Status**: Comma-separated list of expected HTTP status codes (default: 200)
   - **Headers**: Custom headers, one per line in "Key: Value" format

## Sensor Attributes

Each endpoint creates a sensor with the following attributes:

- **State**: "up" or "down" based on response
- **status_code**: HTTP status code returned
- **response_time**: Response time in milliseconds
- **url**: The monitored URL
- **last_success**: Timestamp of last successful check
- **last_failure**: Timestamp of last failed check
- **ssl_expires**: SSL certificate expiration date (for HTTPS endpoints)

## Examples

### Basic HTTP Monitoring
```yaml
# Configuration via UI
Name: My Website
URL: https://example.com
Method: GET
Expected Status: 200
```

### API Endpoint with Custom Headers
```yaml
# Configuration via UI
Name: API Health Check
URL: https://api.example.com/health
Method: GET
Headers:
Authorization: Bearer your-token-here
Content-Type: application/json
Expected Status: 200,204
```

### Internal Service without SSL Verification
```yaml
# Configuration via UI
Name: Internal Service
URL: https://internal.service.local:8443/status
Verify SSL: false
Expected Status: 200
```

## Troubleshooting

- Check the Home Assistant logs for any error messages
- Ensure the endpoint is accessible from your Home Assistant instance
- Verify SSL settings if monitoring HTTPS endpoints
- Check that expected status codes match what the endpoint returns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues, please open an issue on the GitHub repository.
