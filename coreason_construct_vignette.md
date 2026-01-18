# The Architecture and Utility of coreason-construct

### 1. The Philosophy (The Why)

In the current landscape of Large Language Model (LLM) development, a significant fragility exists: the reliance on "string bashing." Developers often find themselves concatenating massive strings of natural language instructions, hoping the probabilistic model respects the implied constraints. This approach is brittle, hard to version, and difficult to validate.

**coreason-construct** emerges from the insight that "Prompts are not written; they are assembled. Outputs are not strings; they are Objects." It fundamentally reframes prompt engineering from a creative writing exercise into a **Cognitive Architecture** discipline. By treating prompt elements—Roles, Contexts, Logic Primitives—as typed objects rather than text fragments, the package brings software engineering rigor to the stochastic world of AI.

The tool addresses the critical pain point of "Cognitive Dissonance" in LLMs, where conflicting instructions or missing context lead to hallucinations. By enforcing a strict "Assembly Line" pattern, `coreason-construct` ensures that every request sent to a model is structurally sound, context-aware, and type-safe.

### 2. Under the Hood (The Dependencies & logic)

The package stands on the shoulders of giants to deliver its promise of reliability:

*   **`instructor`**: This is the bridge between the fuzzy world of language and the strict world of code. It patches LLM clients to enforce structured outputs, ensuring the model's logits align with defined schemas.
*   **`pydantic`**: Used for defining the "Cognitive Primitives." Every Role, Context, and Task is a Pydantic model, allowing for validation at assembly time, not just execution time.
*   **`jinja2`**: (Implicitly supported) Facilitates dynamic rendering of component content before assembly.

The heart of the system is the **`Weaver`**. This is not merely a string builder; it is a dependency injection container and optimization engine.
1.  **Dependency Resolution**: When a `Role` (e.g., "MedicalDirector") is added, the Weaver checks for and automatically injects required `Context` components (e.g., "HIPAA_Guidelines"), preventing the "missing context" failure mode.
2.  **Token Optimization**: Before finalizing the prompt, the Weaver calculates the token budget. If the prompt is too large, it intelligently sheds "Low Priority" components (like generic boilerplate) while strictly preserving "High Priority" data (like User Input), ensuring the model always sees what matters most.

### 3. In Practice (The How)

Here is how `coreason-construct` transforms abstract requirements into executable, type-safe operations.

#### Example A: The "Cohort Logic" Generation
Instead of asking the LLM to "write SQL," we assemble a cognitive stack designed for query generation. The `Weaver` combines a specialized Role with a `CohortLogicPrimitive` that enforces a valid `CohortQuery` structure.

```python
from coreason_construct.weaver import Weaver
from coreason_construct.roles.base import RoleDefinition
from coreason_construct.primitives.cohort import CohortLogicPrimitive

# 1. Define the Cognitive Assembler
weaver = Weaver()

# 2. Add Identity (Who is thinking?)
# The Weaver will automatically resolve any dependencies this role has.
biostat = RoleDefinition(
    name="Biostatistician",
    title="Senior Biostatistician",
    tone="Precise and Logical",
    competencies=["SQL", "Clinical Trial Protocols", "Set Theory"]
)
weaver.add(biostat)

# 3. Add the Task Primitive (What output do we need?)
# This primitive forces the LLM to output a CohortQuery object.
weaver.add(CohortLogicPrimitive())

# 4. Build the Prompt
# The result is a fully configured object ready for the instructor client.
user_request = "Find all diabetic patients over 50 who have taken Metformin."
prompt_config = weaver.build(user_input=user_request)

print(f"System Message:\n{prompt_config.system_message[:100]}...")
print(f"Target Schema: {prompt_config.response_model.__name__}")
# Output: Target Schema: CohortQuery
```

#### Example B: Type-Safe Entity Extraction
In this scenario, we need to extract specific medical events. We define a custom schema and use the generic `ExtractionPrimitive` to bind it to the LLM's output.

```python
from typing import Literal
from pydantic import BaseModel, Field
from coreason_construct.primitives.extract import ExtractionPrimitive

# 1. Define the desired output shape (The Object)
class AdverseEvent(BaseModel):
    term: str = Field(..., description="The medical term for the event")
    severity: Literal["MILD", "MODERATE", "SEVERE"]
    causality: str = Field(..., description="Likelihood related to study drug")

# 2. Assemble the components
weaver = Weaver()
weaver.add(RoleDefinition(
    name="SafetyScientist",
    title="Pharmacovigilance Expert",
    tone="Clinical",
    competencies=["Pharmacovigilance", "MedDRA Coding"]
))

# 3. Bind the extraction task to our schema
extraction_task = ExtractionPrimitive(
    name="AE_Extractor",
    schema=AdverseEvent
)
weaver.add(extraction_task)

# 4. Execute (Conceptual)
# client.chat.completions.create(..., response_model=prompt_config.response_model)
narrative = "Patient 001 experienced mild nausea 2 hours after dosing."
config = weaver.build(user_input=narrative)

# The Weaver ensures the LLM knows it MUST return an AdverseEvent object.
```
