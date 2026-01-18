# **Product Requirements Document: coreason-construct**

Domain: Component-Based Prompting, Cognitive Primitives, & Type-Safe Generation
Architectural Role: The "Prompt Assembly Line" / The Component Library
Core Philosophy: "Prompts are not written; they are assembled. Outputs are not strings; they are Objects."
Dependencies: instructor (Structured Output), coreason-validator (Schemas/Enums), coreason-codex (Terminology)

## **\---**

**1\. Executive Summary**

coreason-construct is the **Standard Library for Cognitive Architecture**.

It replaces ad-hoc prompt engineering with **Type-Driven Generation**. It integrates **instructor** to patch LLM clients, linking Pydantic schemas directly to the model's logits.

However, structure alone is not enough. The package provides a strictly typed library of **Cognitive Components**—Roles, Contexts, Logic Primitives, and Data Banks—that are assembled by the **Weaver**. The Weaver not only enforces output schema but also manages **Dependency Resolution** (context injection) and **Token Optimization** before the request is sent.

## **2\. Functional Philosophy: The Assembler Pattern**

A Prompt is an object composed of:

1. **Identity (Who):** The Role and its biases.
2. **Environment (Where):** The regulatory and data context.
3. **Mode (How):** The active reasoning style (e.g., "Six Hats", "Socratic").
4. **Data (Evidence):** Few-shot examples and negative constraints.
5. **Task (What):** The **Structured Primitive** (e.g., CohortLogic, Extract).
6. **Output (Type):** The specific Pydantic model the LLM *must* populate.

## **\---**

**3\. Core Functional Requirements (The Components)**

### **3.1 Identity Components (/roles)**

**Concept:** Standardized "Personas."

* **Structure:** RoleDefinition (Title, Tone, Competencies, Biases).
* **Requirement:** Must include the 70+ legacy roles (e.g., MedicalDirector, Biostatistician).

### **3.2 Environment Components (/contexts)**

**Concept:** "Injectable Reality."

* **Static:** GxP\_Guidelines, HIPAA\_Constraints.
* **Dynamic:** PatientHistory(id), StudyProtocol(nct\_id).

### **3.3 Cognitive Modes (/modes)**

**Concept:** "Thinking Caps" that override default role behavior.

* **Library:**
  * SixThinkingHats: White, Black, Yellow, Green, Blue, Red.
  * ReasoningPatterns: FirstPrinciples, PreMortem, ChainOfVerification.

### **3.4 Data Components (/data) \[RESTORED\]**

**Concept:** Manages the "Few-Shot" context window.

* **FewShotBank:** "Input \-\> Ideal Output" pairs mapped to the target Pydantic schema.
* **NegativeExample:** Explicit examples of failures to avoid (e.g., "Do not extract family history as a current condition").
* **DataDictionary:** Injects domain definitions (e.g., "Definition of an SAE per 21 CFR 312.32").

### **3.5 Structured Primitives (/primitives) \[RESTORED & UPDATED\]**

**Concept:** Atomic Units of Work defined by Pydantic Schemas via instructor.

* **ClassificationPrimitive:**
  * **Task:** Forces choice from a coreason-validator Enum.
* **ExtractionPrimitive:**
  * **Task:** Pulls entities into a generic Pydantic model.
* **SummarizationPrimitive:**
  * **Task:** Returns a structured summary object (e.g., class Summary(BaseModel): title: str, bullets: List\[str\], sentiment: float).
* **CohortLogicPrimitive:**
  * **Task:** Generates structured query logic for patient selection.
  * **Output Schema:** class CohortQuery(BaseModel): inclusion\_criteria: List\[Criterion\], sql\_logic: str.

### **3.6 The Weaver (The Builder Engine) \[RESTORED\]**

**Concept:** The engine that stitches components into the final request configuration.

* **Dependency Resolution:** If the Role is Doctor, the Weaver *automatically* injects HIPAA\_Context without the developer asking.
* **Token Optimization:** If the prompt exceeds the context window, the Weaver intelligently truncates "Low Priority" contexts (e.g., generic GxP rules) while preserving "High Priority" data (User Input).
* **Output:** Returns a PromptConfiguration compatible with instructor.

## **\---**

**4\. Data Schema & Object Definitions**

### **4.1 Base Classes**

Python

from enum import Enum
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel
import instructor

class ComponentType(str, Enum):
    ROLE \= "ROLE"
    CONTEXT \= "CONTEXT"
    MODE \= "MODE"
    DATA \= "DATA"
    PRIMITIVE \= "PRIMITIVE"

class PromptComponent(BaseModel):
    name: str
    type: ComponentType
    content: str
    priority: int \= 1  \# 1 (Low) to 10 (Critical)

    def render(self, \*\*kwargs) \-\> str:
        return self.content.format(\*\*kwargs)

class PromptConfiguration(BaseModel):
    system\_message: str
    user\_message: str
    response\_model: Optional\[Type\[BaseModel\]\]
    max\_retries: int \= 3
    provenance\_metadata: Dict\[str, str\] \# For Veritas Logging

### **4.2 The Weaver (With Intelligence)**

Python

class Weaver:
    def \_\_init\_\_(self):
        self.components: List\[PromptComponent\] \= \[\]
        self.\_response\_model: Optional\[Type\[BaseModel\]\] \= None

    def add(self, component: PromptComponent):
        \# 1\. Dependency Resolution
        if component.name \== "MedicalDirector" and not self.\_has\_component("HIPAA"):
            self.components.append(get\_context("HIPAA"))

        self.components.append(component)
        if isinstance(component, StructuredPrimitive):
            self.\_response\_model \= component.response\_model
        return self

    def build(self, user\_input: str, variables: Dict\[str, Any\] \= {}) \-\> PromptConfiguration:
        \# 2\. Optimization (Mock logic)
        \# if total\_tokens \> limit: remove\_low\_priority(self.components)

        sorted\_comps \= self.\_sort\_components(self.components)

        system\_parts \= \[c.render(\*\*variables) for c in sorted\_comps if c.type \!= ComponentType.PRIMITIVE\]
        task\_part \= next((c.render(\*\*variables) for c in sorted\_comps if c.type \== ComponentType.PRIMITIVE), "")

        final\_user\_msg \= f"{task\_part}\\n\\nINPUT DATA:\\n{user\_input}"

        \# 3\. Provenance Capture
        metadata \= {
            "role": next((c.name for c in self.components if c.type \== ComponentType.ROLE), "None"),
            "mode": next((c.name for c in self.components if c.type \== ComponentType.MODE), "None"),
            "schema": self.\_response\_model.\_\_name\_\_ if self.\_response\_model else "None"
        }

        return PromptConfiguration(
            system\_message="\\n\\n".join(system\_parts),
            user\_message=final\_user\_msg,
            response\_model=self.\_response\_model,
            provenance\_metadata=metadata
        )

## **\---**

**5\. Directory Structure**

Plaintext

coreason-construct/
├── src/
│   └── coreason\_construct/
│       ├── roles/              \# Identity
│       ├── contexts/           \# Environment
│       ├── modes/              \# Cognitive Modes
│       ├── data/               \# Few-Shot & Negatives \[RESTORED\]
│       ├── primitives/         \# Structured Tasks
│       │   ├── classify.py
│       │   ├── extract.py
│       │   ├── summarize.py    \# \[RESTORED\]
│       │   └── cohort.py       \# \[RESTORED\]
│       ├── schemas/            \# Internal schemas
│       └── weaver.py           \# Builder with Logic

## **\---**

**6\. User Stories**

### **Story A: The "Cohort Logic" Generation**

Goal: Translate "Find diabetic patients over 50" into a query.
Weaver Assembly:

* **Role:** Biostatistician
* Primitive: CohortLogicPrimitive (Schema: CohortQuery)
  Execution:
* LLM outputs: CohortQuery(sql="SELECT \* FROM person WHERE...", criteria=\[...\]).
* *Note:* The schema enforces valid SQL syntax structure.

### **Story B: The "Type-Safe" Extraction**

Goal: Extract Adverse Events.
Weaver Assembly:

* **Role:** SafetyScientist
* **Data:** FewShotBank("AE\_Examples")
* Primitive: ExtractionPrimitive(schema=AdverseEventSchema)
  Result: LLM returns AdverseEvent(term="Nausea", severity="MILD").

## **\---**

**7\. Implementation Directives for the Coding Agent**

1. **Instructor Integration:** primitives must use instructor to define the interaction with the LLM.
2. **Serialization (Audit):** The Weaver.build() method must return provenance\_metadata. This dictionary must be passed to coreason-veritas whenever the prompt is executed, ensuring we know *which* Role and *which* Schema generated the data.
3. **Schema Flexibility:** The ExtractionPrimitive must accept Generic types to support any Pydantic model.
4. **Auto-Dependency:** Implement a basic dependency map (e.g., Role \-\> RequiredContexts) in the Weaver to automate context injection.
