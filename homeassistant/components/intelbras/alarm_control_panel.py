from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    CodeFormat,
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
    async_add_entities([AMTAlarm(config_entry.runtime_data)])


class AMTAlarm(CoordinatorEntity[AMTCoordinator], AlarmControlPanelEntity):
    def __init__(self, coordinator: AMTCoordinator):
        CoordinatorEntity.__init__(self, coordinator, None)
        self._attr_unique_id = coordinator.servidor.mac.hex("_")
        self._attr_device_info = DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._attr_unique_id)
            },
            name=coordinator.data["messages"]["name"],
        )
        self._attr_name = coordinator.data["messages"]["name"]
        self.code_format = CodeFormat.NUMBER
        self.supported_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.ARM_HOME
            | AlarmControlPanelEntityFeature.TRIGGER
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data["status"]["partitionAArmed"]:
            self._attr_state = "armed_away"
        elif self.coordinator.data["status"]["partitionBArmed"]:
            self._attr_state = "armed_home"
        elif self.coordinator.data["status"]["sirenTriggered"]:
            self._attr_state = "triggered"
        else:
            self._attr_state = "disarmed"
        self.async_write_ha_state()
