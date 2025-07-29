"""Constants for the HTTP Uptime Monitor integration."""

DOMAIN = "http_uptime"

# Configuration keys
CONF_ENDPOINTS = "endpoints"
CONF_URL = "url"
CONF_NAME = "name"
CONF_VERIFY_SSL = "verify_ssl"
CONF_TIMEOUT = "timeout"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_METHOD = "method"
CONF_HEADERS = "headers"
CONF_EXPECTED_STATUS = "expected_status"

# Default values
DEFAULT_TIMEOUT = 10
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_METHOD = "GET"
DEFAULT_VERIFY_SSL = True
DEFAULT_EXPECTED_STATUS = [200]

# Attributes
ATTR_STATUS_CODE = "status_code"
ATTR_RESPONSE_TIME = "response_time"
ATTR_URL = "url"
ATTR_LAST_SUCCESS = "last_success"
ATTR_LAST_FAILURE = "last_failure"
ATTR_SSL_EXPIRES = "ssl_expires"
