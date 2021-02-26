import menu
from filer import get_filers
from login import login
from cterasdk import *
import csv, logging, os, re, sys

def write_status(p_filename):
    """Save and write Filer status information to filename param."""
    global_admin = login()
    """List of paths to pass to get_multi request"""
    get_list = ['config','status','proc/cloudsync','proc/time/',
                'proc/storage/summary','proc/perfMonitor']
    for filer in get_filers(global_admin):
        info = filer.get_multi('', get_list)
        sync_id = info.proc.cloudsync.serviceStatus.id
        selfScanIntervalInHours = info.config.cloudsync.selfScanVerificationIntervalInHours
        uploadingFiles = info.proc.cloudsync.serviceStatus.uploadingFiles
        scanningFiles = info.proc.cloudsync.serviceStatus.scanningFiles
        selfVerificationscanningFiles = info.proc.cloudsync.serviceStatus.selfVerificationScanningFiles
        CurrentFirmware = info.status.device.runningFirmware
        try:
            MetaLogMaxSize = info.config.logging.metalog.maxFileSizeMB
        except:
            try:
                MetaLogMaxSize = filer.get('/config/logging/log2File/maxFileSizeMB')
            except:
                MetaLogMaxSize = ('Not Applicable')
        try:
            MetaLogMaxFiles = info.config.logging.metalog.maxfiles
        except:
            try:
                MetaLogMaxFiles = filer.get('/config/logging/log2File/maxfiles')
            except:
                MetaLogMaxFiles = ('Not Applicable')
        try:
            MetaLogs1 = filer.cli.run_command('dbg le')
        except:
            MetaLogs1 = ('Not Applicable')
        License = filer.licenses.get()
        # License = info.config.device.activeLicenseType
        IP1 = info.status.network.ports[0].ip.address
        storageThresholdPercentTrigger = info.config.cloudsync.cloudExtender.storageThresholdPercentTrigger
        uptime = info.proc.time.uptime
        curr_cpu = info.proc.perfMonitor.current.cpu
        curr_mem = info.proc.perfMonitor.current.memUsage
        _total = info.proc.storage.summary.totalVolumeSpace
        _used = info.proc.storage.summary.usedVolumeSpace
        _free = info.proc.storage.summary.freeVolumeSpace
        volume = "Total: {} Used: {} Free: {}".format(_total,_used,_free)
        #dbg_level = filer.support.set_debug_level()
        #MetaLogs1 = dbg_level[-28:-18]
        Alerts = info.config.logging.alert
        TimeServer = info.config.time
        _mode = TimeServer.NTPMode
        _zone = TimeServer.TimeZone
        _servers = TimeServer.NTPServer
        time = "Mode: {} Zone: {} Servers: {}".format(_mode,_zone,_servers)

        """Parse Performance History"""
        def get_max_cpu():
            cpu_history = []
            for i in info.proc.perfMonitor.samples:
                cpu_history.append(i.cpu)
            return "{}%".format(max(cpu_history))

        def get_max_memory():
            memory_history = []
            for i in info.proc.perfMonitor.samples:
                memory_history.append(i.memUsage)
            return "{}%".format(max(memory_history))


        """Write results to output filename"""
        with open(p_filename, mode='a', newline='', encoding="utf-8-sig") as gatewayList:
            gateway_writer = csv.writer(gatewayList, 
                    dialect='excel',
                    delimiter=',', 
                    quotechar='"', 
                    quoting=csv.QUOTE_MINIMAL)
            gateway_writer.writerow([
                    filer.name,
                    sync_id,
                    selfScanIntervalInHours,
                    uploadingFiles,
                    scanningFiles,
                    selfVerificationscanningFiles,
                    MetaLogs1,
                    MetaLogMaxSize,
                    MetaLogMaxFiles,
                    CurrentFirmware,
                    License,
                    storageThresholdPercentTrigger,
                    volume,
                    IP1,
                    Alerts,
                    time,
                    uptime,
                    "CPU: {}% Mem: {}%".format(curr_cpu,curr_mem),
                    get_max_cpu(),
                    get_max_memory()
                    ])
    global_admin.logout()

def write_header(p_filename):
    """Write CSV header to given filename parameter """
    try:
        with open(p_filename, mode='a', newline='', encoding="utf-8-sig") as gatewayList:
            gateway_writer = csv.writer(
                    gatewayList,
                    dialect='excel',
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                    )
            gateway_writer.writerow(['Gateway',
                                     'CloudSync Status',
                                     'selfScanIntervalInHours',
                                     'uploadingFiles',
                                     'scanningFiles',
                                     'selfVerificationscanningFiles',
                                     'MetaLogsSetting',
                                     'MetaLogMaxSize',
                                     'MetaLogMaxFiles',
                                     'CurrentFirmware',
                                     'License',
                                     'EvictionPercentage',
                                     'CurrentVolumeStorage',
                                     'IP Config',
                                     'Alerts',
                                     'TimeServer',
                                     'uptime',
                                     'Current Performance',
                                     'Max CPU',
                                     'Max Memory'
                                     ])
    except FileNotFoundError as error:
        logging.error(error)
        print("ERROR: Unable to open filename specified: {}".format(p_filename))
        sys.exit("Make sure you entered a valid file name and it exists")

def create_csv():
    """Prompt to create a CSV or append to existing. Return filename."""
    _filename = input("Enter output filename. Make sure extension is csv: ")
    if os.path.exists(_filename):
        print ('File exists. It will be deleted and a new one will be created')
        deletefile = input("Delete File? Type Y/n: ")
        if deletefile in ('Y', 'y'):
            os.remove(_filename)
            write_header(_filename)
        if deletefile in ('N', 'n'):
            print ('Contents will be appended to the existing file')
    else:
        print("Output file does not exist. Creating new file")
        write_header(_filename)
    return _filename

def run_status():
    logging.info('Starting status task')
    filename = create_csv()
    write_status(filename)
    logging.info('Finished status task.')
    menu.menu()

