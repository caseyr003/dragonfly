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
            self._session = self._authenticate()

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
        items = request.json()['result']

        for item in items:
            items_list.append(item)

        return items_list

    def authenticate(self):
        """ Perform authentication and retrieve the cookie """

        path = '/authenticate/'

        try:
            self._session = requests.Session()
            request = self._session.post(self._url(path), json=self.auth_data, headers=self.headers)
            status = "Success"
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError) as error:
            status = error
            # socket error import
        if request.status_code == requests.codes.unauthorized: # pylint: disable=no-member
            status = "Authentication failed. Incorrect username/password"

        return status

    def list_instances(self):
        """ LIST instances in the container """
        path = '/instance/Compute-'+str(self.tenant)+'/'
        data = self._list(path)
        return data
