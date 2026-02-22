"""Tests for station selection domain rules."""
from __future__ import annotations

import pytest

from src.domain.model.station import Station, StationType, StationId, DatasetId
from src.domain.rules.station_selection import StationSelectionPolicy, StationSelector


class TestStationSelectionPolicy:
    """Tests for StationSelectionPolicy."""

    def _create_station(
        self,
        station_id: int,
        station_type: StationType = StationType.ISS,
        is_active: bool = True,
    ) -> Station:
        return Station(
            id=StationId(station_id),
            dataset_id=DatasetId(f"{station_id}-dataset"),
            name=f"Station {station_id}",
            station_type=station_type,
            is_active=is_active,
        )

    def test_default_policy_accepts_active_iss(self) -> None:
        policy = StationSelectionPolicy()
        station = self._create_station(42, StationType.ISS, is_active=True)
        assert policy.accepts(station)

    def test_default_policy_rejects_inactive(self) -> None:
        policy = StationSelectionPolicy()
        station = self._create_station(42, StationType.ISS, is_active=False)
        assert not policy.accepts(station)

    def test_default_policy_rejects_other_type(self) -> None:
        policy = StationSelectionPolicy()
        station = self._create_station(42, StationType.OTHER, is_active=True)
        assert not policy.accepts(station)

    def test_policy_allow_inactive(self) -> None:
        policy = StationSelectionPolicy(allow_inactive=True)
        station = self._create_station(42, StationType.ISS, is_active=False)
        assert policy.accepts(station)

    def test_policy_allow_other_types(self) -> None:
        policy = StationSelectionPolicy(
            allowed_types=frozenset({StationType.ISS, StationType.OTHER})
        )
        station_iss = self._create_station(42, StationType.ISS)
        station_other = self._create_station(43, StationType.OTHER)
        
        assert policy.accepts(station_iss)
        assert policy.accepts(station_other)

    def test_policy_whitelist_accepts_listed(self) -> None:
        policy = StationSelectionPolicy(
            whitelist=frozenset({StationId(42), StationId(43)})
        )
        station = self._create_station(42)
        assert policy.accepts(station)

    def test_policy_whitelist_rejects_unlisted(self) -> None:
        policy = StationSelectionPolicy(
            whitelist=frozenset({StationId(42), StationId(43)})
        )
        station = self._create_station(99)
        assert not policy.accepts(station)

    def test_policy_blacklist_rejects_listed(self) -> None:
        policy = StationSelectionPolicy(
            blacklist=frozenset({StationId(42)})
        )
        station = self._create_station(42)
        assert not policy.accepts(station)

    def test_policy_blacklist_accepts_unlisted(self) -> None:
        policy = StationSelectionPolicy(
            blacklist=frozenset({StationId(42)})
        )
        station = self._create_station(43)
        assert policy.accepts(station)

    def test_policy_blacklist_overrides_whitelist(self) -> None:
        policy = StationSelectionPolicy(
            whitelist=frozenset({StationId(42)}),
            blacklist=frozenset({StationId(42)}),
        )
        station = self._create_station(42)
        # Blacklist should take precedence
        assert not policy.accepts(station)

    def test_policy_all_conditions_must_pass(self) -> None:
        policy = StationSelectionPolicy(
            allowed_types=frozenset({StationType.ISS}),
            allow_inactive=False,
            whitelist=frozenset({StationId(42)}),
        )
        
        # Correct type, active, in whitelist -> accept
        station_ok = self._create_station(42, StationType.ISS, is_active=True)
        assert policy.accepts(station_ok)
        
        # Wrong type
        station_wrong_type = self._create_station(42, StationType.OTHER, is_active=True)
        assert not policy.accepts(station_wrong_type)
        
        # Inactive
        station_inactive = self._create_station(42, StationType.ISS, is_active=False)
        assert not policy.accepts(station_inactive)
        
        # Not in whitelist
        station_not_whitelisted = self._create_station(99, StationType.ISS, is_active=True)
        assert not policy.accepts(station_not_whitelisted)


class TestStationSelector:
    """Tests for StationSelector service."""

    def _create_station(
        self,
        station_id: int,
        station_type: StationType = StationType.ISS,
        is_active: bool = True,
    ) -> Station:
        return Station(
            id=StationId(station_id),
            dataset_id=DatasetId(f"{station_id}-dataset"),
            name=f"Station {station_id}",
            station_type=station_type,
            is_active=is_active,
        )

    def test_selector_filters_by_policy(self) -> None:
        policy = StationSelectionPolicy()
        selector = StationSelector(policy)
        
        candidates = [
            self._create_station(42, StationType.ISS, is_active=True),
            self._create_station(43, StationType.OTHER, is_active=True),
            self._create_station(44, StationType.ISS, is_active=False),
        ]
        
        selected = selector.select(candidates)
        assert len(selected) == 1
        assert selected[0].id.value == 42

    def test_selector_returns_sorted_list(self) -> None:
        policy = StationSelectionPolicy()
        selector = StationSelector(policy)
        
        candidates = [
            self._create_station(99, StationType.ISS, is_active=True),
            self._create_station(42, StationType.ISS, is_active=True),
            self._create_station(55, StationType.ISS, is_active=True),
        ]
        
        selected = selector.select(candidates)
        assert len(selected) == 3
        assert selected[0].id.value == 42
        assert selected[1].id.value == 55
        assert selected[2].id.value == 99

    def test_selector_empty_candidates(self) -> None:
        policy = StationSelectionPolicy()
        selector = StationSelector(policy)
        
        selected = selector.select([])
        assert len(selected) == 0

    def test_selector_no_matches(self) -> None:
        policy = StationSelectionPolicy()
        selector = StationSelector(policy)
        
        candidates = [
            self._create_station(42, StationType.OTHER, is_active=True),
            self._create_station(43, StationType.ISS, is_active=False),
        ]
        
        selected = selector.select(candidates)
        assert len(selected) == 0

    def test_selector_all_match(self) -> None:
        policy = StationSelectionPolicy()
        selector = StationSelector(policy)
        
        candidates = [
            self._create_station(42, StationType.ISS, is_active=True),
            self._create_station(43, StationType.ISS, is_active=True),
            self._create_station(44, StationType.ISS, is_active=True),
        ]
        
        selected = selector.select(candidates)
        assert len(selected) == 3
