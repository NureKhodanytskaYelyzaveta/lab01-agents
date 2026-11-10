# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from app.environment import normalize_name, lookup_event_function


def test_normalize_name() -> None:
    assert normalize_name(" Awake() ") == "awake"
    assert normalize_name("Fixed Update") == "fixedupdate"
    assert normalize_name("LATE_UPDATE") == "lateupdate"


def test_lookup_known_event() -> None:
    result = lookup_event_function("Awake")
    assert result.startswith("awake:")
    assert "один раз" in result


def test_lookup_accepts_normalized_name() -> None:
    result = lookup_event_function("Fixed Update")
    assert result.startswith("fixedupdate:")


def test_lookup_unknown_event() -> None:
    result = lookup_event_function("OnTeleport")
    assert result.startswith("NOT_FOUND:")
