import yaml
import json
import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

# https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-notifications-cli

class AzureCloud:
    """Encapsulates Azure-specific operations for multiple subscriptions."""

    def __init__(self, inventory):
        self.subscriptions = inventory  # List of subscription IDs

    def list_vms_in_subscription(self, subscription_id):
        """List all VMs in a subscription."""
        try:
            credential = DefaultAzureCredential()
            compute_client = ComputeManagementClient(credential, subscription_id)

            # Fetch all VMs in the subscription
            vms = compute_client.virtual_machines.list_all()
            vm_list = []
            for vm in vms:
                resource_group = vm.id.split("/resourceGroups/")[1].split("/")[0]
                vm_name = vm.name
                vm_list.append((vm_name, resource_group))
            return vm_list
        except Exception as e:
            print(f"Error listing VMs in subscription {subscription_id}: {e}")
            return []

    def get_vm_maintenance_details(self, subscription_id, resource_group, vm_name):
        """Retrieve maintenance details for a specific VM."""
        command = [
            'az', 'vm', 'get-instance-view',
            '-g', resource_group,
            '-n', vm_name,
            '--subscription', subscription_id,
            '--query', 'instanceView.maintenanceRedeployStatus',
            '-o', 'json'
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr.strip()}")
                return None

            if not result.stdout.strip():
                return None

            maintenance_details = json.loads(result.stdout)
            return maintenance_details
        except Exception as e:
            print(f"Error retrieving maintenance details for VM '{vm_name}': {e}")
            return None

    def process_inventory(self):
        """Process all subscriptions and check maintenance details for VMs."""
        for subscription in self.subscriptions:
            subscription_id = subscription.get("subscription_id")
            if not subscription_id:
                print("Skipping invalid subscription entry (missing subscription_id).")
                continue

            print(f"\nProcessing subscription: {subscription_id}")
            vm_list = self.list_vms_in_subscription(subscription_id)

            if not vm_list:
                print(f"No VMs found in subscription: {subscription_id}")
                continue

            for vm_name, resource_group in vm_list:
                print(f"\nChecking maintenance status for VM: {vm_name} (Resource Group: {resource_group})")
                maintenance_details = self.get_vm_maintenance_details(subscription_id, resource_group, vm_name)
                if maintenance_details:
                    print("Maintenance Details:", json.dumps(maintenance_details, indent=4))
                else:
                    print(f"The VM `{vm_name}` is not marked for maintenance")

def load_inventory(file_path):
    """Load inventory file."""
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            print("Inventory Loaded Successfully!")
            return data
    except Exception as e:
        print(f"Error reading inventory file: {e}")
        return None

def cloud_factory(cloud_provider, inventory):
    """Factory function to return the appropriate cloud object."""
    return AzureCloud(inventory.get("azure", {}))

def main():

    cloud_provider="azure"
    if cloud_provider not in ['aws', 'azure']:
        print("Invalid cloud provider. Choose from: aws, azure")
        return

    inventory_file = "inventory.yml"  # Path to the inventory file

    # Load inventory
    inventory = load_inventory(inventory_file)
    if not inventory:
        print("Failed to load inventory. Exiting.")
        return

    # Process the selected cloud provider's inventory
    cloud = cloud_factory(cloud_provider, inventory)
    cloud.process_inventory()

if __name__ == "__main__":
    main()