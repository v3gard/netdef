import logging
import datetime
from . import BaseController, Controllers
from ..Sources.BaseSource import StatusCode

@Controllers.register("InternalController")
class InternalController(BaseController.BaseController):
    """
    .. tip:: Development Status :: 5 - Production/Stable

    """
    def __init__(self, name, shared):
        super().__init__(name, shared)
        self.logger = logging.getLogger(self.name)
        self.logger.info("init")
        self.send_events = self.shared.config.config(self.name, "send_events", 0)
        self.send_init_event = self.shared.config.config(self.name, "send_init_event", 0)

    def run(self):
        "Main loop. Will exit when receiving interrupt signal"
        self.logger.info("Running")
        while not self.has_interrupt():
            self.loop_incoming() # dispatch handle_* functions
            self.loop_outgoing() # dispatch poll_* functions
        self.logger.info("Stopped")

    def handle_add_source(self, incoming):
        self.logger.debug("'Add source' event for %s", incoming.key)
        self.add_source(incoming.key, incoming)
        
        if not self.send_events:
            incoming.status_code = StatusCode.INITIAL
            incoming.get = {}

        if self.send_init_event:
            incoming.status_code = StatusCode.INITIAL
            incoming.get = {}
            self.send_outgoing(incoming)


    def handle_write_source(self, incoming, value, source_time):
        # vi gjør ikke så mye annet enn å tidsstemple nye verdier
        # og sette statuskoden
        
        incoming.get = value
        incoming.source_time = source_time

        prev_st = incoming.status_code

        if prev_st == StatusCode.NONE:
            incoming.status_code = StatusCode.INITIAL
        else:
            incoming.status_code = StatusCode.GOOD

        if self.send_events:
            self.send_outgoing(incoming)

    def poll_outgoing_item(self, item):
        pass
