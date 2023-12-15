#!/usr/bin/python3

import os, sys, requests

from alibabacloud_alidns20150109.client import Client as alidns_client
from alibabacloud_tea_openapi import models as tea_openapi_models
from alibabacloud_alidns20150109 import models as alidns_models


class sc_ddns_records:
    def __init__(self, access_key_id : str, access_key_secret : str):
        self.__client_ctx = self.__create_client(
            access_key_id, access_key_secret)
        self.__ddns_records = self.__describe_domain_records(
            os.getenv('prefix'), os.getenv('domain_name'))

    def __create_client(self, access_key_id : str, access_key_secret : str):
        config = tea_openapi_models.Config(
            access_key_id = access_key_id,
            access_key_secret = access_key_secret
        )
        config.endpoint = f'alidns.cn-hangzhou.aliyuncs.com'
        return alidns_client(config)

    def __get_ipv4(self):
        i = 0
        while i < self.__ddns_records.body.total_count:
            domain = self.__ddns_records.body.domain_records.record[i]
            i += 1
            if domain.type == 'A':
                return domain.value
        return '0.0.0.0'

    def __get_ipv6(self):
        i = 0
        while i < self.__ddns_records.body.total_count:
            domain = self.__ddns_records.body.domain_records.record[i]
            i += 1
            if domain.type == 'AAAA':
                return domain.value
        return '::'

    def __get_ip4_record_id(self):
        i = 0
        while i < self.__ddns_records.body.total_count:
            domain = self.__ddns_records.body.domain_records.record[i]
            i += 1
            if domain.type == 'A':
                return domain.record_id
        return '0'

    def __get_ip6_record_id(self):
        i = 0
        while i < self.__ddns_records.body.total_count:
            domain = self.__ddns_records.body.domain_records.record[i]
            i += 1
            if domain.type == 'AAAA':
                return domain.record_id
        return '0'

    def __describe_domain_records(self, prefix : str, domain_name : str):
        get_record_ctx = alidns_models.DescribeDomainRecordsRequest(
            domain_name = domain_name, rrkey_word = prefix)
        return self.__client_ctx.describe_domain_records(get_record_ctx)

    def update_ddns_record_ipv4(self, prefix : str, ip_new : str):
        if ip_new == self.__get_ipv4():
            print('ddns ip4 not changed: ' + ip_new)
            return
        record_id = self.__get_ip4_record_id()
        update_ctx = alidns_models.UpdateDomainRecordRequest(
            record_id = record_id, rr = prefix, type = 'A', value = ip_new)
        self.__client_ctx.update_domain_record(update_ctx)

    def update_ddns_record_ipv6(self, prefix : str, ip_new : str):
        if ip_new == self.__get_ipv6():
            print('ddns ip6 not changed: ' + ip_new)
            return
        record_id = self.__get_ip6_record_id()
        update_ctx = alidns_models.UpdateDomainRecordRequest(
            record_id = record_id, rr = prefix, type = 'AAAA', value = ip_new)
        self.__client_ctx.update_domain_record(update_ctx)

    def __repr__(self):
        return self.__get_ipv4() + ', ' + self.__get_ip4_record_id()    \
            + '; ' + self.__get_ipv6() + ', ' + self.__get_ip6_record_id()

    def __str__(self):
        return self.__get_ipv4() + ', ' + self.__get_ip4_record_id()    \
            + '; ' + self.__get_ipv6() + ', ' + self.__get_ip6_record_id()


class sc_real_ip:
    def __init__(self):
        self.__ipv4_path = '/tmp/sc_ddns_ip4.tmp'
        self.__ipv6_path = '/tmp/sc_ddns_ip6.tmp'
        self.__str_ipv4 = ''
        self.__str_ipv6 = ''

        if not os.path.isfile(self.__ipv4_path):
            self.__create_file(self.__ipv4_path, '127.0.0.1')
        if not os.path.isfile(self.__ipv6_path):
            self.__create_file(self.__ipv6_path, '::1')

        self.__read_all_ip4()
        self.__read_all_ip6()

    def get_real_ip4(self):
        return requests.get('https://speed4.neu6.edu.cn/getIP.php').text

    def get_real_ip6(self):
        return requests.get('https://speed.neu6.edu.cn/getIP.php').text

    def is_ip4_changed(self):
        real_ip = self.get_real_ip4()
        if real_ip != self.__str_ipv4:
            self.__str_ipv4 = real_ip
            return True
        return False

    def is_ip6_changed(self):
        real_ip = self.get_real_ip6()
        if real_ip != self.__str_ipv6:
            self.__str_ipv6 = real_ip
            return True
        return False

    def get_ip4(self):
        return self.__str_ipv4

    def get_ip6(self):
        return self.__str_ipv6

    def __create_file(self, path, file_str):
        f = open(path, 'w')
        f.write(file_str + '\n')
        f.close()

    def __repr__(self):
        return self.__str_ipv4 + ', ' + self.__str_ipv6

    def __str__(self):
        return self.__str_ipv4 + ', ' + self.__str_ipv6

    def __read_all_ip4(self):
        f = open(self.__ipv4_path, 'r+')
        self.__str_ipv4 = f.readline().strip('\r\n\t ')
        f.close()

    def __read_all_ip6(self):
        f = open(self.__ipv6_path, 'r+')
        self.__str_ipv6 = f.readline().strip('\r\n\t ')
        f.close()

    def write_all_ip4(self):
        f = open(self.__ipv4_path, 'w')
        f.write(self.__str_ipv4.strip('\r\n\t ') + '\n')
        f.close()

    def write_all_ip6(self):
        f = open(self.__ipv6_path, 'w')
        f.write(self.__str_ipv6.strip('\r\n\t ') + '\n')
        f.close()


if __name__ == '__main__':
    ipv4_changed = False
    ipv6_changed = False
    real_ip = sc_real_ip()
    if True != real_ip.is_ip4_changed():
        print('IP4 NOT changed: ' + real_ip.get_ip4())
    else:
        ipv4_changed = True
        print('IP4 changed: ' + real_ip.get_ip4())

#     if True != real_ip.is_ip6_changed():
    if True:
        print('IP6 NOT changed: ' + real_ip.get_ip6())
    else:
        ipv6_changed = True
        print('IP6 changed: ' + real_ip.get_ip6())

    if False == ipv4_changed and False == ipv6_changed:
        sys.exit(0)

    sc_ddns = sc_ddns_records(
        os.getenv('access_key_id'), os.getenv('access_key_secret'))
    if False != ipv4_changed:
        sc_ddns.update_ddns_record_ipv4(os.getenv('prefix'), real_ip.get_ip4())
        real_ip.write_all_ip4()
    if False != ipv6_changed:
        sc_ddns.update_ddns_record_ipv6(os.getenv('prefix'), real_ip.get_ip6())
        real_ip.write_all_ip6()

    sys.exit(0)
