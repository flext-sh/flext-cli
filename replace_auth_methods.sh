#!/bin/bash
# Script to replace all method implementations in auth.py with flext-auth delegation

cd /home/marlonsc/flext/flext-cli

# Use sed to replace method bodies with delegation calls
# This is a complex sed script that replaces everything between method signatures and the next method

sed -i '
/def [a-zA-Z_][a-zA-Z0-9_]*([^)]*) -> .*:/{
    # Store the method signature
    h
    # Read lines until next method definition or end of method
    :loop
    n
    /^def [a-zA-Z_][a-zA-Z0-9_]*([^)]*) -> .*:$/{
        # Next method found, stop and process current method
        b process
    }
    /^class /{
        # Class found, stop and process current method
        b process
    }
    $ {
        # End of file, process current method
        b process
    }
    b loop

    :process
    # Exchange hold space with pattern space to get method signature
    x
    # Extract method name
    s/def \([a-zA-Z_][a-zA-Z0-9_]*\).*/\1/
    # Create delegation call
    s/.*/        """\1 via flext-auth delegation."""\
        return self._auth.\1(/
    # Add parameters (this is simplified - would need more complex logic for real parameters)
    s/$/)/
    # Print the replacement
    p
    # Clear pattern space for next method
    s/.*//
    x
}' src/flext_cli/auth.py