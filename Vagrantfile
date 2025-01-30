Vagrant.configure("2") do |config|
  config.vm.box = "debian/bookworm64"
#  config.vm.box_version = "12.20250126.1"
#  config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"
#  config.vm.network "private_network", ip: "192.168.33.10"
#  config.vm.synced_folder ".", "/vagrant", type: 'nfs'
  config.vm.provider :libvirt do |v|
    v.memory = 1024
  end
#  config.vm.provision "ansible" do |ansible|
#    ansible.verbose = "v"
#    ansible.playbook = "playbook.yml"
#  end
end

#Vagrant.configure("2") do |config|
#  config.vm.box = "debian/bookworm64"
#  config.vm.box_version = "12.20250126.1"
#end
