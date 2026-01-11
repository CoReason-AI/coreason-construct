import pytest
from pydantic import ValidationError

from coreason_construct.roles.base import RoleDefinition
from coreason_construct.roles.library import Biostatistician, MedicalDirector
from coreason_construct.schemas.base import ComponentType, PromptComponent


def test_role_definition_initialization() -> None:
    role = RoleDefinition(title="Test Role", tone="Neutral", competencies=["Skill A"], biases=["Bias B"])
    assert role.title == "Test Role"
    assert role.tone == "Neutral"
    assert role.competencies == ["Skill A"]
    assert role.biases == ["Bias B"]


def test_role_to_component_rendering() -> None:
    role = RoleDefinition(title="Test Role", tone="Neutral", competencies=["Skill A", "Skill B"], biases=["Bias X"])
    component = role.to_component()

    assert isinstance(component, PromptComponent)
    # Name sanitization check: "Test Role" -> "TestRole"
    assert component.name == "TestRole"
    assert component.type == ComponentType.ROLE
    assert component.priority == 10

    expected_content = (
        "ROLE: Test Role\nTONE: Neutral\nCOMPETENCIES:\n- Skill A\n- Skill B\nBIASES/CONSTRAINTS:\n- Bias X"
    )
    assert component.content == expected_content


def test_medical_director_role() -> None:
    comp = MedicalDirector.to_component()
    assert comp.name == "MedicalDirector"
    assert "ROLE: Medical Director" in comp.content
    assert "Risk-Averse" in comp.content
    assert "- Clinical Development Strategy" in comp.content
    assert "- Prioritize patient safety" in comp.content


def test_biostatistician_role() -> None:
    comp = Biostatistician.to_component()
    assert comp.name == "Biostatistician"
    assert "ROLE: Biostatistician" in comp.content
    assert "Precise" in comp.content
    assert "- Power Calculations" in comp.content
    assert "- Reject conclusions not supported" in comp.content


# --- Edge Case & Complex Tests ---


def test_role_validation_empty_fields() -> None:
    """Edge Case: Validation failures for empty/blank title or tone."""
    # Empty string
    with pytest.raises(ValidationError):
        RoleDefinition(title="", tone="Neutral")

    # Whitespace only
    with pytest.raises(ValidationError):
        RoleDefinition(title="   ", tone="Neutral")

    with pytest.raises(ValidationError):
        RoleDefinition(title="Valid", tone="   ")


def test_role_whitespace_stripping() -> None:
    """Edge Case: Inputs with extra whitespace should be trimmed."""
    role = RoleDefinition(title="  Spaced Role  ", tone="  Relaxed  ")
    assert role.title == "Spaced Role"
    assert role.tone == "Relaxed"

    comp = role.to_component()
    assert comp.name == "SpacedRole"
    assert "ROLE: Spaced Role" in comp.content


def test_role_empty_lists() -> None:
    """Edge Case: Role with no competencies or biases."""
    role = RoleDefinition(title="Novice", tone="Naive", competencies=[], biases=[])
    comp = role.to_component()

    assert "ROLE: Novice" in comp.content
    assert "TONE: Naive" in comp.content
    assert "COMPETENCIES:" not in comp.content
    assert "BIASES/CONSTRAINTS:" not in comp.content


def test_role_special_characters() -> None:
    """Complex Case: Handling special characters and preexisting bullets."""
    role = RoleDefinition(
        title="Dr. O'Neil & Sons",
        tone="Professional @ 100%",
        competencies=[
            "- Already bulleted",  # Should not double bullet
            "Normal item",
            "Multi\nline item",  # Should probably be handled (currently just printed)
        ],
        biases=["#1 Bias", "🚀 Emoji Support"],
    )

    comp = role.to_component()
    assert comp.name == "DrONeilSons"  # Alphanumeric only check

    assert "ROLE: Dr. O'Neil & Sons" in comp.content
    assert "- Already bulleted" in comp.content
    assert "- - Already bulleted" not in comp.content  # Check no double bullet
    assert "- 🚀 Emoji Support" in comp.content


def test_role_large_content() -> None:
    """Complex Case: Stress testing with large inputs."""
    long_competency = "A" * 1000
    many_competencies = [f"Skill {i}" for i in range(100)]

    role = RoleDefinition(title="Overqualified", tone="Verbose", competencies=[long_competency] + many_competencies)

    comp = role.to_component()
    assert len(comp.content) > 1000
    assert long_competency in comp.content
    assert "Skill 99" in comp.content
