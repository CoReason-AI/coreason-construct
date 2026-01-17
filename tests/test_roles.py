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
from coreason_construct.roles.library import Biostatistician, MedicalDirector, SafetyScientist
from coreason_construct.schemas.base import ComponentType


def test_role_definition_auto_content() -> None:
    """Test that content is auto-generated from attributes."""
    role = RoleDefinition(name="TestRole", title="Tester", tone="Neutral", competencies=["Testing", "Debugging"])
    assert role.type == ComponentType.ROLE
    assert "You are a Tester." in role.content
    assert "Tone: Neutral." in role.content
    assert "Competencies: Testing, Debugging." in role.content


def test_role_definition_explicit_content() -> None:
    """Test that explicit content overrides auto-generation."""
    role = RoleDefinition(name="TestRole", title="Tester", tone="Neutral", competencies=[], content="Custom content")
    assert role.content == "Custom content"


def test_medical_director_role() -> None:
    """Test the MedicalDirector pre-defined role."""
    role = MedicalDirector
    assert role.name == "MedicalDirector"
    assert role.title == "Medical Director"
    assert role.priority == 10
    assert "Patient Safety" in role.content
    assert "Skeptical of unverified data" in role.content


def test_biostatistician_role() -> None:
    """Test the Biostatistician pre-defined role."""
    role = Biostatistician
    assert role.name == "Biostatistician"
    assert "Data-Driven" in role.tone
    assert "SAS/R Programming" in role.content


def test_safety_scientist_role() -> None:
    """Test the SafetyScientist pre-defined role."""
    role = SafetyScientist
    assert role.name == "SafetyScientist"
    assert role.title == "Senior Safety Scientist"
    assert role.priority == 10
    assert "Vigilant" in role.tone
    assert "Pharmacovigilance (PV)" in role.content
    assert "Assume causality until proven otherwise" in role.content
    assert "HIPAA" in role.dependencies
    assert "GxP" in role.dependencies
