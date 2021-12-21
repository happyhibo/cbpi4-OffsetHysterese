
# -*- coding: utf-8 -*-
import asyncio
from asyncio import tasks
import logging
from types import TracebackType
from cbpi.api import *
from cbpi.api.timer import Timer

@parameters([Property.Number(label="OffsetOn", configurable=True, description="Standart Offset switched on"),
             Property.Number(label="OffsetOff", configurable=True, description="Standart Offset switched off"),
             Property.Number(label="TempStart1", configurable=True, description="Starttemperatur Bereich 1"),
             Property.Number(label="TempStop1", configurable=True, description="Endtemperatur Bereich 1"),
             Property.Number(label="Offset1", configurable=True, description="Offset Bereich 1"),
             Property.Number(label="TempStart2", configurable=True, description="Starttemperatur Bereich 2"),
             Property.Number(label="TempStop2", configurable=True, description="Endtemperatur Bereich 2"),
             Property.Number(label="Offset2", configurable=True, description="Offset Bereich 2")])
class HH_Hysteresis(CBPiKettleLogic):
    
    async def run(self):
        try:
            self.offset_on = float(self.props.get("OffsetOn", 0))
            self.offset_off = float(self.props.get("OffsetOff", 0))
            self.temp_low_1 = float(self.props.get("TempStart1", 0))
            self.temp_high_1 = float(self.props.get("TempStop1", 0))
            self.offset_1 = float(self.props.get("Offset1", 0))
            self.temp_low_2 = float(self.props.get("TempStart2", 0))
            self.temp_high_2 = float(self.props.get("TempStop2", 0))
            self.offset_2 = float(self.props.get("Offset2", 0))

            self.kettle = self.get_kettle(self.id)
            self.heater = self.kettle.heater
            logging.info("OffsetHysteresis {} {} {} {}".format(self.offset_on, self.offset_off, self.id, self.heater))
            
            # sind Daten im Offset 1 angegeben
            if  (self.temp_low_1 or self.temp_high_1 or self.offset_1) != 0.0:
                setting1 = True
            else:
                setting1 = False

            # sind Daten im Offset 2 angegeben
            if  (self.temp_low_2 or self.temp_high_2 or self.offset_2) != 0.0:
                setting2 = True
            else:
                setting2 = False

            noOffset = False
            target_temp_old = 0
            while self.running == True:
                HeaterIsOn = False
                #Sensordaten abfragen
                sensor_value = self.get_sensor_value(self.kettle.sensor).get("value")
                target_temp = self.get_kettle_target_temp(self.id)
                
                if target_temp != target_temp_old:
                    noOffset = False

                #Offset Temperaturbereich Set 2
                if sensor_value <= self.temp_high_2 and sensor_value >= self.temp_low_2 and setting2 == True:
                    if noOffset == False:
                        if sensor_value >= target_temp - self.offset_2:
                            HeaterIsOn = False
                            if sensor_value >= target_temp:
                                noOffset = True
                        elif sensor_value < target_temp:
                            HeaterIsOn = True
                    else:
                        if sensor_value >= target_temp:
                            HeaterIsOn = False
                        elif sensor_value < target_temp:
                            HeaterIsOn = True

                #Offset Temperaturbereich Set 1
                elif sensor_value <= self.temp_high_1 and sensor_value >= self.temp_low_1 and setting1 == True:
                    if noOffset == False:
                        if sensor_value >= target_temp - self.offset_1:
                            HeaterIsOn = False
                            if sensor_value >= target_temp:
                                noOffset = True
                        elif sensor_value < target_temp:
                            HeaterIsOn = True
                    else:
                        if sensor_value >= target_temp:
                            HeaterIsOn = False
                        elif sensor_value < target_temp:
                            HeaterIsOn = True

                #Standart Offset wenn vorher keine Offsets gesetzt wurden
                elif noOffset == False:
                    if sensor_value >= target_temp - self.offset_off:
                        HeaterIsOn = False
                        if sensor_value >= target_temp:
                            noOffset = True
                    elif sensor_value < target_temp - self.offset_on:
                        HeaterIsOn = True

                #ohne Offsets
                elif noOffset == True:
                    if sensor_value >= target_temp:
                        HeaterIsOn = False
                    elif sensor_value < target_temp:
                        HeaterIsOn = True  

                #Actorsteuerung
                if HeaterIsOn == False:
                    await self.actor_off(self.heater)
                else:
                    await self.actor_on(self.heater)
                
                target_temp_old = target_temp
                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("OffsetHysteresis Error {}".format(e))
        finally:
            self.running = False
            await self.actor_off(self.heater)


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("OffsetHysterese", HH_Hysteresis)
