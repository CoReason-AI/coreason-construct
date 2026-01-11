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
