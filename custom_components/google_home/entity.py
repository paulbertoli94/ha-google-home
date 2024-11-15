"""Defines base entities for Google Home"""

from __future__ import annotations

from abc import ABC, abstractmethod

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import GlocaltokensApiClient
from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .models import GoogleHomeDevice


class GoogleHomeBaseEntity(
    CoordinatorEntity[DataUpdateCoordinator[list[GoogleHomeDevice]]], ABC
):
    """Base entity base for Google Home sensors"""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[GoogleHomeDevice]],
        client: GlocaltokensApiClient,
        device_id: str,
        device_name: str,
        device_model: str,
    ):
        super().__init__(coordinator)
        self.client = client
        self.device_id = device_id
        self.device_name = device_name
        self.device_model = device_model

    @property
    @abstractmethod
    def label(self) -> str:
        """Label to use for name and unique id."""

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.device_name} {self.label}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self.device_id}/{self.label}"

    @property
    def device_info(self) -> DeviceInfo | None:
        device_info: DeviceInfo = {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": f"{DEFAULT_NAME} {self.device_name}",
            "manufacturer": MANUFACTURER,
            "model": self.device_model,
        }
        if (dev := self.get_device()) is not None and dev.mac is not None:
            device_info["connections"] = {(CONNECTION_NETWORK_MAC, dev.mac)}

        return device_info

    def get_device(self) -> GoogleHomeDevice | None:
        """Return the device matched by device name
        from the list of google devices in coordinator_data"""
        matched_devices: list[GoogleHomeDevice] = [
            device
            for device in self.coordinator.data
            if device.device_id == self.device_id
        ]
        return matched_devices[0] if matched_devices else None
