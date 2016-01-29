# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 


# This version is DEPRECATED:
#   it is just kept for compatibility issues with old apps

import time
import logging

_LOGGER = logging.getLogger("[ELOOP]")
_LOGGER.warning("\n\nThis version of eventloop is deprecated. Please use the new enhanced version\n\n")

_id = -1

class Event:
    @staticmethod
    def get_event_id():
        global _id
        _id = _id + 1
        return _id

    PRIO_LOWER = 0
    PRIO_LOW = 10
    PRIO_NORMAL = 20
    PRIO_HIGH = 30
    PRIO_HIGHER = 40
    
    def __init__(self, t, desc, callback, parameters):
        self.id = Event.get_event_id()
        self.t = t
        self.desc = desc
        self.callback = callback
        self.parameters = parameters
        
        # This is a hack to mute a event (ad-hoc solution to mute ''LRMS lifecycle'') TODO (0): eliminar?
        self.stealth = False
        
    def call(self):
        if not self.stealth:
            _LOGGER.debug("(@%.2f) executing event (%s) %s - time %.2f" % (_eventloop.time(), self.id, self.desc, self.t))
            
        if self.callback is not None:
            self.callback(*self.parameters)
            
    def __str__(self):
        return "(EVENT %d@%.2f) %s" % (self.id, self.t, self.desc)

class Event_Periodical(Event):
    def __init__(self, start, t, desc, callback, parameters):
        Event.__init__(self, t, desc, callback, parameters)
        self.start = start
        self.last_called = None
        
    def next_sched(self):
        last_called = self.last_called        
        if last_called is None:
            last_called = 0
        
        last_called = max(self.start, last_called)
        return last_called + self.t
    
    def call(self):
        global _eventloop
        self.last_called = _eventloop.time()
        Event.call(self)

class _EventLoop:
    def __str__(self):
        retval = "Current Time: %f, Pending Events: %d" % (self.time(), len(self._events))
        if len(self._events):
            retval = "%s, Next Event in %.2f time units\nEvent List:" % (retval, self._events[0].t - self._t)
            for ev in self._events:
                retval = "%s\n%s" % (retval, "+%.2f [%s]" % (ev.t - self._t, ev.desc))
        return retval
    
    def __init__(self):
        self._events = []
        self._periodical_events = []
        self._t = 0
        
    def timestep(self):
        self._t = self._t + 1
        return self._t
        
    def _execute_periodical_events(self, next_sched_time):
        # Now we are going to check if there is a periodical event before the next event
        # while True:
        min_sched = next_sched_time
        pe_execute = None
        for pe in self._periodical_events:
            next_sched = pe.next_sched() 
            if next_sched <= min_sched:
                pe_execute = pe
                min_sched = next_sched
                
        if (pe_execute is not None) and (min_sched >= self._t):
            self._t = min_sched
            pe_execute.call()
            return pe_execute
    
        return None
        
    #def force_next_event(self):
    #    # This method is only for non real time timemachines
    #    if len(self._periodical_events) > 0:
    #        for pe in self._periodical_events:
    #            next_sched = pe.next_sched()
    #            ev = self._execute_periodical_events(next_sched)
    #
    #            # We finalize here, because the previous method will check if there is any other event (periodical or not) and will execute it
    #            if ev is not None:
    #                return True
    #            
    #    return False
        
    def advance_to_next_event(self):
        if len(self._events) == 0:
            return None
        
        pe_execute = self._execute_periodical_events(self._events[0].t)
        if pe_execute is not None:
            return pe_execute
                
        ev = self._events.pop(0)
        self._t = ev.t
        ev.call()
        return ev
    
    def time(self):
        return self._t
    
    def event_count(self):
        return len(self._events)
    
    def add_control_event(self, elapsed, desc = "control event to force reaching to a timestamps in simulated environments", stealth = True):
        self.add_event(elapsed, desc, stealth = stealth)
    
    def add_periodical_event(self, elapsed, start_time = 0, desc = "", callback = None, arguments = [], stealth = False):
        ev = Event_Periodical(self._t + start_time, elapsed, desc, callback, arguments)
        # ev = Event_Periodical(start_time, elapsed, desc, callback, arguments)
        ev.stealth = stealth    # TODO (0): eliminar?

        if not stealth:         # TODO (0): eliminar?
            _LOGGER.debug("(@%.2f) appending periodical event (%s) %s @ %.2f" % (self.time(), ev.id, ev.desc, ev.t))
        
        self._periodical_events.append(ev)
        return ev.id
    
    def add_event(self, elapsed, desc = "", callback = None, arguments = [], stealth = False):
        ev = Event(self._t + elapsed, desc, callback, arguments)
        ev.stealth = stealth    # TODO (0): eliminar?

        if not stealth:         # TODO (0): eliminar?
            _LOGGER.debug("(@%.2f) appending event (%s) %s @ %.2f" % (self.time(), ev.id, ev.desc, ev.t))
        
        if len(self._events) == 0:
            self._events.append(ev)
            return ev        

        # now find where to insert the event
        prev_t = self._t
        for i in range(0, len(self._events)):
            if (ev.t >= prev_t) and (ev.t < self._events[i].t): 
                self._events.insert(i, ev)
                return ev
            else:
                prev_t = self._events[i].t

        self._events.append(ev)
        return ev
    
    def cancel_event(self, ev_id):
        # This is probably a slow mechanism to cancel an event, but by now will be enough
        events = [ ev for ev in self._events if ev.id != ev_id ]
        self._events = events
        
        periodical_events = [ ev for ev in self._periodical_events if ev.id != ev_id ]
        self._periodical_events = periodical_events

    def loop(self, stime = 0.5):
        _LOGGER.info("running in simulated time")
        _LOGGER.debug("remember that this method should be used only for batches because of lack of interactivity")
        
        while True:
            e = self.advance_to_next_event()
            if e is None:
                time.sleep(stime)

class _EventLoop_RT(_EventLoop):
    def __init__(self):
        self._s = 0 # time.time()
        _EventLoop.__init__(self)
        
    def time(self):
        return time.time() - self._s

    def force_next_event(self):
        pass

    def execute_next_event(self):
        # Now we are going to check if there is a periodical event before the next event
        # while True:
        min_sched = self.time()
            
        pe_execute = None
        for pe in self._periodical_events:
            next_sched = pe.next_sched()
            if next_sched <= min_sched:
                pe_execute = pe
                min_sched = next_sched
                
        if (pe_execute is not None):
            # self._t = min_sched
            pe_execute.call()
            return pe_execute

        # -----------------------

        if len(self._events) == 0:
            return None

        if self.time() >= self._events[0].t:
            ev = self._events.pop(0)
            self._t = ev.t
            ev.call()
            self._t = time.time()
            return ev
        
        return None

    def add_event(self, elapsed, desc = "", callback = None, arguments = [], stealth = False):
        self._t = self.time()
        return _EventLoop.add_event(self, elapsed, desc, callback, arguments, stealth)

    def add_periodical_event(self, elapsed, start_time = 0, desc = "", callback = None, arguments = [], stealth = False):
        self._t = self.time()
        return _EventLoop.add_periodical_event(self, elapsed, start_time, desc, callback, arguments, stealth)

    def advance_to_next_event(self):
        return None

    def loop(self, stime = 0.5):
        _LOGGER.info("running in real time")

        while True:
            e = self.execute_next_event()
            if e is None:
                time.sleep(stime)

def create_eventloop(rt = True):
    global _eventloop
    if rt:
        _eventloop = _EventLoop_RT()
    else:
        _eventloop = _EventLoop()

def get_eventloop():
    global _eventloop
    if _eventloop is None:
        create_eventloop()
    return _eventloop

_eventloop = None
_NOW = 0

# This can be used to avoid multiple calls to time.time() but also to make coincide events in time
def now():
    global _eventloop
    global _NOW
    if _eventloop is None:
        _NOW = time.time()
    else:
        _NOW = _eventloop.time()
    return _NOW

# TODO: implementando la cola con prioridades (hay eventos "poco" prioritarios y otros que son mas: ej. un trabajo termina)
if __name__ == '__main__':

    def function(param):
        print param

    logging.basicConfig(filename=None,level=logging.DEBUG)
    
    create_eventloop(False)
    _eventloop.add_event(10,"alarma1")
    _eventloop.add_event(10,"alarma1")
    _eventloop.add_event(12,"alarma2")
    _eventloop.add_event(12,"alarma3")
    _eventloop.add_event(12,"alarma4")
    _eventloop.add_event(11,"alarma5")
    _eventloop.add_event(16,"alarma4")
    _eventloop.add_periodical_event(5, 0,"periodical")
    _eventloop.add_periodical_event(1, 0,"period-check",function, ["sisisi"])
    
    _eventloop.add_event(1,"alarma6",function,["hi"])
    print _eventloop
    
    _eventloop.loop()