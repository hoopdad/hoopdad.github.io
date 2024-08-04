---
layout: post
title:  "Azure Managed Identity for Service Accounts"
---

## Why am I writing about Managed Identities on this lovely summer Saturday afternoon?

![Azure Managed Identities](/assets/Azure_Public_Service_Icons/Icons/identity/10227-icon-service-Managed-Identities.svg) As a developer who has survived and learned from generations of distributing computing, I like how Managed Identities solve a few key problems. From application code, I need to access other services and databases, but we can't leave those other services and databases wide open with no authentication or authorization. They need some auth mechanisms. And I don't want passwords stored in files, cumbersome encryption algorithms which we wrote back in the day, and I can't ask for any more favors of my operations team in password management. The "service account" concept helped with a lot but didn't get us all the way. Managed Identities simplify all of this.

## What is a Managed Identity used for?

### Background and the Problem

A service account was created just like a user account and assigned privileges, usually in Active Directory (AD). A lot of times security faux pas were committed by development teams to enable their service account to work, such as eliminating the need to ever change the password and embedding that password in clear text. Not exactly best practices!

Encrypting passwords in lookup files or services was next, and big step forward. But password rotation was still often manual, sometimes with custom tools, and, out of concern for downtime, the expiration of passwords was also usually extended mainly out of fear of production downtime.

I hope you can see by now that developers need a secure way to access various services from an application without adding burden to the operations teams.

### Managed Identity Advantages

Good thought went into the concept of the Managed Identity. It solves the above problems in a few ways.

- Managed Identities are clearly not user accounts, managed separately and can auto-cleanup when resources are deleted.
- Password rotation is not needed since the system uses a just-in-time token mechanism.
- A clever environment variable injection method puts the authentication information exactly and only where it needs to be.

## How To Use a Managed Identity

### Infrastructure Setup

You can choose to use a system-assigned managed identity, convenient for limited number of resource configurations, or a "user-assigned" managed identity, great for conveniently connecting a few resources.

I'll show you how to do a simple setup in Terraform and a couple of different ways to write code to take advantage of the built-in security.

#### Assign the Managed Identity

When you define a resource, you can also tell Azure to configure a managed identity of either kind with it. For example, when you create a Virtual Machine or a Function App, you associate a managed identity with it.

Assign roles to the managed identity on another resource such as a storage account or a key vault. This will enable processes running on your VM or Function App to get a Certificate from a Key Vault or write to certain storage objects.

Here's an example that creates a User Assigned Identity with `azurerm_user_assigned_identity`, a VM, and a storage account. It then enables the managed identity to be a Contributor to the storage account and write files to a blob using the `azurerm_role_assignment` object.

```hcl

# Declare the provider
provider "azurerm" {
  features {}
}

# Define a resource group
resource "azurerm_resource_group" "rg" {
  name     = "example-resources"
  location = "West Europe"
}

# Define a storage account
resource "azurerm_storage_account" "sa" {
  name                     = "examplestorageacct"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Define a container AKA blob in the storage account
resource "azurerm_storage_container" "container" {
  name                  = "content"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

# Define a User Assigned Managed Identity
resource "azurerm_user_assigned_identity" "identity" {
  name                = "example-identity"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

# Define your VM
resource "azurerm_virtual_machine" "vm" {
  name                  = "example-vm"
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  vm_size               = "Standard_DS1_v2"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.identity.id]
  }

  storage_os_disk {
    name              = "example-osdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_profile {
    computer_name  = "hostname"
    admin_username = "adminuser"
    admin_password = "Password1234!"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }
}

# Assign privileges via a role to the Managed Identity for the Storage Account
resource "azurerm_role_assignment" "identity_storage_contributor" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.identity.principal_id
}

# Assign privileges via a role to the Managed Identity for the Blob
resource "azurerm_role_assignment" "identity_storage_contributor" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.identity.principal_id
}
```

This serves as a starting point, and then you would need to add in your specific VNET, Subnet, and NIC details for the VM. Apply that terraform to your subscription.

#### Write your Code - SDK Example

The point of doing all this is so we can write code that uses an identity to do something. Here's a simple example of a C# program that will get the authorization token from a built-in service and write a file to the blob.

This example uses the .NET Core Identity library to simplify getting the token for you, basically in a single object constructor: `new DefaultAzureCredential()`. To get a feel for what it does under the cover, see the REST API example below this one.

```csharp
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.Storage.Blobs;
using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Azure storage account and container names
        string storageAccountName = "examplestorageacct";
        string containerName = "content";
        string blobName = "example.txt";

        // The URL of the Azure storage account
        string storageAccountUrl = $"https://{storageAccountName}.blob.core.windows.net";

        // Create a BlobServiceClient using DefaultAzureCredential
        // KEY POINT HERE
        // This service client object will run with the privileges assigned to the Managed Identity of our VM!
        BlobServiceClient blobServiceClient = new BlobServiceClient(new Uri(storageAccountUrl), new DefaultAzureCredential());

        // Get a reference to the container
        BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient(containerName);

        // Get a reference to the blob
        BlobClient blobClient = containerClient.GetBlobClient(blobName);

        // Create a new blob and upload text data
        using (MemoryStream ms = new MemoryStream())
        {
            using (StreamWriter writer = new StreamWriter(ms))
            {
                writer.Write("Hello, Blob Storage!");
                writer.Flush();
                ms.Position = 0;
                await blobClient.UploadAsync(ms, overwrite: true);
            }
        }

        Console.WriteLine("File uploaded to blob storage successfully.");
    }
}
```

Run this on the command line, i.e.

```bash
dotnet run myprogram.cs
```

#### Write your Code - REST API Example

That SDK is nice, but it isn't available for all languages. For those writing in other languages or if you want to get a little deeper into the guts of how it works, this example is for you.

Key Concept: injected environment variables

Azure will add these to your local environment whenever you have a managed identity assigned. As a developer you can use these to get the token that will be passed on to other Azure services for authentication and authorization.

- IDENTITY_ENDPOINT - the endpoint of the identity service that you will use to get your auth token
- IDENTITY_HEADER - the one-time token to pass to the identity service to get your next token that you'll use for accessing services

```python
import sys
import requests

# Get command line arguments
STORAGE_ACCOUNT_NAME = sys.argv[1]
CONTAINER_NAME = sys.argv[2]
BLOB_NAME = sys.argv[3]
LOCAL_FILE_PATH = sys.argv[4]

IDENTITY_ENDPOINT = os.getenv('IDENTITY_ENDPOINT')
IDENTITY_HEADER = os.getenv('IDENTITY_HEADER')

# KEY POINT HERE!!!!
# Get the access token from the managed identity
def get_access_token():
    if IDENTITY_ENDPOINT and IDENTITY_HEADER:
        url = IDENTITY_ENDPOINT
        headers = {
            "X-IDENTITY-HEADER": IDENTITY_HEADER
        }
    else: # We should never get to this condition these but makes example writing easier
        url = "http://169.254.169.254/metadata/identity/oauth2/token"
        headers = {
            "Metadata": "true"
        }

    params = {
        "api-version": "2018-02-01",
        "resource": "https://storage.azure.com/"
    }
    
    # send the IDENTITY_HEADER to the IDENTITY_ENDPOINT to get our token
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

# Upload the file to the blob
def upload_blob(storage_account_name, container_name, blob_name, local_file_path, access_token):
    with open(local_file_path, 'rb') as data:
        url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        headers = {
            "x-ms-blob-type": "BlockBlob",
            "Authorization": f"Bearer {access_token}" # here's the auth token from before
        }
        response = requests.put(url, headers=headers, data=data)
        response.raise_for_status()
        print(f"File uploaded to blob storage successfully. Status code: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <STORAGE_ACCOUNT_NAME> <CONTAINER_NAME> <BLOB_NAME> <LOCAL_FILE_PATH>")
        sys.exit(1)

    access_token = get_access_token()
    upload_blob(STORAGE_ACCOUNT_NAME, CONTAINER_NAME, BLOB_NAME, LOCAL_FILE_PATH, access_token)
```

Run this on your command line, i.e.

```bash
python script.py examplestorageacct content myfile.txt myfile.txt
```

## Conclusion

In Azure, take advantage of Managed Identities to greatly simplify a secure programming environment with low operational overhead! It's available for any programming language, with .NET SDK or not, using the methods above. And it can run on a lot of Azure services beyond VM's including Function App, Event Grid, and many container environments. Now, back to my summer afternoon sunshine...
