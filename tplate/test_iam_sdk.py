#!/usr/bin/env python
#API Connection
import sys
sys.path.insert(0, r'/root/iam/qingcloud-sdk-python')
import unittest
import csv
from qingcloud.iaas import APIConnection
import os
from json import dumps
import warnings


class TestIAM(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)
        self.host = "api.alphacloud.com"
        self.port = 80
        self.protocol = "http"
        self.zone = 'test'
        self.credential_proxy_host='169.254.169.254'
        self.credential_proxy_port=80
        # self.qy_access_key_id = ''
        # self.qy_secret_access_key = ''

        # init connection
        self.conn = APIConnection(host=self.host,
                                  port=self.port,
                                  protocol=self.protocol,
                                  zone=self.zone,
                                  credential_proxy_host=self.credential_proxy_host,
                                  credential_proxy_port=self.credential_proxy_port)

    def tearDown(self):
        pass

    def test_action(self):
        # got all the interface and the params defined
        data_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], r"../template/iaas.csv")
        print("current script path is {}".format(data_path))

        with open(data_path, "r") as f:
            interface_defined = csv.DictReader(f)
            error_interfaces = []
            ERROR_FLAG = []
            for interface in interface_defined:
                action = interface['id']
                params = '{'
                # require_params = interface['requiredResources'].split(sep=',')
                require_params = eval(interface['requiredResources'])
                # print("require_params is : {}".format(require_params) )
                # optional_params = interface['optionalResources'].split(sep=',')
                optional_params = eval(interface['optionalResources'])
                # print("optional_params is : {}".format(optional_params))

                # got required params
                # print('begin to get params...')
                for i in require_params:
                    if i:
                        # print('getting require_params "{}"'.format(i))
                        params += ('"' + '{}'.format(i) + '"' + ':' + 'null,')
                for j in optional_params:
                    if j:
                        # print('getting optional_params "{}"...'.format(j))
                        params += ('"' + '{}'.format(j) + '"' + ':' + 'null,')
                new_params = params.rstrip(',')
                new_params += '}'
                # print(new_params)

                params_dict = dumps(new_params)
                # show the params
                print('interface {}\'s parameters are : {}'.format(action, params_dict))

                # send request
                response = self.conn.send_request(action=action,
                                       body=params_dict)

                # init interface store list and dict
                error_interface = {}

                # add interface and ret error code to dictionary
                if response['ret_code'] != 0 and response['ret_code'] not in ERROR_FLAG:
                    ERROR_FLAG.append(response['ret_code'])
                    error_interface['ret_code'] = response['ret_code']
                    error_interface['interfaces'] = []
                    error_interfaces.append(error_interface)
                if response['ret_code'] in ERROR_FLAG:
                    # print(action, params_dict)
                    for i in error_interfaces:
                        if i['ret_code'] == response['ret_code']:
                            del error_interfaces[error_interfaces.index(i)]
                            i['interfaces'].append(action)
                            error_interfaces.append(i)
                            print('interface {}\'s ret_code : {}, message : {}'.format(action,
                                                                                       response['ret_code'],
                                                                                       response['message']))

            print('There are {} ret codes : {}'.format(len(ERROR_FLAG), ERROR_FLAG))
            for i in error_interfaces:
                print("There are {} error interfaces with error_code {}: {}".format(len(i['interfaces']),
                                                                                    i['ret_code'],
                                                                                    i['interfaces']))


if __name__ == '__main__':
    unittest.main()
