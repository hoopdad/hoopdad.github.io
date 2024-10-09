---
layout: post
title:  "A More Secure PaaS Environment in Azure, Part 3 - Build and Deploy"
---

This is part 3 of a 3 part series about Microsoft's Application Service Environment.

1. Application Service Environment's Infrastructure Modes
2. Application Service Environment's Compute Isolation
3. Building and Deploying to an Application Service Environment (this post)

## Objective

This post walks through building an Azure Application Service Environment v3, and then deploying a simple Hello World timer-based Function. We will use the Zone Redundant mode for this example but will call out the 2 different parameters that differentiate the two modes. See the prior articles which help guide you to deicde which mode you need for your use case.

Note the reference to "v3" Application Service Environment throughout. This is because v1 and v2 docs and structures that you may find are incompatible with v3, which is the only supported version since August of 2024 and the writing of this post.

### Our Directory Structure

Create a directory structure like the below and we'll add files as we go.

```txt
/infrastructure/base
/infrastructure/asev3
/infrastructure/functionapp
/app
```

If you haven't yet logged into Azure via the [AZ CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows), make sure to download that and run the following.

```bash
az login
az account set --subscription <your subscription UUID>
```

## Dependency Objects

Start with identifying your Azure Subscription, signing up for your free trial if necessary. Ideally you are storing these in a git repo like GitHub and running your Terraform in CI/CD pipelines, but for example purposes we are using bash (or Windows Subsystem for Linux, WSL.) 

We'll put Terraform files into 3 subdirectories under "infrastructure". You'll need to run them in order and make sure each run is successful before moving to the next.

Create a provider file and save it into all 3 infrastructure folders.

```hcl
# provider.tf
terraform {
  backend "local" {}
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.100.0"
    }
  }
}
provider "azurerm" {
  features {
  }
}
```

Create a resource group. This is a structure in Azure that helps us to group our related object for easier management.

```hcl
# rg.tf
resource "azurerm_resource_group" "this" {
  location = "centralus"
  name     = "asev3_demo_rg
}
```

Create a subnet. You will need to identify the Virtual Network name and plan your IP address range. The Virtual Network can be defined in Terraform, too, but that will vary by organization so it is not included here.

Note about CIDR blocks: You must use at least a "/27" CIDR block (32 total addresses) as a minimum, but a "/24" (256 addresses) is recommended by Microsoft for production installations. It will need to cover multiple listeners for services you deploy.

Note about Subnet Delegation: The subnet must be "delegated" to the ASE, so if you have additional resources to deploy outside of the ASE, even like Key Vault or Storage, you will need at least one additional subnet. Here we assume ASE and app services it contains is all we are deploying. Delegation gives the containing service control over IP's in the subnet, so you would cause address conflicts if you try to deploy additionally into that subnet.

You optionally may need to enable access to your subnet with Network Security Groups and rules. This includes the HTTPS traffic from consumers of our application or services, as well as the internal load balancers that Microsoft uses in front of our services. That will vary by deployment so it is not defined here.

```hcl
# network.tf
resource "azurerm_subnet" "asev3" {
  name                 = "asev3-subnet"
  resource_group_name  = "asev3_demo_rg"
  virtual_network_name = "my_vnet"
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "Microsoft.Web.hostingEnvironments"
    service_delegation {
      name    = "Microsoft.Web/hostingEnvironments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}
```

Run your Terraform code with the following. Check the output of each and resolve any errors before going onto the next section.

```bash
cd infrastructure/base
Terraform init
Terraform validate
Terraform plan
Terraform apply
```

The Terraform messages will tell you success or failure, and I recommend logging into the Azure Portal to visually inspect the resources to make sure. Once you see the Resource Group, Network Security Group, Subnet, and NSG rules all created per spec, then move onto the ASE.

## ASE v3

We'll need to include a data reference to our subnet to get the ID. While this feels like overhead keeping the structures separate for provisioning is important because the ASE can take 2 hours to fully build, so we want to run this Terraform independently of the rest.

```hcl
# data.tf
data "azuremrm_subnet" "asev3" {
  name                 = "asev3-subnet"
  resource_group_name  = "asev3_demo_rg"
  virtual_network_name = "my_vnet""
}
```

Now create a file for the ASE definition. Note the 2 parameters that differentiate our two modes are mutually exclusive; defining both results in a Terraform error. We use `zone_redundant=true` for our deployment as we want the Zone Redundant features. When we define this, you cannot also define `dedicated_host_count` as that is the way to set it to Dedicated Host mode. You have to pick one of `zone_redundant` or `dedicated_host_count` but never both. If you want Dedicated Hosts, assign it a value greater than 1 which will create n number of virtual machines under the covers.

```hcl
# ase.tf
resource "azurerm_app_service_environment_v3" "ase" {
  name                = "my-asev3"
  resource_group_name = "asev3_demo_rg"
  subnet_id           = data.azurerm_subnet.asev3.id

  internal_load_balancing_mode = "Web, Publishing"

  zone_redundant = true
  # do not also define dedicated_host_count as that conflicts

  cluster_setting {
    name  = "DisableTls1.0"
    value = "1"
  }

  cluster_setting {
    name  = "InternalEncryption"
    value = "true"
  }

  cluster_setting {
    name  = "FrontEndSSLCipherSuiteOrder"
    value = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
  }
}
```

Finally deploy our Application Service Plan which defines the exact compute specifications. We have to use the Isolated SKU's for either ASE mode.

```hcl
# asp.tf
resource "azurerm_service_plan" "ase" {
  name                       = "my-asp"
  location                   = "centralus"
  resource_group_name        = "asev3_demo_rg"
  os_type                    = "Linux"
  sku_name                   = "I1v2"
  app_service_environment_id = azurerm_app_service_environment_v3.ase.id
}
```

Run your Terraform code with the following. Check the output of each and resolve any errors before going onto the next section.

```bash
cd infrastructure/base
Terraform init
Terraform validate
Terraform plan
Terraform apply
```

As with the first section, visit your Azure Portal to verify that the components were built successful. You may note that while the ASE is building, it is in a "Preparing" state. When completed, it should be in a "Ready" state.

Part of the activities while in "Preparing" state is internal Azure DNS registration. You may also want custom DNS names for your environment, and that is supported though out of scope of this article. The ASE deployment will create a new subdomain based on the name you provided and the Microsoft-owned "appserviceenvironment.net" domain. It will also  allocate IP addresses. Some corporate environments do not use the DNS entries created by Microsoft. In that case, you would need to add these per your organization's standards. There are many ways to do this so it is not documented here.

To find out, make sure you can resolve  <DNS Suffix>.appserviceenvironment.net at this point. If you cannot, likely you need to follow the Microsoft instructions on setting up DNS. Here's how you could test our example:

```bash
nslookup my-asev3.appserviceenvironment.net
```

If you want nice Terraform outputs, you can use `internal_inbound_ip_addresses` and `dns_suffix` from the `azurerm_app_service_environment_v3` object. All traffic to the ASE and its hosted service go to the one IP address; it cleverly uses hostnames to route to the correct one. For example, our Function App will be `funcapp.my-asev3.appserviceenvironment.net`. This will resolve to the same address as `my-asev3.appserviceenvironment.net` and `funcapp2.my-asev3.appserviceenvironment.net` since the Load Balancer is the entry point to all.

## Function App

Now we have a secure hosting place for our Function App. You can also deploy web apps, Logic Apps, or anything that goes into an Application Service Plan.

First create storage. This is used to store app settings and the deployment itself.

```hcl
#storage.tf
resource "azurerm_storage_account" "ase" {
  name                     = "mystorage"
  location                 = "centralus"
  resource_group_name      = "asev3_demo_rg"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

We'll need a reference to our App Service Plan from before.

```hcl
# data.tf
data "azurerm_service_plan" "ase" {
  name                       = "my-asp"
  resource_group_name        = "asev3_demo_rg"
}
```

And finally the Function App service itself.

```hcl
# funcapp.tf
resource "azurerm_linux_function_app" "example" {
  name                = "funcapp1"
  location            = "centralus"
  resource_group_name = "asev3_demo_rg"

  storage_account_name       = azurerm_storage_account.ase.name
  storage_account_access_key = azurerm_storage_account.ase.primary_access_key
  service_plan_id            = data.azurerm_service_plan.ase.id

  site_config {}
}
```

Run your Terraform code with the following. Check the output of each and resolve any errors before going onto the next section.

```bash
cd infrastructure/base
Terraform init
Terraform validate
Terraform plan
Terraform apply
```

You should be able to log into the Azure Portal, see the Function App in a "Running" state.

## Python Function Code

## Code Deployment

## See it run

## Summary
