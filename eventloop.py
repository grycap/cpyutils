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

import log
import time
import threading
_LOGGER = log.Log("ELOOP")

def create_eventloop(rt = True):
    global _eventloop
    if rt:
        _eventloop = _EventLoop_RTT()
    else:
        _eventloop = _EventLoop()

def set_eventloop(evloop):
    global _eventloop
    _eventloop = evloop

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

class Event_Generic(object):
    '''
    This is the base class for the definition of one event.
    '''
    _id = -1
    
    @staticmethod
    def get_event_id():
        Event._id = Event._id + 1
        return Event._id

    PRIO_LOWER = 100
    PRIO_LOW = 50
    PRIO_NORMAL = 0
    PRIO_HIGH = -50
    PRIO_HIGHER = -100
    
    def __init__(self, t, callback = None, description = None, parameters = [], priority = PRIO_NORMAL, mute = False, threaded_callback = False):
        self.id = Event.get_event_id()
        self.t = 0
        self.__set_t(t)
        if description is None:
            description = "event %s at %s" % (self.id, self.t)
        self.description = description
        self.callback = callback
        self.parameters = parameters
        self.priority = priority
        self.mute = mute
        self.lastcall = None
        self.threaded_callback = threaded_callback

    def execute_callback_in_thread(self, execute_callback_in_thread = True):
        self.threaded_callback = execute_callback_in_thread

    def call(self, now):
        # This method executes the event. If there is a callback, it will be executed
        self.lastcall = now
        
        if not self.mute:
            _LOGGER.debug("(@%.4f) executing event (%s) %s - time %.2f" % (now, self.id, self.description, self.t))

        if self.callback is not None:
            if self.threaded_callback:
                th = threading.Thread(target=self.callback,args=self.parameters)
                th.start()
            else:
                self.callback(*self.parameters)
            
    def next_sched(self, now):
        # This method returns the next time in which the event should be executed. If the event
        #   has no repetition period, it will return None to indicate that it will not be executed
        #   anymore.
        return None

    def reprogram(self, t = None):
        # This method is set to change the programmation of the next execution of the event
        self.__set_t(t)

    def __set_t(self, t):
        # We are truncating to milliseconds in order to avoid artifacts such as programming
        # two events one after the other for the same elapsed time with different priority
        # and one of them happens after the other while has more priority
        #   * This can be related to the resolution of the loop in the RT eventloop
        #     but it is around 0.5 seconds.
        # self.t = int(t * 100.0) * 0.01
        self.t = t
    
    def __str__(self):
        return "(EVENT %d@%.2f) %s" % (self.id, self.t, self.description)
    
class Event_Periodical(Event_Generic):
    '''
    This class is used to implement events that happen each period of time
    '''
    def __init__(self, t, repeat, callback = None, description = None, parameters = [], priority = Event_Generic.PRIO_NORMAL, mute = False, threaded_callback = False):
        Event_Generic.__init__(self, t, callback = callback, description = description, parameters = parameters, priority = priority, mute = mute, threaded_callback = threaded_callback)
        self.repeat = repeat

    def next_sched(self, now):
        return self.t

    def call(self, now):
        # The event will be called as usual, but it will be reprogrammed to be repeated according to the period of time
        Event_Generic.call(self, now)
        self.reprogram(self.t + self.repeat)
        
class Event(Event_Generic):
    '''
    This class is a simplification of the generic event in order to have events that happen just once
    '''
    def __init__(self, t, callback = None, description = None, parameters = [], priority = Event_Generic.PRIO_NORMAL, mute = False, threaded_callback = False):
        # We will increase the priority by just 1 in order to make that punctual events with the same priority than periodical ones will be executed in first place
        priority -= 1
        Event_Generic.__init__(self, t, callback = callback, description = description, parameters = parameters, priority = priority, mute = mute, threaded_callback = threaded_callback)

    def next_sched(self, now):
        # This method returns the next time in which the event should be executed. If the event
        #   has no repetition period, it will return None to indicate that it will not be executed
        #   anymore.
        if self.lastcall is not None:
            # If the event was called, the there is not any call more
            return None
        return self.t
    
class Event_Simple(Event):
    '''
    This class is a simplification of a generic event to have just an event without callback
    '''
    def __init__(self, t, description, mute = False):
        Event.__init__(self, t, callback = None, description = description, parameters = [], priority = Event_Generic.PRIO_NORMAL, mute = mute, threaded_callback = False)        

class _EventLoop(object):
    '''
    This class is used to implement a generic event loop that runs on time-steps. The time
        is simmulated and the eventloop just advances to the next event in the eventloop.
    '''
    def __init__(self):
        self._lock = threading.Lock()
        self.events = {}
        self.t = 0
        self.t = self.time()
        self._walltime = None
        self._endless_loop = True
        self._max_only_periodical_events = 10
        self._current_periodical_events = 10
        self._timestamp_last_new_event = None
        self._limit_new_events_time = None

    def limit_time_without_new_events(self, limit):
        # This method is used to limit the times in which no new events appear. This mechanism introduce the ability to finalize one application in which new events do not happen.
        #    It is designed mainly for simulation purposes, but maybe it has further applications in real-time apps.
        self._limit_new_events_time = limit
        
    def unlimit_time_without_new_events(self):
        self._limit_new_events_time = None

    def set_endless_loop(self, endless = True):
        self._endless_loop = endless
                
    def limit_walltime(self, walltime):
        # This method is used to limit the time during which the event loop will be executed
        self._walltime = self.time() + walltime
        
    def unlimit_walltime(self):
        # This method removes the limitation of the eventloop and will run forever
        self._walltime = None
        
    def time(self):
        # This method returns the time, according to the event loop
        return self.t
    
    def add_event(self, event):
        self._lock.acquire()
        # This method adds one event to the event loop. The event will be reprogramed to interpret the time
        #   in which the method is set to be executed to be relative to the moment in which the event is
        #   added i.e.: now.
        # It returns the event
        # It can raise an exception in case that one event with the same id already exists in the eventloop
        if event.id in self.events:
            self._lock.release()
            raise Exception("An event with id %s already exists" % event.id)

        now = self.time()
        event.reprogram(event.t + now)
        self.events[event.id] = event
        self._timestamp_last_new_event = now
        self._lock.release()
        return event

    def cancel_event(self, event_id):
        # This method cancels one event, by using its id. Returns True if the event was cancelled. Otherwise
        #   it returns False.
        result = False
        self._lock.acquire()
        if event_id in self.events:
            del self.events[event_id]
            result = True
        self._lock.release()
        return False
    
    def _sort_events(self, now):
        # This method is used to obtain the programmation of the execution of the events in the order of
        #   happening. Moreover this method also purges all these events that will not be executed anymore
        # It returns a list of pairs (event_id, program_time) that correspond to the each of the events
        #   that should be executed in the future.
        forgotten_events = []
        nexteventsqueue = []

        self._lock.acquire()
        for event_id, event in self.events.items():
            next_sched = event.next_sched(now)
            if next_sched is None:
                forgotten_events.append(event_id)
            else:
                nexteventsqueue.append((event_id, next_sched, event.priority))
                
        # Order according to 1: the time, 2: priority
        nexteventsqueue.sort(key = lambda x: (x[1], x[2]))
        self._lock.release()

        # Clean the events that are not being executed anymore
        for event_id in forgotten_events:
            self.cancel_event(event_id)
        
        return [ (x,y) for (x, y, _) in nexteventsqueue ]
    
    def _progress_to_time(self, t):
        # This method is used to make the time advance in order to be more near to one time
        self._lock.acquire()
        self.t = t
        self._lock.release()

    def loop(self):
        # This is the main loop of events. The events will be executed in order, as long as the time in
        #   the eventloop arrives to them.
        while True:
            now = self.time()
            if (self._walltime is not None) and (now > self._walltime):
                _LOGGER.info("walltime %.2f achieved" % self._walltime)
                break

            if not self._endless_loop:
                if (self._limit_new_events_time is not None):
                    elapsed = 0
                    
                    self._lock.acquire()
                    if self._timestamp_last_new_event is not None:
                        elapsed = now - self._timestamp_last_new_event
                        
                    self._lock.release()
                    if elapsed > self._limit_new_events_time:
                        _LOGGER.info("limit of time without new events reached")
                        break
            
            next_events = self._sort_events(now)
                
            if len(next_events) > 0:
                (ev_id, program_t ) = next_events[0]
                
                # will execute the first event whose time has just passed
                if program_t <= now:
                    self._lock.acquire()
                    ev = self.events[ev_id]
                    self._lock.release()
                    ev.call(now)
                else:
                    self._progress_to_time(program_t)
            else:
                if self._endless_loop:
                    # We are simply implementing an endless loop.
                    # - Using this mechanism the eventloop will be able to attend to events if they appear
                    self._progress_to_time(now + 1)
                else:
                    _LOGGER.info("no more events")
                    break
                        
    def __str__(self):
        now = self.time()
        retval = "Current Time: %f, Pending Events: %d" % (now, len(self.events))
        if len(self.events) > 0:
            for ev_id, ev in self.events.items():
                when = ev.next_sched(now)
                if when is not None:
                    when = "%.2f" % when
                else:
                    when = "None"
                retval = "%s\n%s" % (retval, "+%s [%s]" % (when, ev.description))
        return retval

class _EventLoop_TimeStep(_EventLoop):
    '''
    This class is used to create an eventloop that advances in timesteps, instead of advancing
        on the time of the events. In this way, the events happen between two different moments.
        So the events are not executed in the moment that they should be executed
    '''
    def __init__(self):
        _EventLoop.__init__(self)
        self.resolution = 0.5

    def set_resolution(self, resolution):
        # This method sets the resolution of the time for the eventloop.
        self.resolution = resolution

    def _progress_to_time(self, t):
        self._lock.acquire()
        self.t = self.t + self.resolution
        self._lock.release()

class _EventLoop_RT(_EventLoop_TimeStep):
    '''
    This class is used to create an eventloop that is executed in real time. The time-steps are
        real time units and the time is interpreted in seconds.
    '''
    def time(self):
        # The current time for this eventloop is based on the realtime.
        return time.time()
    
    def _progress_to_time(self, t):
        # The way to make that the time is more near to a time "t" in a real-time
        #   eventloop is just wait. We calculate an addapatative wait time in order
        #   to take into account the time used to execute the events.
        now = self.time()
        tsleep = self.resolution - (now - int(now / self.resolution) * self.resolution)
        time.sleep(tsleep)

class _EventLoop_RT0(_EventLoop_RT):
    def time(self):
        # The current time for this eventloop is based on the realtime, but we are
        #   substracting the init time in order to get the notion of a local time.
        return time.time() - self.t
       
class _EventLoop_RTT(_EventLoop_RT):
    def __init__(self):
        _EventLoop_RT.__init__(self)
        self.next_event = None
    
    def add_event(self, event):
        ev = _EventLoop_RT.add_event(self, event)

        self._lock.acquire()
        
        # Now we will signal the alarm in order to evaluate the event queue again
        if self.next_event is not None:
            self.next_event.set()
        
        self._lock.release()
        
        return ev
    
    def _progress_to_time(self, t):
        self._lock.acquire()
        
        if self.next_event is not None:
            # This CANNOT happen, but it will signal the event just in case
            self.next_event.set()

        self.next_event = threading.Event()
        self._lock.release()

        now = self.time()
        tsignal = t - now

        self.next_event.wait(tsignal)

class _EventLoop_RTT0(_EventLoop_RTT):
    def time(self):
        # The current time for this eventloop is based on the realtime, but we are
        #   substracting the init time in order to get the notion of a local time.
        return time.time() - self.t
            
if __name__ == '__main__':
    def create_new_event():
        get_eventloop().add_event(Event(10, description = "event in second %.1f" % (get_eventloop().time() + 10.0)))
        
    # create_eventloop(False)
    set_eventloop(_EventLoop_RTT())
    set_eventloop(_EventLoop())
    # get_eventloop().set_resolution(0.5)
    #create_eventloop(False)
    get_eventloop().add_event(Event_Periodical(0, 1, description = "periodical event each 1s"))
    get_eventloop().add_event(Event_Periodical(5, 3, description = "periodical event that starts in second 5, each 2s"))
    get_eventloop().add_event(Event(2, description = "event in second 2"))
    get_eventloop().add_event(Event(2, callback = create_new_event, description = "priority event in second 2", priority = Event.PRIO_HIGH))
    get_eventloop().limit_walltime(20.1)
    get_eventloop().loop()
