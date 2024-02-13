#!/usr/bin/python3

import os, sys, getopt, requests, json

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
        self.__real_ipv4_str = ''
        self.__real_ipv6_str = ''

        if not os.path.isfile(self.__ipv4_path):
            self.__create_file(self.__ipv4_path, '127.0.0.1')
        if not os.path.isfile(self.__ipv6_path):
            self.__create_file(self.__ipv6_path, '::1')

        self.__read_all_ip4()
        self.__read_all_ip6()
        self.__get_firewall_status(os.getenv('opnsense_domain'))

    def __get_firewall_status(self, url : str):
        try:
            a = '{}/api/diagnostics/interface/getInterfaceConfig'.format(url)
            b = requests.get(a, verify = os.getenv('opnsense_verify'),
                             auth = (os.getenv('opnsense_key'), os.getenv('opnsense_secret')),
                             timeout = (5, 5)).text
            c = json.loads(b)
            d = c['pppoe0']['ipv4']
            e = c['pppoe0']['ipv6']

            for obj in d:
                self.__real_ipv4_str = obj.get('ipaddr')

            for obj in e:
                if False != obj.get('deprecated'):
                    continue
                if False != obj.get('tentative'):
                    continue
                if False != obj.get('link-local'):
                    continue
                self.__real_ipv6_str = obj.get('ipaddr')

        except:
            print('get firewall ip status failed')
            sys.exit(-1)

    def get_real_ip4(self):
        # 此函数用于获取公网IPv4地址，此处给出模板，可以自己实现
        if '' != self.__real_ipv4_str:
            return self.__real_ipv4_str
        return '127.0.0.1'

    def get_real_ip6(self):
        # 此函数用于获取公网IPv6地址，此处给出模板，可以自己实现
        if '' != self.__real_ipv6_str:
            return self.__real_ipv6_str
        return '::1'

    def is_ip4_changed(self):
        real_ip = self.get_real_ip4()
        if (real_ip != self.__str_ipv4) and ('127.0.0.1' != real_ip):
            self.__str_ipv4 = real_ip
            return True
        return False

    def is_ip6_changed(self):
        real_ip = self.get_real_ip6()
        if (real_ip != self.__str_ipv6) and ('::1' != real_ip):
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
    opt_flag_use_ipv4 = False
    opt_flag_use_ipv6 = False
    ipv4_changed = False
    ipv6_changed = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], '?h46', ['ipv4', 'ipv6'])
    except:
        print("unknow opts")
        sys.exit(-1)
    
    for opt, args in opts:
        if ('-h' == opt) or ('-?' == opt):
            sys.exit(0)
        elif opt in ('-4', '--ipv4'):
            opt_flag_use_ipv4 = True
        elif opt in ('-6', '--ipv6'):
            opt_flag_use_ipv6 = True

    real_ip = sc_real_ip()

    # 若没有指定使用IPv4或IPv6，默认更新全部
    if (True != opt_flag_use_ipv4) and (True != opt_flag_use_ipv6):
        opt_flag_use_ipv4 = True
        opt_flag_use_ipv6 = True

    # 若需要更新IPv4
    if True == opt_flag_use_ipv4:
        ipv4_changed = real_ip.is_ip4_changed()
        if True != ipv4_changed:
            print('IPv4 NOT changed: ' + real_ip.get_ip4())
        else:
            print('IPv4 changed: ' + real_ip.get_ip4())

    # 若需要更新IPv6
    if True == opt_flag_use_ipv6:
        ipv6_changed = real_ip.is_ip6_changed()
        if True != ipv6_changed:
            print('IPv6 NOT changed: ' + real_ip.get_ip6())
        else:
            print('IPv6 changed: ' + real_ip.get_ip6())

    # ip地址没有更改 or 不需要更新，反正不需要执行升级操作的，直接退出
    if (False == ipv4_changed) and (False == ipv6_changed):
        sys.exit(0)

    # 创建sc_ddns_records对象后，会与阿里云建立连接。
    # 本着只建立必要连接的原则，在必须使用的情况下才建立连接
    sc_ddns = sc_ddns_records(
        os.getenv('access_key_id'), os.getenv('access_key_secret'))
    if False != ipv4_changed:
        sc_ddns.update_ddns_record_ipv4(os.getenv('prefix'), real_ip.get_ip4())
        real_ip.write_all_ip4()
    if False != ipv6_changed:
        sc_ddns.update_ddns_record_ipv6(os.getenv('prefix'), real_ip.get_ip6())
        real_ip.write_all_ip6()

    sys.exit(0)
