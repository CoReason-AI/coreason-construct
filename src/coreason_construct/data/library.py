# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_construct

from coreason_construct.data.components import FewShotBank, FewShotExample
from coreason_construct.schemas.clinical import Severity

AE_Examples = FewShotBank(
    name="AE_Examples",
    examples=[
        FewShotExample(
            input="Patient reported nausea",
            output={"term": "Nausea", "severity": Severity.MILD.value},
        )
    ],
    priority=5,
)
