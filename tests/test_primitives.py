# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from enum import Enum

from pydantic import BaseModel

from coreason_construct.primitives.classify import ClassificationPrimitive
from coreason_construct.primitives.extract import ExtractionPrimitive
from coreason_construct.schemas.base import ComponentType


class Colors(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"


class UserInfo(BaseModel):
    name: str
    age: int


def test_classification_primitive() -> None:
    """Test ClassificationPrimitive initialization and rendering."""
    primitive = ClassificationPrimitive(name="ColorClassifier", enum_type=Colors)

    assert primitive.name == "ColorClassifier"
    assert primitive.type == ComponentType.PRIMITIVE
    assert "RED" in primitive.content
    assert "BLUE" in primitive.content
    assert issubclass(primitive.response_model, BaseModel)

    # Verify the dynamically created model has 'selection' field of type Colors
    fields = primitive.response_model.model_fields
    assert "selection" in fields
    # Checking annotation might be tricky due to how create_model works,
    # but we can check if it accepts our Enum
    assert primitive.response_model(selection=Colors.RED).selection == Colors.RED  # type: ignore[attr-defined]


def test_extraction_primitive() -> None:
    """Test ExtractionPrimitive initialization and rendering."""
    primitive = ExtractionPrimitive(name="UserExtractor", schema=UserInfo)

    assert primitive.name == "UserExtractor"
    assert primitive.type == ComponentType.PRIMITIVE
    assert "UserInfo" in primitive.content
    assert primitive.response_model == UserInfo
