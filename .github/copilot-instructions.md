<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Home Assistant HACS Integration - HTTP Uptime Monitor

This is a Home Assistant HACS integration project for monitoring HTTP endpoint status codes.

## Project Guidelines

- This integration monitors multiple configurable HTTP endpoints
- Each endpoint can have configurable SSL verification settings
- Results are exposed as sensor entities with up/down attributes
- Follow Home Assistant integration development best practices
- Use async/await patterns for HTTP requests
- Implement proper error handling and logging
- Follow Home Assistant coding standards and conventions
- Configuration should be done via YAML or UI config flow
