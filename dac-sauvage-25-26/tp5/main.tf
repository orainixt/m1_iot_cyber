terraform {
  required_version = ">= 1.4.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

variable "os_auth_url" {type = string} 
variable "os_username" {type = string} 
variable "os_project_id" {type = string} 
variable "os_project_name" {type = string} 
variable "os_domain" {type = string} 
variable "os_region" {type = string} 
variable "os_password" {
    type = string
    sensitive = true
}
variable "image_name" {type = string}
variable "image_id" {type=string}

variable "vm_flavor" {type=string}

variable "instance_names" {type=list(string)} 

variable "vm_key_pair" {type=string}
provider "openstack" {
  user_name   = var.os_username
  tenant_id   = var.os_project_id
  password    = var.os_password
  auth_url    = var.os_auth_url
  region      = var.os_region
}


resource "openstack_compute_instance_v2" "instance" {
  for_each = toset(var.instance_names)
  name = each.value
  provider = openstack
  flavor_name = var.vm_flavor
  image_id = var.image_id
  key_pair = var.vm_key_pair 
}

output "instance_1_ip_adress" {
   value = openstack_compute_instance_v2.instance["db1"].access_ip_v4
}
output "instance_2_ip_adress" {
   value = openstack_compute_instance_v2.instance["web1"].access_ip_v4
}

# # Création d'une paire de clé SSH
# resource "openstack_compute_keypair_v2" "keypair" {
#     name = "keypaircode"
#     public_key = "${file("~ficher.pub")}"
# }

# data "open_stack_image" "ubuntu" {
#     most_recent = true 
#     name= var.image_name
# }

# ## Get the external network
# data "openstack_networking_network_v2" "external-network" {
#   name = "PUBLICNET"
# }

# ## Create a router
# resource "openstack_networking_router_v2" "external-router" {
#   name                = "external-router"
#   admin_state_up      = true
#   external_network_id = data.openstack_networking_network_v2.external-network.id
# }

# ## Create internal network
# resource "openstack_networking_network_v2" "internal-network" {
#   name                  = "internal-network"
#   admin_state_up        = "true"
#   external              = false
#   port_security_enabled = true
# }

# ## Create internal subnet
# resource "openstack_networking_subnet_v2" "internal-subnet" {
#   name        = "internal-subnet"
#   network_id  = openstack_networking_network_v2.internal-network.id
#   cidr        = "192.168.50.0/24"
#   ip_version  = 4
#   enable_dhcp = true
#   allocation_pool {
#     start = "192.168.50.10"
#     end   = "192.168.50.254"
#   }
# }

# ## Create internal router interface
# resource "openstack_networking_router_interface_v2" "internal-router-interface" {
#   router_id = openstack_networking_router_v2.external-router.id
#   subnet_id = openstack_networking_subnet_v2.internal-subnet.id
# }
