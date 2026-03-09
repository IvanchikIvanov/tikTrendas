from __future__ import annotations

import pytest
from pydantic import ValidationError

from trend2video.domain.entities.search_job import TrendSearchJob


def test_search_job_validates_time_window() -> None:
    with pytest.raises(ValidationError):
        TrendSearchJob(
            name="bad",
            countries=["Belarus"],
            time_window="14d",
        )
