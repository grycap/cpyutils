# CLUES Python Utils
This is a set of util functions and classes for python that were initially created in the CLUES project, but are of general purpose and can be used in other projects, such as VMCA.

These utilities include a mechanism to easily load configuration files, to connect to OpenNebula, to generate objects from a XML document, etc.

## Examples

### eventloop module

It is possible to create a eventloop in which the events are automatically called as they happen in the time. This is a simple example of an event loop with periodical events and one eventual alarm.

```
def function(param):
  print param

import cpyutils.eventloop
cpyutils.eventloop.create_eventloop(True)
cpyutils.eventloop.get_eventloop().add_event(10,"alarma1")
cpyutils.eventloop.get_eventloop().add_periodical_event(1, 0,"period-check",function, ["sisisi"])
cpyutils.eventloop.get_eventloop().loop()
```

This eventloop has also the possibility of running in real time or in simmulated time (the internal time of the event loop advances as a time machine to the next event).

### config module

Using this piece of code you will have the initialized values of these variables in the ```myconfig``` object, or the values in the configuration file (more complex constructions are available).

```
import cpyutils.config
cpyutils.config.set_paths([ './etc/', '/etc/' ])
cpyutils.config.set_main_config_file("myconfig.cfg")
myconfig = cpyutils.config.Configuration(
    "GENERAL",
    {
        "DEBUG_LEVEL": "error",
        "LOG_FILE": None,
    }
)
```

# Installing

Installing cpyutils package is as easy as executing (as root):

``` $ python setup.py install --record installed-files.txt```

This way you will have the installed-files.txt file to be able to uninstall this package in case that you don't need it anymore. To uninstall this package, you can execute (as root):

``` $ cat installed-files.txt | xargs rm -rf```
