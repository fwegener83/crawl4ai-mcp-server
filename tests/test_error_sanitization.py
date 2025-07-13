"""Error message sanitization tests."""
import pytest
import re


class TestErrorMessageSanitization:
    """Test error message sanitization patterns."""
    
    @pytest.mark.parametrize("input_error,expected_patterns", [
        (
            "Database connection failed: postgresql://user:password@localhost:5432/db",
            {
                "should_contain": ["Database connection failed", "postgresql://", "localhost"],
                "should_not_contain": ["password", "user:password"]
            }
        ),
        (
            "MySQL error: mysql://admin:secret123@db.example.com:3306/production",
            {
                "should_contain": ["MySQL error", "mysql://", "db.example.com"],
                "should_not_contain": ["secret123", "admin:secret123"]
            }
        ),
        (
            "API authentication failed with key: sk-1234567890abcdef",
            {
                "should_contain": ["API authentication failed"],
                "should_not_contain": ["sk-1234567890abcdef"]
            }
        ),
        (
            "File not found: /etc/passwd",
            {
                "should_contain": ["File not found"],
                "should_not_contain": ["/etc/passwd"]
            }
        ),
        (
            "Windows error accessing C:\\Users\\Admin\\secret.txt",
            {
                "should_contain": ["Windows error accessing"],
                "should_not_contain": ["C:\\Users\\Admin\\secret.txt"]
            }
        ),
        (
            "AWS credentials invalid: AKIAIOSFODNN7EXAMPLE",
            {
                "should_contain": ["AWS credentials invalid"],
                "should_not_contain": ["AKIAIOSFODNN7EXAMPLE"]
            }
        ),
        (
            "JWT token expired: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            {
                "should_contain": ["JWT token"],
                "should_not_contain": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"]
            }
        ),
        (
            "Configuration error: SECRET_KEY=abcd1234efgh5678 not found",
            {
                "should_contain": ["Configuration error", "not found"],
                "should_not_contain": ["SECRET_KEY=abcd1234efgh5678", "abcd1234efgh5678"]
            }
        ),
    ])
    def test_error_message_sanitization(self, input_error, expected_patterns):
        """Test error message sanitization patterns."""
        # This test will FAIL initially (Red phase) - sanitize_error_message doesn't exist yet
        from tools.error_sanitizer import sanitize_error_message
        
        sanitized = sanitize_error_message(input_error)
        
        # Verify expected content is preserved
        for content in expected_patterns["should_contain"]:
            assert content in sanitized, f"Expected content '{content}' not found in sanitized message: {sanitized}"
        
        # Verify sensitive content is removed
        for sensitive in expected_patterns["should_not_contain"]:
            assert sensitive not in sanitized, f"Sensitive content '{sensitive}' found in sanitized message: {sanitized}"

    def test_sanitization_preserves_useful_info(self):
        """Test that sanitization doesn't over-sanitize."""
        from tools.error_sanitizer import sanitize_error_message
        
        error = "Connection failed to https://example.com:443 with timeout after 30 seconds"
        sanitized = sanitize_error_message(error)
        
        # Should preserve useful debugging information
        assert "Connection failed" in sanitized
        assert "example.com" in sanitized
        assert "timeout" in sanitized
        assert "30 seconds" in sanitized

    def test_sanitization_handles_empty_and_none(self):
        """Test sanitization handles edge cases."""
        from tools.error_sanitizer import sanitize_error_message
        
        # Test empty string
        assert sanitize_error_message("") == ""
        
        # Test None
        assert sanitize_error_message(None) == ""
        
        # Test whitespace-only
        assert sanitize_error_message("   ") == "   "

    def test_sanitization_comprehensive_patterns(self):
        """Test comprehensive sanitization pattern coverage."""
        from tools.error_sanitizer import sanitize_error_message
        
        test_cases = [
            "postgresql://user:secret@db.com/prod",
            "mysql://admin:password123@localhost:3306",
            "API_KEY=sk-abcd1234efgh5678 failed", 
            "SECRET_TOKEN=abc123def456 invalid",
            "Error in /etc/passwd access",
            "Failed C:\\Users\\Admin\\secret.txt",
            "AWS key AKIAIOSFODNN7EXAMPLE leaked",
            "Password: mySecretPass123 incorrect",
            "ssh://user:pass@server.com connection failed",
        ]
        
        for case in test_cases:
            sanitized = sanitize_error_message(case)
            
            # Verify no common sensitive patterns remain (excluding [REDACTED])
            sensitive_patterns = [
                r'password[s]?[=:\s]+[\'"]?(?!\[REDACTED\])[^\s\'"]{4,}',
                r'secret[s]?[=:\s]+[\'"]?(?!\[REDACTED\])[^\s\'"]{4,}',
                r'sk-[a-zA-Z0-9]+(?<!\[REDACTED\])',
                r'AKIA[0-9A-Z]{16}(?<!\[REDACTED\])',
                r'://[^:]+:[^@]+@(?!\[REDACTED\])',
                r'/etc/[^\s]+(?<!\[REDACTED\])',
                r'C:\\[^\s]+\\[^\s]+(?<!\[REDACTED\])',
            ]
            
            for pattern in sensitive_patterns:
                matches = re.search(pattern, sanitized, re.IGNORECASE)
                assert not matches, f"Sensitive pattern '{pattern}' found in sanitized text: {sanitized}"

    def test_sanitization_multiple_sensitive_items(self):
        """Test sanitization handles multiple sensitive items in one message."""
        from tools.error_sanitizer import sanitize_error_message
        
        complex_error = (
            "Database connection postgresql://user:password@localhost failed. "
            "Tried API key sk-1234567890abcdef but got error from /etc/config/secret.conf. "
            "AWS credentials AKIAIOSFODNN7EXAMPLE also invalid."
        )
        
        sanitized = sanitize_error_message(complex_error)
        
        # Should contain useful info
        assert "Database connection" in sanitized
        assert "postgresql://" in sanitized
        assert "localhost" in sanitized
        assert "failed" in sanitized
        assert "API key" in sanitized
        assert "AWS credentials" in sanitized
        assert "invalid" in sanitized
        
        # Should not contain sensitive info
        assert "password" not in sanitized
        assert "user:password" not in sanitized
        assert "sk-1234567890abcdef" not in sanitized
        assert "/etc/config/secret.conf" not in sanitized
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized

    def test_redaction_marker_consistency(self):
        """Test that redaction markers are consistent."""
        from tools.error_sanitizer import sanitize_error_message
        
        errors_with_secrets = [
            "Password: secret123 failed",
            "API key sk-abcd1234 invalid",
            "File /etc/passwd not found"
        ]
        
        for error in errors_with_secrets:
            sanitized = sanitize_error_message(error)
            # Should contain redaction marker
            assert "[REDACTED]" in sanitized


class TestErrorSanitizerModule:
    """Test error sanitizer module structure and functionality."""
    
    def test_error_sanitizer_module_exists(self):
        """Test that error sanitizer module can be imported."""
        # This test will FAIL initially - module doesn't exist yet
        import tools.error_sanitizer
        assert tools.error_sanitizer is not None

    def test_sanitize_error_message_function_exists(self):
        """Test that sanitize_error_message function exists."""
        from tools.error_sanitizer import sanitize_error_message
        assert callable(sanitize_error_message)

    def test_sanitizer_has_pattern_definitions(self):
        """Test that sanitizer has pattern definitions."""
        from tools.error_sanitizer import ErrorMessageSanitizer
        
        sanitizer = ErrorMessageSanitizer()
        
        # Should have pattern definitions
        assert hasattr(sanitizer, 'SENSITIVE_PATTERNS')
        assert isinstance(sanitizer.SENSITIVE_PATTERNS, dict)
        assert len(sanitizer.SENSITIVE_PATTERNS) > 0

    def test_sanitizer_performance(self):
        """Test that sanitization is performant."""
        import time
        from tools.error_sanitizer import sanitize_error_message
        
        # Test with a complex error message
        complex_error = (
            "Database postgresql://user:password@localhost:5432 failed. "
            "API key sk-1234567890abcdef rejected. "
            "Config file /etc/app/secret.conf missing. "
            "AWS key AKIAIOSFODNN7EXAMPLE invalid. "
        ) * 10  # Repeat 10 times to make it larger
        
        start_time = time.perf_counter()
        
        # Run sanitization 100 times
        for _ in range(100):
            sanitized = sanitize_error_message(complex_error)
            assert "[REDACTED]" in sanitized
        
        duration = time.perf_counter() - start_time
        
        # Should be very fast (under 100ms for 100 operations)
        assert duration < 0.1, f"Sanitization too slow: {duration:.4f}s for 100 operations"

    def test_sanitizer_pattern_validation(self):
        """Test sanitizer pattern validation."""
        from tools.error_sanitizer import ErrorMessageSanitizer
        
        sanitizer = ErrorMessageSanitizer()
        
        # Test that patterns are compiled regex objects
        for pattern_name, pattern in sanitizer.SENSITIVE_PATTERNS.items():
            assert hasattr(pattern, 'search'), f"Pattern {pattern_name} is not a compiled regex"
            assert hasattr(pattern, 'sub'), f"Pattern {pattern_name} is not a compiled regex"


class TestSanitizationValidation:
    """Test sanitization validation helper functions."""
    
    def test_validate_sanitization_function(self):
        """Test that validation function exists and works."""
        # This test will FAIL initially - validation function doesn't exist yet
        from tools.error_sanitizer import validate_sanitization
        
        original = "Password: secret123 failed"
        sanitized = "Password: [REDACTED] failed"
        
        # Should detect no leaks
        leaks = validate_sanitization(original, sanitized)
        assert isinstance(leaks, list)
        assert len(leaks) == 0

    def test_validate_sanitization_detects_leaks(self):
        """Test that validation detects sensitive data leaks."""
        from tools.error_sanitizer import validate_sanitization
        
        original = "Password: secret123 failed"
        poorly_sanitized = "Password: secret123 failed"  # Not sanitized
        
        # Should detect leaks
        leaks = validate_sanitization(original, poorly_sanitized)
        assert len(leaks) > 0
        assert any("password" in leak.lower() for leak in leaks)

    def test_validation_comprehensive_patterns(self):
        """Test validation against comprehensive sensitive patterns."""
        from tools.error_sanitizer import validate_sanitization
        
        test_cases = [
            ("sk-1234567890abcdef", "sk-1234567890abcdef"),  # API key leak
            ("AKIAIOSFODNN7EXAMPLE", "AKIAIOSFODNN7EXAMPLE"),  # AWS key leak
            ("/etc/passwd", "/etc/passwd"),  # System path leak
            ("password123", "password123"),  # Password leak
        ]
        
        for original, leaked in test_cases:
            leaks = validate_sanitization(original, leaked)
            assert len(leaks) > 0, f"Should detect leak in: {leaked}"

    def test_validation_performance(self):
        """Test validation performance."""
        import time
        from tools.error_sanitizer import validate_sanitization
        
        original = "Multiple secrets: password123, sk-abcd1234, /etc/passwd, AKIATEST1234"
        sanitized = "Multiple secrets: [REDACTED], [REDACTED], [REDACTED], [REDACTED]"
        
        start_time = time.perf_counter()
        
        # Run validation 1000 times
        for _ in range(1000):
            leaks = validate_sanitization(original, sanitized)
            assert len(leaks) == 0
        
        duration = time.perf_counter() - start_time
        
        # Should be fast (under 100ms for 1000 operations)
        assert duration < 0.1, f"Validation too slow: {duration:.4f}s for 1000 operations"


class TestSanitizationIntegration:
    """Test sanitization integration scenarios."""
    
    def test_sanitization_with_real_error_types(self):
        """Test sanitization with real Python exception types."""
        from tools.error_sanitizer import sanitize_error_message
        
        # Test with actual exception objects
        exceptions = [
            ConnectionError("postgresql://user:password@localhost connection failed"),
            ValueError("Invalid API key: sk-1234567890abcdef"),
            FileNotFoundError("/etc/passwd not found"),
            RuntimeError("Configuration SECRET_KEY=abc123 missing"),
        ]
        
        for exc in exceptions:
            error_str = str(exc)
            sanitized = sanitize_error_message(error_str)
            
            # Should not contain sensitive info
            assert "password" not in sanitized
            assert "sk-1234567890abcdef" not in sanitized
            assert "/etc/passwd" not in sanitized
            assert "SECRET_KEY=abc123" not in sanitized
            
            # Should contain useful error type info
            assert len(sanitized) > 0
            assert "[REDACTED]" in sanitized

    def test_sanitization_with_nested_errors(self):
        """Test sanitization with nested/chained errors."""
        from tools.error_sanitizer import sanitize_error_message
        
        nested_error = (
            "Primary error: Database connection failed postgresql://user:password@localhost. "
            "Secondary error: API fallback failed with key sk-1234567890abcdef. "
            "Tertiary error: Local config /etc/app/secret.conf not accessible."
        )
        
        sanitized = sanitize_error_message(nested_error)
        
        # Should preserve error structure
        assert "Primary error" in sanitized
        assert "Secondary error" in sanitized  
        assert "Tertiary error" in sanitized
        assert "Database connection failed" in sanitized
        assert "API fallback failed" in sanitized
        assert "not accessible" in sanitized
        
        # Should sanitize all sensitive parts
        assert "password" not in sanitized
        assert "sk-1234567890abcdef" not in sanitized
        assert "/etc/app/secret.conf" not in sanitized

    def test_sanitization_preserves_exception_types(self):
        """Test that sanitization preserves exception type information."""
        from tools.error_sanitizer import sanitize_error_message
        
        errors_with_types = [
            "ConnectionError: postgresql://user:password@localhost failed",
            "ValueError: Invalid secret key sk-1234567890abcdef",
            "FileNotFoundError: /etc/passwd not found",
            "PermissionError: Cannot access C:\\Windows\\System32\\secret.dll",
        ]
        
        for error in errors_with_types:
            sanitized = sanitize_error_message(error)
            
            # Should preserve exception type
            error_type = error.split(":")[0]
            assert error_type in sanitized
            
            # Should contain redaction
            assert "[REDACTED]" in sanitized