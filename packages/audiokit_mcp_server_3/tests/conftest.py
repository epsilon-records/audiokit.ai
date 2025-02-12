import sys
from pathlib import Path


# Add the package directory to the Python path
package_dir = str(Path(__file__).parent.parent / "audiokit_mcp_server")
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)
