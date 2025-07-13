"""Error message sanitization for security."""
import re
from typing import List, Dict, Pattern, Optional


class ErrorMessageSanitizer:
    """Comprehensive error message sanitization for security."""
    
    # Compiled regex patterns for performance
    SENSITIVE_PATTERNS: Dict[str, Pattern] = {
        # Password patterns
        'passwords': re.compile(
            r'(?i)(password[s]?[=:\s]+[\'"]?)([^\s\'"]{4,})',
            re.IGNORECASE
        ),
        
        # API keys and tokens (including sk- pattern)
        'api_keys': re.compile(
            r'(?i)(api[_-]?key[s]?[=:\s]+[\'"]?)([a-zA-Z0-9]{20,})',
            re.IGNORECASE
        ),
        
        # Specific sk- pattern for API keys
        'sk_keys': re.compile(
            r'(sk-[a-zA-Z0-9]+)',
            re.IGNORECASE
        ),
        
        # Generic secrets
        'secrets': re.compile(
            r'(?i)(secret[s]?[_-]?[a-z]*[=:\s]+[\'"]?)([a-zA-Z0-9]{8,})',
            re.IGNORECASE
        ),
        
        # Database connection strings
        'db_connections': re.compile(
            r'(postgresql://|mysql://|mongodb://|redis://)([^@/\s]+@)?([^\s/]+)',
            re.IGNORECASE
        ),
        
        # System paths (Unix)
        'unix_paths': re.compile(
            r'(/(?:etc|var|home|root|usr)/[^\s]*)',
            re.IGNORECASE
        ),
        
        # System paths (Windows)
        'windows_paths': re.compile(
            r'([C-Z]:\\(?:Windows|Users|Program Files)[^\s]*)',
            re.IGNORECASE
        ),
        
        # IP addresses with credentials
        'ip_credentials': re.compile(
            r'(https?://)([^@/]+@)(\d+\.\d+\.\d+\.\d+)',
            re.IGNORECASE
        ),
        
        # AWS keys
        'aws_keys': re.compile(
            r'(AKIA[0-9A-Z]{16})',
            re.IGNORECASE
        ),
        
        # JWT tokens
        'jwt_tokens': re.compile(
            r'(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})',
            re.IGNORECASE
        ),
        
        # SSH URLs with credentials
        'ssh_credentials': re.compile(
            r'(ssh://|sftp://)([^@/]+@)([^\s/]+)',
            re.IGNORECASE
        ),
        
        # Generic key=value secrets
        'key_value_secrets': re.compile(
            r'([A-Z_]*(?:KEY|SECRET|TOKEN|PASS)[=:\s]+)([a-zA-Z0-9_-]{6,})',
            re.IGNORECASE
        ),
    }
    
    @classmethod
    def sanitize_error_message(cls, message: str, replacement: str = "[REDACTED]") -> str:
        """
        Sanitize error message by removing sensitive information.
        
        Args:
            message: Original error message
            replacement: String to replace sensitive info with
            
        Returns:
            Sanitized error message
        """
        if not message:
            return message or ""
            
        sanitized = message
        
        for pattern_name, pattern in cls.SENSITIVE_PATTERNS.items():
            if pattern_name in ['passwords', 'api_keys', 'secrets', 'key_value_secrets']:
                # Keep the prefix, replace the value
                sanitized = pattern.sub(rf'\1{replacement}', sanitized)
            elif pattern_name == 'db_connections':
                # Replace credentials but keep protocol and host
                sanitized = pattern.sub(rf'\1{replacement}@\3', sanitized)
            elif pattern_name == 'ip_credentials':
                # Keep protocol, remove credentials, keep IP
                sanitized = pattern.sub(rf'\1{replacement}@\3', sanitized)
            elif pattern_name == 'ssh_credentials':
                # Keep protocol, remove credentials, keep host
                sanitized = pattern.sub(rf'\1{replacement}@\3', sanitized)
            elif pattern_name in ['sk_keys', 'aws_keys', 'jwt_tokens']:
                # Replace entire key/token
                sanitized = pattern.sub(replacement, sanitized)
            else:
                # Replace entire match
                sanitized = pattern.sub(replacement, sanitized)
        
        return sanitized
    
    @classmethod
    def validate_sanitization(cls, original: str, sanitized: str) -> List[str]:
        """
        Validate that sanitization was effective.
        
        Args:
            original: Original error message
            sanitized: Sanitized error message
            
        Returns:
            List of potential leaks found
        """
        leaks = []
        
        # Check for common sensitive patterns (excluding redacted content)
        sensitive_indicators = [
            r'password[s]?[=:\s]+[\'"]?(?!\[REDACTED\])[^\s\'"]{4,}',
            r'api[_-]?key[s]?[=:\s]+[\'"]?(?!\[REDACTED\])[a-zA-Z0-9]{20,}',
            r'secret[s]?[=:\s]+[\'"]?(?!\[REDACTED\])[a-zA-Z0-9]{8,}',
            r'/(?:etc|var|home|root)/[^\s]*(?<!\[REDACTED\])',
            r'[C-Z]:\\(?:Windows|Users)[^\s]*(?<!\[REDACTED\])',
            r'AKIA[0-9A-Z]{16}(?<!\[REDACTED\])',
            r'sk-[a-zA-Z0-9]+(?<!\[REDACTED\])',
            r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+(?<!\[REDACTED\])',
            r'://[^:]+:[^@]+@(?!\[REDACTED\])',
            r'password123|secret123|admin123',  # Common passwords
            r'[A-Z_]*(?:KEY|SECRET|TOKEN|PASS)[=:\s]+(?!\[REDACTED\])[a-zA-Z0-9_-]{6,}',
        ]
        
        for pattern in sensitive_indicators:
            if re.search(pattern, sanitized, re.IGNORECASE):
                leaks.append(f"Potential leak matching pattern: {pattern}")
        
        return leaks


# Convenience function for simple usage
def sanitize_error_message(message: str, replacement: str = "[REDACTED]") -> str:
    """
    Sanitize error message by removing sensitive information.
    
    Args:
        message: Original error message
        replacement: String to replace sensitive info with
        
    Returns:
        Sanitized error message
    """
    return ErrorMessageSanitizer.sanitize_error_message(message, replacement)


def validate_sanitization(original: str, sanitized: str) -> List[str]:
    """
    Validate that sanitization was effective.
    
    Args:
        original: Original error message
        sanitized: Sanitized error message
        
    Returns:
        List of potential leaks found
    """
    return ErrorMessageSanitizer.validate_sanitization(original, sanitized)