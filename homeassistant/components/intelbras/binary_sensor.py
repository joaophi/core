from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntelbrasConfigEnty
from .const import DOMAIN
from .coordinator import AMTCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: IntelbrasConfigEnty,
    async_add_entities: AddEntitiesCallback,
):
    """Set up entry."""
    async_add_entities([AMTEnergySensor(config_entry.runtime_data)])
    async_add_entities([AMTOpenSensor(config_entry.runtime_data, i) for i in range(24)])
    async_add_entities(
        [AMTBatterySensor(config_entry.runtime_data, i) for i in range(24)]
    )


class AMTEnergySensor(CoordinatorEntity[AMTCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: AMTCoordinator):
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_unique_id = coordinator.servidor.mac.hex("_") + "_energy"
        self._attr_device_info = DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, coordinator.servidor.mac.hex("_"))
            },
            name=coordinator.data["messages"]["name"],
        )
        self._attr_device_class = BinarySensorDeviceClass.PLUG
        self._attr_name = coordinator.data["messages"]["name"] + " Energy"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = not self.coordinator.data["status"]["no_energy"]
        self.async_write_ha_state()


class AMTOpenSensor(CoordinatorEntity[AMTCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: AMTCoordinator, index: int):
        CoordinatorEntity.__init__(self, coordinator, context=index)
        self._index = index
        self._attr_unique_id = (
            f"{coordinator.servidor.mac.hex('_')}_zone_{index + 1:02}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._attr_unique_id)
            },
            name=coordinator.data["messages"]["zones"][index] or f"Zone {index + 1:02}",
            via_device=(DOMAIN, coordinator.servidor.mac.hex("_")),
        )
        self._attr_name = (
            coordinator.data["messages"]["zones"][index] or f"Zone {index + 1:02}"
        )
        self._attr_device_class = BinarySensorDeviceClass.OPENING

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        state = self.coordinator.data["status"]["zones"][self._index]
        self._attr_is_on = state["open"]
        self._attr_extra_state_attributes = {
            "violated": state["violated"],
            "anulated": state["anulated"],
            "stay": state["stay"],
            "enabled": state["enabled"],
        }
        self.async_write_ha_state()


class AMTBatterySensor(CoordinatorEntity[AMTCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: AMTCoordinator, index: int):
        CoordinatorEntity.__init__(self, coordinator, context=index)
        self._index = index
        self._attr_unique_id = (
            f"{coordinator.servidor.mac.hex('_')}_zone_{index + 1:02}_battery"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, f"{coordinator.servidor.mac.hex('_')}_zone_{index + 1:02}")
            },
            name=coordinator.data["messages"]["zones"][index] or f"Zone {index + 1:02}",
            via_device=(DOMAIN, coordinator.servidor.mac.hex("_")),
        )
        self._attr_device_class = BinarySensorDeviceClass.BATTERY
        self._attr_name = (
            coordinator.data["messages"]["zones"][index] or f"Zone {index + 1:02}"
        ) + " Battery"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data["status"]["zones"][self._index][
            "low_battery"
        ]
        self.async_write_ha_state()
