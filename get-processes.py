import psutil, sys, time, os
from prometheus_client import push_to_gateway, CollectorRegistry, Gauge

registry = CollectorRegistry()
processes = list(psutil.process_iter())

class BasicProcess:
    def __init__(self, process_name):
        super().__init__()
        self.process_name = process_name
        self.descriptive_name = process_name

    def get_running(self):
        for name, p in self.lookup_process(self.process_name):
            if name is not None:
                return True
        return False

    def lookup_process(self, name):
        try:
            for p in psutil.process_iter():
                if p.name() == name:
                    yield name, p
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return None, None


class ProcessWithArgs(BasicProcess):
    def __init__(self, desc, name, args):
        super().__init__(name)
        if isinstance(args, list):
            self.process_args = args
        else:
            self.process_args = [args]
        self.descriptive_name = desc

    def get_running(self):
        check_args = " ".join(self.process_args).lower()

        for name, p in self.lookup_process(self.process_name):
            if name is None or p is None:
                return False
            if self.process_args is None:
                return True
        
            cl = p.cmdline()
            if cl is None:
                return False

            proc_args = " ".join(cl).lower()
            if check_args in proc_args:
                return True

        return False

class PortIsOpen:
    def __init(self, port_number):
        super().__init__()
        self.port_number = port_number

    def get_running(self):
        # magic to see if the port is open?
        return False

interesting_things = [
    ProcessWithArgs("postgres", "postgres", ["-D", "/fwxserver/DB/"]),

    BasicProcess("fwldap"),
    BasicProcess("fwzmqbroker"),
    ProcessWithArgs("redis-server", "redis-server", "/usr/local/"),
    ProcessWithArgs("fwxserver_a", "fwxserver", "-a"),
    ProcessWithArgs("fwxserver_s", "fwxserver", "-s"),
    ProcessWithArgs("supervisord", "supervisord", ["-C", "/usr/local/etc/filewave"]),
    ProcessWithArgs("scheduler", "python", "/usr/local/filewave/django/scheduler/scheduler"),
    ProcessWithArgs("update_controller", "python", "/usr/local/filewave/django/update_controller/run_controller"),

    BasicProcess("node_exporter"),
    BasicProcess("prometheus"),
    BasicProcess("grafana-server"),
    BasicProcess("alertmanager"),
    
    ProcessWithArgs("filewave-web", "httpd", "fwone-django"),
    ProcessWithArgs("filewave-vpp", "httpd", "filewave-vpp"),
    ProcessWithArgs("filewave-ios", "httpd", "filewave-ios"),
    ProcessWithArgs("filewave-ldap-cf-sync", "httpd", "filewave-ldap-cf-sync"),
    ProcessWithArgs("filewave-inventory", "httpd", "filewave-inventory"),
    ProcessWithArgs("filewave-engage", "httpd", "filewave-engage"),
    ProcessWithArgs("filewave-chrome", "httpd", "filewave-chrome"),
    ProcessWithArgs("filewave-discovery", "httpd", "filewave-discovery"),
    ProcessWithArgs("filewave-notifications", "httpd", "filewave-notifications"),
    ProcessWithArgs("filewave-ios-appportal", "httpd", "filewave-ios-appportal"),
    ProcessWithArgs("filewave-fwserver", "httpd", "filewave-fwserver"),
    ProcessWithArgs("filewave-django", "httpd", "filewave-django"),
    ProcessWithArgs("filewave-dashboard", "httpd", "filewave-dashboard"),
]

if __name__ == "__main__":
    # get the metrics, post into the push gateway
    g = Gauge('filewave_process_running', 'Whether or not parts of the FW system are running or not', ['process_name'], registry=registry)

    host = os.getenv("MON_PUSHGATEWAY_HOST", "localhost")
    port = os.getenv("MON_PUSHGATEWAY_PORT", "9091")
    delay = os.getenv("MON_SECONDS_DELAY_BETWEEN_MONITOR_REQUESTS", 10)

    print("Starting! Pushing to {0}:{1}".format(host, port))

    while True:    

        for thing in interesting_things:
            is_up = thing.get_running()
            print("{}: {}".format(is_up, thing.descriptive_name))
            g.labels(process_name=thing.descriptive_name).set(is_up)

        try:
            push_to_gateway("http://{0}:{1}".format(host, port), job="monitor", registry=registry)
        except:
            pass
   
        time.sleep(delay)