"""Platform for sensor integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from energy_price import EnergyPrice

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    fe_prices = EnergyPrice()
    add_entities([ElectricitySensor(fe_prices), GasSensor(fe_prices)])


class ElectricitySensor(SensorEntity):

    _attr_name = "Frank Energie Electricity Price"
    _attr_native_unit_of_measurement = CURRENCY_EURO+"/"+UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(self, fe_prices, caloric_value = 11.51) -> None:
        super().__init__()
        self.fe_prices = fe_prices
        self.caloric_value = caloric_value

    def update(self) -> None:
        self._attr_native_value = self.fe_prices.get_hourly_price('electricity')


class GasSensor(SensorEntity):

    _attr_name = "Frank Energie Gas Price"
    _attr_native_unit_of_measurement = CURRENCY_EURO+"/"+UnitOfVolume.CUBIC_METERS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, fe_prices, caloric_value = 11.51) -> None:
        super().__init__()
        self.fe_prices = fe_prices
        self.caloric_value = caloric_value

    def update(self) -> None:
        self._attr_native_value = self.fe_prices.get_hourly_price('gas') / self.caloric_value
