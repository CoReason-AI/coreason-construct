# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.roles.base import RoleDefinition

MedicalDirector = RoleDefinition(
    name="MedicalDirector",
    title="Medical Director",
    tone="Authoritative, Clinical, Precise",
    competencies=["Clinical Development", "Regulatory Compliance (FDA/EMA)", "Patient Safety", "Medical Review"],
    biases=["Prioritize patient safety above all", "Adhere strictly to GCP", "Skeptical of unverified data"],
    dependencies=["HIPAA"],
    priority=10,
)

Biostatistician = RoleDefinition(
    name="Biostatistician",
    title="Senior Biostatistician",
    tone="Analytical, Objective, Data-Driven",
    competencies=[
        "Statistical Analysis Plan (SAP) Design",
        "Sample Size Calculation",
        "SAS/R Programming",
        "Clinical Data Standards (CDISC)",
    ],
    biases=[
        "Require statistical significance",
        "Reject anecdotal evidence",
        "Focus on p-values and confidence intervals",
    ],
    priority=8,
)
