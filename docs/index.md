# coreason-construct

**The Standard Library for Cognitive Architecture.**

coreason-construct is a library designed to replace ad-hoc prompt engineering with **Component-Based Prompting** and **Type-Driven Generation**. It integrates with `instructor` to bind Pydantic schemas directly to LLM outputs, ensuring structured and reliable generation.

## Architectural Overview

The core philosophy is: **"Prompts are not written; they are assembled."**

A prompt is treated as an object composed of distinct, reusable components:

1.  **Identity (Roles)**: *Who is answering?* (e.g., `SafetyScientist`, `Biostatistician`)
    -   Defines tone, competencies, and biases.
2.  **Environment (Contexts)**: *What are the constraints?* (e.g., `HIPAA`, `GxP`)
    -   Can be static (regulations) or dynamic (patient history).
3.  **Mode (Modes)**: *How should we think?* (e.g., `SixThinkingHats`, `ChainOfVerification`)
    -   Overrides default role behavior with specific reasoning patterns.
4.  **Data**: *What evidence do we have?* (e.g., `FewShotBank`, `DataDictionary`)
    -   Provides examples and definitions to guide the model.
5.  **Task (Primitives)**: *What is the output?* (e.g., `ExtractionPrimitive`, `CohortLogicPrimitive`)
    -   Defines the structured Pydantic model for the response.

### The Weaver

The **Weaver** is the engine that stitches these components together. It is responsible for:

-   **Dependency Resolution**: Automatically injecting required contexts (e.g., adding `HIPAA` when `MedicalDirector` is used).
-   **Token Optimization**: Intelligently truncating low-priority components if the context window is exceeded.
-   **Provenance Capture**: recording which Role and Schema generated the data for auditability.
-   **Prompt Construction**: Rendering the final system and user messages using Jinja2 templating.

## Usage Pattern

The typical workflow involves:
1.  Instantiating the `Weaver`.
2.  Adding a `Role` (which brings in its dependencies).
3.  Adding relevant `Data` (e.g., few-shot examples).
4.  Adding a `Primitive` (task definition).
5.  Calling `weaver.build(user_input)` to generate the configuration.
6.  Passing the configuration to an LLM client (e.g., `instructor`-patched OpenAI client).
