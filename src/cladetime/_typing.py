"""Type aliases for this package."""

from pathlib import Path
from typing import TypeAlias, Union

from cloudpathlib import AnyPath, CloudPath

# Data types
# Pathlike: TypeAlias = Path | AnyPath | CloudPath
Pathlike: TypeAlias = Union["Path", "AnyPath", "CloudPath"]
