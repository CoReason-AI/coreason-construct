# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.contexts.library import GxP_Context, HIPAA_Context, PatientHistory, StudyProtocol
from coreason_construct.schemas.base import ComponentType


def test_patient_history_context() -> None:
    """Test dynamic PatientHistory context."""
    patient_id = "PT-12345"
    context = PatientHistory(patient_id=patient_id)

    assert context.name == "PatientHistory_PT-12345"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 7
    assert "Patient History for ID: PT-12345" in context.content
    assert "[Dynamic patient history data" in context.content


def test_study_protocol_context() -> None:
    """Test dynamic StudyProtocol context."""
    nct_id = "NCT01234567"
    context = StudyProtocol(nct_id=nct_id)

    assert context.name == "StudyProtocol_NCT01234567"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 7
    assert "Study Protocol for NCT ID: NCT01234567" in context.content
    assert "[Dynamic protocol data" in context.content


def test_hipaa_context() -> None:
    """Test HIPAA context definition."""
    context = HIPAA_Context
    assert context.name == "HIPAA"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 10
    assert "HIPAA regulations" in context.content


def test_gxp_context() -> None:
    """Test GxP context definition."""
    context = GxP_Context
    assert context.name == "GxP"
    assert context.type == ComponentType.CONTEXT
    assert context.priority == 9
    assert "GxP guidelines" in context.content
