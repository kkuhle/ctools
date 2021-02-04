# return a single filer 
from cterasdk import *
import logging

def get_filer(self):
    """Prompt for Filer and Return Filer object if found"""
    device = input("Enter device name: ")
    tenant = input("Enter tenant portal of " + device + " : ")
    try:
        filer = self.devices.device(device, tenant)
        print("Device found.")
        return filer
    except CTERAException as error:
        logging.warning(error)
        print("Device not found.")

def get_filers(self):
    """Return all connected Filers from each Tenant"""
    for tenant in self.portals.tenants():
        self.portals.browse(tenant.name)
        all_filers = self.devices.filers(include=[
                'deviceConnectionStatus.connected',
                'deviceReportedStatus.config.hostname'])
        connected_filers = []
        for filer in all_filers:
            if filer.deviceConnectionStatus.connected:
                connected_filers.append(filer)
        return connected_filers

