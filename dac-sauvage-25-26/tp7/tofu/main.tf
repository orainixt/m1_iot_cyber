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

variable "key_pair" {type = string}

variable "network_name" {
  type = string
  default = "prive" 
}


provider "openstack" {
  user_name   = var.os_username
  tenant_id   = var.os_project_id
  password    = var.os_password
  auth_url    = var.os_auth_url
  region      = var.os_region
}


data "openstack_images_image_v2" "debian" {
  name = "debian13" 
}

data "openstack_networking_network_v2" "network" {
  name = var.network_name
}

resource "openstack_compute_instance_v2" "control_panel" {
  name = "controle-panel" 
  image_id = data.openstack_images_image_v2.debian.id 
  flavor_name = "puissante" 
  key_pair = var.key_pair
  security_groups = ["default"] 

  network {
    uuid = data.openstack_networking_network_v2.network.id 
  }
  
  tags = ["cluster","vm_control_panel"]  
}

resource "openstack_compute_instance_v2" "nodes" {
  count = 2 
  name = "node-${count.index}"
  image_id = data.openstack_images_image_v2.debian.id 
  flavor_name = "normale" 
  key_pair = var.key_pair 
  security_groups = ["default"] 

  network {
    uuid = data.openstack_networking_network_v2.network.id 
  } 
  tags = ["cluster", "vm_nodes"] 
}
