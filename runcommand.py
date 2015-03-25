import subprocess
import logging
import time

class CommandError(Exception):pass

# TODO: in case that we try to implement the simulator, we should reimplement the run_command apps to use timemachine and events
#       * it probably will not be needed, because the commands are supposed to not to fail in case that we are simmulating; this
#         this polling method is for production purposes

def _runcommand(command, shell=False, timeout = None):
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    except:
        if type(command)==list: command = " ".join(command)
        logging.error('Could not execute command "%s"' %command)
        raise
    
    finished = False
    if timeout is not None:
        now = time.time()
        while (not finished) and ((time.time() - now) < timeout):
            finished = (p.poll() is not None)
            if not finished:
                time.sleep(0.25)
        
        if not finished:
            p.kill()
            logging.error("Command \"%s\" lasted too long" % command)
            raise CommandError()
        
    (out, err) = p.communicate()
    if p.returncode != 0:
        if type(command)==list: command = " ".join(command)
        logging.error(' Error in command "%s"' % command)
        logging.error(' Return code was: %s' % p.returncode)
        logging.error(' Error output was:\n%s' % err)
        raise CommandError()
    else:
        return out

def runcommand(command, shell = True, timeout = None):
    cout = ""
    try:
        cout = _runcommand(command, shell, timeout)
    except (CommandError, OSError):
        logging.error("error executing command %s" % command)
        return False, cout
    return True, cout