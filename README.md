# coreason-construct

**The Standard Library for Cognitive Architecture.**

[![CI/CD](https://github.com/CoReason-AI/coreason_construct/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/CoReason-AI/coreason_construct/actions/workflows/ci-cd.yml)
[![Docker](https://github.com/CoReason-AI/coreason_construct/actions/workflows/docker.yml/badge.svg)](https://github.com/CoReason-AI/coreason_construct/actions/workflows/docker.yml)
[![PyPI version](https://badge.fury.io/py/coreason_construct.svg)](https://badge.fury.io/py/coreason_construct)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/coreason_construct.svg)](https://pypi.org/project/coreason_construct/)
[![License](https://img.shields.io/badge/license-Prosperity%20Public%20License%203.0-blue.svg)](LICENSE)
[![codecov](https://codecov.io/gh/CoReason-AI/coreason_construct/branch/main/graph/badge.svg)](https://codecov.io/gh/CoReason-AI/coreason_construct)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

coreason-construct replaces ad-hoc prompt engineering with **Type-Driven Generation**. It provides a strictly typed library of Cognitive Components—Roles, Contexts, Logic Primitives, and Data Banks—assembled by the **Weaver** into optimized prompt configurations.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry (for development)

### Installation

```sh
pip install coreason-construct
```

Or with Poetry:

```sh
poetry add coreason-construct
```

### Quick Start

Assemble a prompt for Adverse Event extraction using a standardized Role and Few-Shot Data.

```python
from coreason_construct import Weaver
from coreason_construct.roles.library import SafetyScientist
from coreason_construct.data.library import AE_Examples
from coreason_construct.primitives.extract import ExtractionPrimitive
from coreason_construct.schemas.clinical import AdverseEvent

# 1. Initialize the Weaver
weaver = Weaver()

# 2. Add Components
weaver.add(SafetyScientist)  # Automatically injects HIPAA & GxP Contexts
weaver.add(AE_Examples)      # Injects Few-Shot examples for robust extraction

# 3. Add the Task (Primitive)
extractor = ExtractionPrimitive(
    name="AE_Extractor",
    schema=AdverseEvent
)
weaver.add(extractor)

# 4. Build the Prompt Configuration
user_input = "Patient reported mild nausea after taking the study drug."
config = weaver.build(user_input)

# The 'config' object is now ready to be sent to an LLM via instructor
print(config.system_message)
# Output includes:
# - Safety Scientist Persona
# - HIPAA/GxP Constraints
# - Few-Shot Examples (formatted JSON)
# - Extraction Instructions
```

## Architecture

- **Roles**: Standardized personas (e.g., `SafetyScientist`, `MedicalDirector`).
- **Contexts**: Injectable environment constraints (e.g., `HIPAA`, `StudyProtocol`).
- **Data**: Few-shot examples and dictionaries (e.g., `AE_Examples`).
- **Primitives**: Structured tasks defined by Pydantic schemas (e.g., `Extract`, `Classify`).
- **Weaver**: The engine that assembles components, resolves dependencies, and optimizes token usage.

## License

Proprietary and Dual-Licensed. See [LICENSE](LICENSE) for details.
