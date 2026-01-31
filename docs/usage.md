# Usage Guide

This guide provides a detailed overview of the `coreason-construct` library, explaining how to use its components to build structured, type-safe prompts for LLMs.

## Overview

`coreason-construct` treats prompts as assembled objects rather than raw strings. The core concept is the **Weaver**, an engine that stitches together various **Components** into a final `PromptConfiguration`.

## The Weaver

The `Weaver` is the central builder class. It manages:

*   **Component Assembly:** Adding roles, contexts, modes, etc.
*   **Dependency Resolution:** Automatically adding required contexts (e.g., adding HIPAA context when a medical role is used).
*   **Token Optimization:** (Future) Truncating low-priority components if the context window is exceeded.
*   **Provenance Capture:** Tracking which components contributed to the final prompt for auditing.

```python
from coreason_construct.weaver import Weaver

weaver = Weaver()
```

## Components

Components are the building blocks of a prompt. There are several types:

### 1. Identity Components (Roles)

Roles define the "persona" of the AI. They include tone, competencies, and biases.

```python
from coreason_construct.roles.library import SafetyScientist, MedicalDirector

# Add a role to the weaver
weaver.add(SafetyScientist)
```

**Note:** Adding a role may trigger the automatic injection of related Contexts (e.g., `GxP_Guidelines`).

### 2. Environment Components (Contexts)

Contexts define the rules and data environment.

*   **Static Contexts:** Global rules like `HIPAA_Constraints` or `GxP_Guidelines`.
*   **Dynamic Contexts:** specific data like `PatientHistory` or `StudyProtocol`.

```python
from coreason_construct.contexts.library import HIPAA_Constraints

# Manually adding a context (though Roles often do this automatically)
weaver.add(HIPAA_Constraints)
```

### 3. Cognitive Modes

Modes override the default behavior of a role to enforce a specific reasoning style.

*   `SixThinkingHats`: Forces the model to adopt a specific perspective (White, Black, Red, etc.).
*   `ReasoningPatterns`: Enforces patterns like `FirstPrinciples` or `ChainOfVerification`.

```python
from coreason_construct.modes.library import SixThinkingHats

# Force the model to think optimistically (Yellow Hat)
weaver.add(SixThinkingHats.Yellow)
```

### 4. Data Components

Data components provide "few-shot" examples or negative constraints to guide the model.

*   `FewShotBank`: Input/Output pairs mapped to a schema.
*   `NegativeExample`: Examples of what *not* to do.
*   `DataDictionary`: Domain definitions.

```python
from coreason_construct.data.library import AE_Examples

# Add few-shot examples for Adverse Event extraction
weaver.add(AE_Examples)
```

### 5. Structured Primitives

Primitives define the **Task** and the **Output Schema**. They use `instructor` to enforce strict Pydantic models on the LLM's response.

Common Primitives:
*   `ExtractionPrimitive`: Pulls entities into a model.
*   `ClassificationPrimitive`: Forces a choice from an Enum.
*   `CohortLogicPrimitive`: Generates structured query logic.
*   `SummarizationPrimitive`: Returns a structured summary.

```python
from coreason_construct.primitives.extract import ExtractionPrimitive
from coreason_construct.schemas.clinical import AdverseEvent

# Define the task
extractor = ExtractionPrimitive(
    name="AE_Extractor",
    schema=AdverseEvent
)

weaver.add(extractor)
```

## Building the Prompt

Once all components are added, use `weaver.build()` to generate the configuration.

```python
user_input = "The patient experienced a mild headache."
config = weaver.build(user_input)

# config contains:
# - system_message (assembled from components)
# - user_message (task instructions + input)
# - response_model (the Pydantic class)
# - provenance_metadata (audit trail)
```

## Integration with Instructor

The `PromptConfiguration` object is designed to be used with the `instructor` library.

```python
import instructor
import openai

client = instructor.patch(openai.OpenAI())

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": config.system_message},
        {"role": "user", "content": config.user_message}
    ],
    response_model=config.response_model
)

# response is an instance of AdverseEvent
print(response.term) # "headache"
print(response.severity) # "mild"
```

## Microservice Usage

`coreason-construct` can now be deployed as a standalone **Prompt Compilation Microservice**. This offloads component assembly, dependency resolution, and token optimization to a centralized service.

### API Endpoints

#### 1. Compile Prompt (`POST /v1/compile`)

Weaves raw components into a final, optimized configuration.

**Request:**

```json
{
  "user_input": "Patient reported nausea.",
  "variables": {"study_id": "CT-123"},
  "components": [
    {
      "name": "SafetyScientist",
      "type": "ROLE",
      "content": "You are a Safety Scientist...",
      "priority": 10
    },
    {
      "name": "BackgroundContext",
      "type": "CONTEXT",
      "content": "Protocol Details...",
      "priority": 1
    }
  ],
  "max_tokens": 100
}
```

**Response:**

```json
{
  "system_prompt": "You are a Safety Scientist...",
  "token_count": 85,
  "warnings": ["BackgroundContext"]
}
```

*Note: `warnings` lists components dropped due to `max_tokens` constraints.*

#### 2. Optimize Text (`POST /v1/optimize`)

Truncates a text block to a specific token limit using a "Middle-Out" strategy (preserving start and end).

**Request:**

```json
{
  "text": "Long chat history...",
  "limit": 100,
  "strategy": "prune_middle"
}
```

**Response:**

```json
{
  "text": "Long chat...[snip]...history end."
}
```
