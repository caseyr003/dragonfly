'''
Created on June 4, 2018

@author: caseyr003
Thanks to the OCI PM team for providing most functions used in this class
'''

import requests
from logzero import logger


class ClassicAPI(object):
    """
    Compute Classic API Class
    """

    def __init__(self, tenant, username, password, api_host):
        """
        Initialize
        """
        self.tenant = tenant
        self.username = username
        self.password = password
        self.api_host = api_host
        self.headers = {'Content-Type': 'application/oracle-compute-v3+json'}

        self.auth_data = {
            'user': self.username,
            'password': self.password
        }

        self._session = None

    def _url(self, path):
        """ Create a URL """
        return str("https://"+self.api_host+path)

    def _call(self, method, path, **kwargs):
        """ Make HTTP request """

        post_data = kwargs.get('data')
        json_data = kwargs.get('json')

        url = self._url(path)

        session = self._session

        request_data = session.prepare_request(
            requests.Request(
                method,
                url,
                data=post_data,
                json=json_data,
                headers=self.headers,
                cookies=session.cookies
                )
            )

        request = session.send(request_data)
        # logger.debug('request: ' +str(request_data.url) + ' <'+str(request.status_code) + '> ')

        if request.status_code == requests.codes.unauthorized: # pylint: disable=no-member
            self._session, code, status_msg = self.authenticate()

            session = self._session

            request_data = session.prepare_request(
                requests.Request(
                    method,
                    url,
                    data=post_data,
                    headers=self.headers,
                    cookies=session.cookies
                    )
                )

            request = session.send(request_data)

        return request

    def _list(self, path):
        """ Get used to retrieve list instead of single object """

        items_list = []

        method = 'GET'
        request = self._call(method, path)
        if 'result' in request.json():
            items = request.json()['result']
        else:
            return 1, "Failed to retrieve list"

        for item in items:
            items_list.append(item)

        return 0, items_list

    def _get(self, path):
        """ Get Object """
        method = 'GET'
        try:
            request = self._call(method, path).json()
        except Exception as error:
            logger.error(error)
            return None
            #request = self._call(method, path)

        dictionary = {}
        for item, value in request.items():
            dictionary[item] = value

        return dictionary

    def authenticate(self):
        """ Perform authentication and retrieve the cookie """

        path = '/authenticate/'

        try:
            self._session = requests.Session()
            request = self._session.post(self._url(path), json=self.auth_data, headers=self.headers)
            status_msg = "Authentication successful"
            code = 0

        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError) as error:
            status_msg = "Authentication failed." + error
            code = 1
            # socket error import
        if request.status_code == requests.codes.unauthorized: # pylint: disable=no-member
            status_msg = "Authentication failed. Incorrect username/password"
            code = 2

        return self._session, code, status_msg

    def list_instances(self):
        """ LIST instances in the container """
        path = '/instance/Compute-'+str(self.tenant)+'/'
        code, data = self._list(path)
        return code, data

    def get_instance(self, name):
        """ LIST instance details """
        path = '/instance'+str(name)
        data = self._get(path)
        return data

    def get_storage_volume(self, name):
        """ GET storage snapshots details """
        path = '/storage/volume'+str(name)
        try:
            data = self._get(path)
        except:
            raise

        return data

    def get_boot_volume(self, instance):
        """Returns information about boot enabled disks of the instance """
        boot_disk = None

        instance_details = self.get_instance(instance)

        if not instance_details or 'message' in instance_details:
            return 2, "Instance Not Found", {}

        if 'storage_attachments' in instance_details:

            disk_count = int(len(instance_details.get('storage_attachments')))
            if disk_count > 0:
                bootable_count = 0
                for disk in instance_details.get('storage_attachments'):
                    if 'volume' in disk:
                        disk_details = self.get_storage_volume(disk.get('volume'))
                    if 'storage_volume_name' in disk:
                        disk_details = self.get_storage_volume(disk.get('storage_volume_name'))

                    if disk_details.get('bootable'):
                        bootable_count = bootable_count + 1
                        boot_disk = disk_details

                    # print('Disk ' + str(disk.get('index')) + \
                    #              ' size: ' + str(int(disk_details.get('size')) / 1073741824) + 'GB' + \
                    #              ' bootable: ' + str(disk_details.get('bootable')))


                if int(boot_disk.get('size')) > 274877906944:
                    return 1, "Instance boot disk is too large", {}

                if bootable_count > 1:
                    return 1, "Instances with more than 1 bootable disk are not supported", {}

                if bootable_count == 0:
                    return 1, "No disks detected", {}

            else:
                return 1, "No disks detected", {}

            return 0, "Successfully retrieved boot disk", boot_disk
