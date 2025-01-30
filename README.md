# Lamp Tracker

## Run it yourself
1. Use a GNU/Linux machine. The project maintainers run [Debian](https://www.debian.org) and some piece of arcane garbage on their development machines. We do not yet support MacOS, Windows, Haiku, 9Front, etc., but invite contributions to development environment documentation.
1. Clone this repository.
1. Install dependencies on your local machine:
   * **Debian**: apt install `vagrant-libvirt` `libvirt-daemon-system` `virt-manager` `ansible`
   * **Ubuntu**: `qemu-kvm` `libvirt-clients` `libvirt-daemon-system` `bridge-utils` `libguestfs-tools` `genisoimage` `virtinst` `lobosinfo-bin` `virt-manager`
1. Next, you will need to add your user to these groups:
    - **Debian** : `libvirt` `libvirt-qemu`
    - **Ubuntu** : `libvirtd` `kvm`
1. Reboot your computer. If you have issues with the libvirt setup, check out [this CTT video](https://www.youtube.com/watch?v=ozYKkaVK0_A).
1. In the project root, create a file called 'vagrant_ansible_vars.yml' with this content:
    ```
    ---
    fqdn: "localhost"
    secret_key: "A RANDOMLY GENERATED SECRET THAT YOU DO NOT SHARE"
    mapbox_api_key: "YOUR MAPBOX API KEY"
    db_password: "A RANDOMLY GENERATED PASSWORD"
    ```
    (Please note that you must replace everything in quotes with your own data.)

1. Run `vagrant up` then `vagrant provision` to set up and run the included Vagrant box
1. Visit http://localhost:8080 to ensure the site is working properly.

## Troubleshooting
- If, after nuking the local repo in a git mishap, `vagrant up` presents `Name <vagrant-domain-name> of domain about to create is already taken. Please try to run
'vagrant up' command again.`:
    - run `vagrant box remove <boxname>`
    - run `sudo virsh undefine <vagrant-domain-name>`
    - run `vagrant up` again
