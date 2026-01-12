# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.primitives.cohort import CohortLogicPrimitive
from coreason_construct.primitives.summarize import SummarizationPrimitive
from coreason_construct.schemas.base import ComponentType
from coreason_construct.schemas.primitives import CohortQuery, Summary


def test_summarization_primitive() -> None:
    """Test SummarizationPrimitive initialization."""
    primitive = SummarizationPrimitive()
    assert primitive.name == "Summarizer"
    assert primitive.type == ComponentType.PRIMITIVE
    assert primitive.response_model == Summary
    assert "Summarize" in primitive.content


def test_cohort_logic_primitive() -> None:
    """Test CohortLogicPrimitive initialization."""
    primitive = CohortLogicPrimitive()
    assert primitive.name == "CohortBuilder"
    assert primitive.type == ComponentType.PRIMITIVE
    assert primitive.response_model == CohortQuery
    assert "Translate" in primitive.content
