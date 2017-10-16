"""Created on 12/10/2017
   @author: michaelnew"""

# Third Party Imports
from datetime import datetime
from time import sleep
import json
import sys

# Python 2 compatibility
PY2 = sys.version_info[0] == 2
PY3 = (sys.version_info[0] >= 3)

if PY2:
    import Queue as queue
else:  # PY3
    import queue


# Skyze Imports
from Skyze_Standard_Library.SkyzeServiceAbstract import *
from Skyze_Messaging_Service.Messages.SkyzeMessageTypes import *


class SkyzeMessageBusService(SkyzeServiceAbstract):
    """Skyze inter-service message bus"""

    def __init__(self):
        """Constructor"""
        path_to_service = "Skyze_Messaging_Service"
        super().__init__(log_path=path_to_service)
        self.__continue_processing = True
        self.__message_bus = queue.Queue()

    def setServices(self, market_data_cleaner, market_data_updater, message_logger, notifier, scheduler, screener):
        """Sets the services pub/sub to the bus"""
        self.__market_data_cleaner_service = market_data_cleaner
        self.__market_data_updater_service = market_data_updater
        self.__message_logger_service = message_logger
        self.__notifier_service = notifier
        self.__scheduler_service = scheduler
        self.__screener_service = screener

    def getCreated(self):
        """Getter"""
        return self.__created

    def getContinueProcessing(self):
        """Getter"""
        return self.__continue_processing

    def getCreated(self):
        """Getter"""
        return self.__created

    def getJSON(self):
        """Getter"""
        return json.dumps(self.__dict__)

    def setContinueProcessing(self, continue_processing):
        """Setter"""
        self.__continue_processing = continue_processing

    def publishMessage(self, published_message):
        """Publishes Messages"""
        self.__message_bus.put(published_message)

    def __route_message(self, message):
        """Sends message to apprpriate receiver"""
        # All messages are logged
        self.__message_logger_service.log(message)

        # Route to appropriate service
        message_type = message.getMessageType()
        if message_type == SkyzeMessageType.NEW_MARKET_DATA \
           or message_type == SkyzeMessageType.SCREENER_RUN:
            # Route to the Screener Service
            self.__screener_service.receiveMessage(message)
        elif message_type == SkyzeMessageType.MARKET_DATA_UPDATER_RUN \
                or message_type == SkyzeMessageType.MARKET_DATA_UPDATER_RUN_ALL:
            # Route to the Market Data Updater Service
            self.__market_data_updater_service.receiveMessage(message)
        elif message_type == SkyzeMessageType.NOTIFICATION:
            # Route to the Notifier Service
            self.__notifier_service.receiveMessage(message)
        elif message_type == SkyzeMessageType.SCHEDULER_RUN \
                or message_type == SkyzeMessageType.SCHEDULER_TEST:
            # Route to the Scheduler Service
            self.__scheduler_service.receiveMessage(message)
        else:
            # raise exception - Message not identified
            self._unknownMessageTypeError(message)

    def process_messages(self):
        """Infinite loop to process messages on the messuage bus"""

        # Messaging handline loop
        while self.__continue_processing:
            try:
                # get next message off message bus
                next_message = self.__message_bus.get(False)
            except queue.Empty:
                # if no message then start the scheduler after this there
                # will always be a message as scheduler will generate messages
                # and sleep in between
                sleep(5)
            else:
                self.__route_message(next_message)
