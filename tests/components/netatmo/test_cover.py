"""The tests for Netatmo cover."""

from unittest.mock import AsyncMock, patch

from syrupy import SnapshotAssertion

from homeassistant.components.cover import (
    ATTR_POSITION,
    DOMAIN as COVER_DOMAIN,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    SERVICE_SET_COVER_POSITION,
    SERVICE_STOP_COVER,
)
from homeassistant.components.netatmo.const import (
    DOMAIN as NETATMO_DOMAIN,
    SERVICE_MOVE_COVER_TO_PREFERRED_POSITION,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.entity_registry as er

from .common import selected_platforms, snapshot_platform_entities

from tests.common import MockConfigEntry


async def test_entity(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    netatmo_auth: AsyncMock,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test entities."""
    await snapshot_platform_entities(
        hass,
        config_entry,
        Platform.COVER,
        entity_registry,
        snapshot,
    )


async def test_cover_setup_and_services(
    hass: HomeAssistant, config_entry: MockConfigEntry, netatmo_auth: AsyncMock
) -> None:
    """Test setup and services."""
    with selected_platforms([Platform.COVER]):
        assert await hass.config_entries.async_setup(config_entry.entry_id)

        await hass.async_block_till_done()

    switch_entity = "cover.entrance_blinds"

    assert hass.states.get(switch_entity).state == "closed"

    # Test cover open
    with patch("pyatmo.home.Home.async_set_state") as mock_set_state:
        await hass.services.async_call(
            COVER_DOMAIN,
            SERVICE_OPEN_COVER,
            {ATTR_ENTITY_ID: switch_entity},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_set_state.assert_called_once_with(
            {
                "modules": [
                    {
                        "id": "0009999992",
                        "target_position": 100,
                        "bridge": "12:34:56:30:d5:d4",
                    }
                ]
            }
        )

    # Test cover close
    with patch("pyatmo.home.Home.async_set_state") as mock_set_state:
        await hass.services.async_call(
            COVER_DOMAIN,
            SERVICE_CLOSE_COVER,
            {ATTR_ENTITY_ID: switch_entity},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_set_state.assert_called_once_with(
            {
                "modules": [
                    {
                        "id": "0009999992",
                        "target_position": 0,
                        "bridge": "12:34:56:30:d5:d4",
                    }
                ]
            }
        )

    # Test stop cover
    with patch("pyatmo.home.Home.async_set_state") as mock_set_state:
        await hass.services.async_call(
            COVER_DOMAIN,
            SERVICE_STOP_COVER,
            {ATTR_ENTITY_ID: switch_entity},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_set_state.assert_called_once_with(
            {
                "modules": [
                    {
                        "id": "0009999992",
                        "target_position": -1,
                        "bridge": "12:34:56:30:d5:d4",
                    }
                ]
            }
        )

    # Test set cover position
    with patch("pyatmo.home.Home.async_set_state") as mock_set_state:
        await hass.services.async_call(
            COVER_DOMAIN,
            SERVICE_SET_COVER_POSITION,
            {ATTR_ENTITY_ID: switch_entity, ATTR_POSITION: 50},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_set_state.assert_called_once_with(
            {
                "modules": [
                    {
                        "id": "0009999992",
                        "target_position": 50,
                        "bridge": "12:34:56:30:d5:d4",
                    }
                ]
            }
        )


async def test_service_move_cover_to_preferred_position(
    hass: HomeAssistant, config_entry: MockConfigEntry, netatmo_auth: AsyncMock
) -> None:
    """Test service clearing temperature setting."""
    with selected_platforms([Platform.COVER]):
        assert await hass.config_entries.async_setup(config_entry.entry_id)

        await hass.async_block_till_done()

    cover_entity = "cover.entrance_blinds"

    assert hass.states.get(cover_entity).state == "closed"

    # Test move cover to preferred position
    with patch("pyatmo.home.Home.async_set_state") as mock_set_state:
        await hass.services.async_call(
            NETATMO_DOMAIN,
            SERVICE_MOVE_COVER_TO_PREFERRED_POSITION,
            {ATTR_ENTITY_ID: cover_entity},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_set_state.assert_called_once_with(
            {
                "modules": [
                    {
                        "id": "0009999992",
                        "target_position": -2,
                        "bridge": "12:34:56:30:d5:d4",
                    }
                ]
            }
        )
