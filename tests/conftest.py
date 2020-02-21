# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring

import sys

# We need to mock away dtls since this may segfault if not patched
sys.modules["dtls"] = __import__("mock_dtls")
