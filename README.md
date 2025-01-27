# Install

## Assumptions

MacOS or Linux environments with Python 3.9 installed.

## Requirements

```
❯ pip install -r requirements.txt
```

Once installed the dependencies, update the `inventory.yml` file and specify the Azure subscription list.

```
azure:
  - subscription_id: "first-subscription-id"
```

If there are more than one subscriptions, add on to the list by adding a new line 

```
azure:
  - subscription_id: "first-subscription-id"
  - subscription_id: "second-subscription-id"
```

Once inventory is ready, install the Azure CLI and connect to it using

```
❯ az login
```

This will open up the browser and let you connect to your Azure account. Once success, the browser will tell you to close the browser and that the authentication is successful.

Second optional step is to specify your default `subscription_id` in case you have more than one.

```
❯ az account set --subscription <subscription_id>
```

Finally, Test Azure connectivity to Azure.

```
❯ az account show
{
  "environmentName": "AzureCloud",
  "id": "572262dc-1acb-4f7c-af50-4d64f1f2f7e5",
  "isDefault": true,
  "name": "Subscription Name",
  "state": "Enabled",
  "tenantId": "d8620fa6-a8dc-44e4-95de-3d9de07a0d77",
  "user": {
    "name": "user_b81774cb@example.com",
    "type": "user"
  }
}
```

To start the instance state checker


```
❯ python status_check.py
Inventory Loaded Successfully!

Processing subscription: df7c1c8e-d80a-4be9-89f0-ffe9f8754cbd

Checking maintenance status for VM: azure-test-maintenance (Resource Group: AZURETEST)
The VM `azure-test-maintenance` is not marked for maintenance
```
