import json
import os
import time
import oci
from oci.object_storage.transfer.constants import MEBIBYTE


class Account:
    def __init__(self, name, tenancy_ocid, user_ocid, region, fingerprint, key_location, vm_list):
        self.name = name
        self.tenancy_ocid = tenancy_ocid
        self.user_ocid = user_ocid
        self.region = region
        self.fingerprint = fingerprint
        self.key_location = key_location
        self.vm_list = vm_list

    def get_json(self):
        return {
            'name': self.name,
            'tenancy_ocid': self.tenancy_ocid,
            'user_ocid': self.user_ocid,
            'region': self.region,
            'fingerprint': self.fingerprint,
            'key_location': self.key_location,
            'vms': self.vm_list
        }

    def save_account(self, data_file):
        if os.stat(data_file).st_size == 0:
            with open(data_file, 'w') as data_file:
                json.dump({"accounts":[self.get_json()]}, data_file, indent=2)
        else:
            with open(data_file, 'r') as read_data:
                data = json.load(read_data)

            data["accounts"].append(self.get_json())

            with open(data_file, 'w') as write_data:
                json.dump(data, write_data, indent=2)

    def config_account(self, config_file):
        config = open(config_file, 'w')
        config.seek(0)
        config.truncate()
        config.write('[DEFAULT]\n')
        config.write('user=%s\n' % self.user_ocid)
        config.write('fingerprint=%s\n' % self.fingerprint)
        config.write('key_file=%s\n' % self.key_location)
        config.write('tenancy=%s\n' % self.tenancy_ocid)
        config.write('region=%s\n' % self.region)
        config.close()

    def is_active(self, config_file):
        self.config_account(config_file)

        success = False
        try:
            config = oci.config.from_file(file_location=config_file)
            identity = oci.identity.IdentityClient(config)
            user = identity.get_user(config["user"])
            print user.data.name
            print user.data.description
            print user.data.lifecycle_state
            success = True
        except:
            print "An Error Occured"

        return success

    def get_compartments(self, config_file):
        config = oci.config.from_file(file_location=config_file)

        # Store compartments in array to return
        compartment_array = []
        # Get identity store for region and compartment
        identity_store = oci.identity.identity_client.IdentityClient(config)
        # Select compartment for compute
        compartment_res = identity_store.list_compartments(compartment_id=self.tenancy_ocid)
        compartment_list = compartment_res.data
        for x in compartment_list:
            compartment = Compartment(x.id, x.name)
            compartment_array.append(compartment)
        return compartment_array

    def get_buckets(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)
        bucket_array = []
        obj_store = oci.object_storage.ObjectStorageClient(config)
        namespace = obj_store.get_namespace().data
        try:
            bucket_res = obj_store.list_buckets(namespace_name=namespace, compartment_id=compartment_id)
            bucket_list = bucket_res.data
        except:
            print "probably don't have access to compartment"
            return [[], False]

        for x in bucket_list:
            bucket = Bucket(x.name)
            bucket_array.append(bucket)
        return [bucket_array, True]

    def get_availability_domains(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        ad_array = []
        identity_store = oci.identity.identity_client.IdentityClient(config)

        ad_list = identity_store.list_availability_domains(compartment_id=compartment_id).data
        for x in ad_list:
            ad = AvailabilityDomain(x.name)
            ad_array.append(ad)
        return ad_array

    def get_vcns(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        vcn_array = []
        vnc_store = oci.core.virtual_network_client.VirtualNetworkClient(config)

        vcn_list = vnc_store.list_vcns(compartment_id=compartment_id).data
        for x in vcn_list:
            vcn = VirtualCloudNetwork(x.id, x.display_name)
            vcn_array.append(vcn)
        return vcn_array

    def get_subnets(self, config_file, compartment_id, vcn_id):
        config = oci.config.from_file(file_location=config_file)

        subnet_array = []
        vnc_store = oci.core.virtual_network_client.VirtualNetworkClient(config)

        subnet_list = vnc_store.list_subnets(compartment_id=compartment_id, vcn_id=vcn_id).data
        for x in subnet_list:
            subnet = Subnet(x.id, x.display_name)
            subnet_array.append(subnet)
        return subnet_array

    def get_shapes(self, config_file, compartment_id):
        config = oci.config.from_file(file_location=config_file)

        shape_array = []
        compute_store = oci.core.compute_client.ComputeClient(config)

        shape_list = compute_store.list_shapes(compartment_id=compartment_id).data
        for x in shape_list:
            shape = Shape(x.shape)
            shape_array.append(shape)
        return shape_array

    def upload_image(self, config_file, bucket_name, file_name, file_path):
        success = False

        config = oci.config.from_file(file_location=config_file)
        obj_store = oci.object_storage.ObjectStorageClient(config)
        namespace = obj_store.get_namespace().data
        region = self.region
        part_size = 1000 * MEBIBYTE
        upload_man = oci.object_storage.UploadManager(obj_store, allow_parallel_uploads=True,
                                                      parallel_process_count=3)
        print 'Starting upload to OCI object storage...'
        try:
            upload_res = upload_man.upload_file(namespace, bucket_name, file_name,
                                                file_path, part_size=part_size,
                                                progress_callback=self.progress_callback)
            success = True
        except:
            print "Error Occurred during image upload"

        return [success, namespace]

    def create_image(self, config_file, namespace, bucket_name, file_name, display_name, image_type, compartment_id):

        region = self.region
        launch_mode="EMULATED"
        success = False
        config = oci.config.from_file(file_location=config_file)
        compute_store = oci.core.compute_client.ComputeClient(config)
        source_uri="https://objectstorage.%s.oraclecloud.com/n/%s/b/%s/o/%s" % (region, namespace, bucket_name, file_name)

        print 'Starting image import from object storage...'
        image_source_details = oci.core.models.ImageSourceViaObjectStorageUriDetails(source_image_type=image_type,
                                                                                     source_type="objectStorageUri",
                                                                                     source_uri=source_uri)
        create_image_details = oci.core.models.CreateImageDetails(compartment_id=compartment_id,
                                                                  display_name=display_name,
                                                                  image_source_details=image_source_details,
                                                                  launch_mode=launch_mode)
        try:
            create_image_res = compute_store.create_image(create_image_details=create_image_details)
            image_id=create_image_res.data.id
            image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state
            while image_status != "AVAILABLE":
                if image_status != "IMPORTING":
                    print "Error occured while importing custom image"
                    return [success, image_id]
                time.sleep(20)
                image_status = compute_store.get_image(image_id=image_id).data.lifecycle_state
                print image_status
        except:
            print "Error importing image."
            return [success, "failed"]

        success = True
        return [success, image_id]

    def progress_callback(self, bytes_uploaded):
        print "uploading"

    def provision_vm(self, config_file, subnet_id, ad_name, compartment_id, display_name, image_id, shape):

        success = False
        config = oci.config.from_file(file_location=config_file)
        compute_store = oci.core.compute_client.ComputeClient(config)
        create_vnic_details = oci.core.models.CreateVnicDetails(subnet_id=subnet_id)
        launch_instance_details = oci.core.models.LaunchInstanceDetails(availability_domain=ad_name,
                                                                        compartment_id=compartment_id,
                                                                        create_vnic_details=create_vnic_details,
                                                                        display_name=display_name,
                                                                        image_id=image_id,
                                                                        shape=shape)

        try:
            create_vm_res = compute_store.launch_instance(launch_instance_details=launch_instance_details)
            instance_id = create_vm_res.data.id
            instance_status = compute_store.get_instance(instance_id=instance_id).data.lifecycle_state
            print 'Provisioning instance...'
            while instance_status != "RUNNING":
                if instance_status != "PROVISIONING":
                    print 'An error occured while provisioning the server'
                    return [success, instance_id]
                time.sleep(20)
                instance_status = compute_store.get_instance(instance_id=instance_id).data.lifecycle_state
                print 'Provisioning instance... \r'
        except:
            print "Failed during image provisioning"
            return [success, "failed"]

        try:
            vnic_res = compute_store.list_vnic_attachments(compartment_id=compartment_id, instance_id=instance_id)
            vnic_id = vnic_res.data[0].vnic_id
            vcn_store = oci.core.virtual_network_client.VirtualNetworkClient(config)
            vnic_instance = vcn_store.get_vnic(vnic_id=vnic_id)
            instance_ip = vnic_instance.data.public_ip
        except:
            print "Failed to get IP for instance"
            return [success, "failed"]

        print 'Instance successfully created'
        print 'Your image is now running in Oracle Cloud Infrastructure'
        print 'Public IP: %s' % instance_ip

        success = True
        return [success, instance_id, instance_ip]

    def get_instance_status(self, instance_id, config_file):
        config = oci.config.from_file(file_location=config_file)
        compute_store = oci.core.compute_client.ComputeClient(config)
        instance_status = compute_store.get_instance(instance_id=instance_id).data.lifecycle_state
        return instance_status

    def add_vm(self, data_file, index, name, ocid, ip, status):
        new_vm = {
            'name': name,
            'ocid': ocid,
            'ip': ip,
            'status': status,
            'complete': False,
            'failed': False
        }
        with open(data_file, 'r') as read_data:
            data = json.load(read_data)

        vm_index = len(data["accounts"][index]["vms"])
        print vm_index

        data["accounts"][index]["vms"].append(new_vm)

        with open(data_file, 'w') as write_data:
            json.dump(data, write_data, indent=2)

        return vm_index

    def update_vm(self, data_file, index, ocid, ip, status, complete, failed, vm_index):
        with open(data_file, 'r') as read_data:
            data = json.load(read_data)

        data["accounts"][index]["vms"][vm_index]["ocid"] = ocid
        data["accounts"][index]["vms"][vm_index]["ip"] = ip
        data["accounts"][index]["vms"][vm_index]["status"] = status
        data["accounts"][index]["vms"][vm_index]["complete"] = complete
        data["accounts"][index]["vms"][vm_index]["failed"] = failed

        with open(data_file, 'w') as write_data:
            json.dump(data, write_data, indent=2)

    def update_vm_status(self, data_file, index, status, complete, failed, vm_index):
        with open(data_file, 'r') as read_data:
            data = json.load(read_data)

        data["accounts"][index]["vms"][vm_index]["status"] = status
        data["accounts"][index]["vms"][vm_index]["complete"] = complete
        data["accounts"][index]["vms"][vm_index]["failed"] = failed

        with open(data_file, 'w') as write_data:
            json.dump(data, write_data, indent=2)
