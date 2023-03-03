import json
from addict import Dict
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models


class TXCloud():
    def __init__(self, sid, skey):
        self.config = Dict({
            "SecretId": sid,
            "SecretKey": skey,
        })
        self.y = Dict()

        # self.y.duan_domain_list    # 短的域名列表

        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        self.cred = credential.Credential(
            self.config.SecretId, self.config.SecretKey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        self.httpProfile = HttpProfile()
        self.httpProfile.endpoint = "dnspod.tencentcloudapi.com"  # 指定接入地域域名（默认就近接入）

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        self.clientProfile = ClientProfile()
        self.clientProfile.httpProfile = self.httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        self.client = dnspod_client.DnspodClient(
            self.cred, "", self.clientProfile)

    def get_one_domain_data(self, domain_name):
        try:
            req = models.DescribeRecordListRequest()
            params = {
                "Domain": domain_name
            }
            req.from_json_string(json.dumps(params))
            # 返回的resp是一个DescribeRecordListResponse的实例，与请求对象对应
            resp = self.client.DescribeRecordList(req)
            # 输出json格式的字符串回包

            # print(resp.to_json_string())
            # 将resp转换为字典对象然后放入对应的 self.y.all_dict[self.y.n_id[domain_name]]["ym_jl"] 中
            r_dict1 = Dict()
            resp_data = resp.RecordList

            for i in resp_data:
                d = Dict({
                    "Name": i.Name,
                    "RecordId": i.RecordId,
                    "Type": i.Type,
                    "Value": i.Value,
                    "Status": i.Status,
                    "UpdatedOn": i.UpdatedOn,
                    "row_data": i.__dict__
                })
                r_dict1[str(i.RecordId)] = d
                self.y.ym_jl[domain_name][str(i.RecordId)] = d

            # self.y.all_dict[self.y.n_id[domain_name]]["ym_jl"] = r_dict1
            return r_dict1

        except TencentCloudSDKException as err:
            print(err)

    def get_domain_list(self):
        r_dict = Dict()
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
            # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
            req = models.DescribeDomainListRequest()
            params = {

            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个DescribeDomainListResponse的实例，与请求对象对应
            resp = self.client.DescribeDomainList(req)
            # 输出json格式的字符串回包
            r_list = resp.DomainList
            # ok_list = [i for i in  r_list if i.Status == 'ENABLE']
            # old_list = [i for i in  r_list if i.Status == 'DISABLE']
            # {"657226221": {
            #   "DomainId": 657226221,
            #   "Name": "pscly.cn",
            #   "Status": "ENABLE",   # or "PAUSE"
            #   "UpdatedOn": "2021-03-23 15:00:00",
            #   "row_data": {...}
            # },
            # ....
            # }
            self.y.n_id = Dict()
            for i in r_list:
                self.y.n_id[i.Name] = str(i.DomainId)    # 用域名作为key，方便以后的操作
                r_dict[str(i.DomainId)] = Dict({
                    "DomainId": i.DomainId,
                    "Name": i.Name,
                    "Status": i.Status,
                    "UpdatedOn": i.UpdatedOn,
                    "row_data": i.__dict__
                })

            for i in r_dict:
                r_dict[i].ym_jl = self.get_one_domain_data(r_dict[i].Name)
            self.y.all_dict = r_dict
            return Dict(r_dict)  # 我多写了一遍
        except TencentCloudSDKException as err:
            print(err)

    def get_duan_domain_list(self):
        datas = self.get_domain_list()
        r_data = Dict()
        tmp_data1 = Dict()     # 临时存储方便后面使用
        for data_id in datas:
            data = datas[data_id]
            r_data[data.Name] = Dict({
                "Name": data.Name,
                "Status": data.Status,
                "DomainId": data.DomainId,
            })

            for t_data1 in data.ym_jl:
                t_data2 = data.ym_jl[t_data1]
                if (str(t_data2['Name']) in ['@']) or (t_data2['Type'] not in ['CNAME', 'AAAA', 'A']):
                    continue
                r_data[data.Name]['ym_jl'][t_data2.Name] = Dict({
                    "Name": t_data2.Name,
                    "RecordId": t_data2.RecordId,
                    "Type": t_data2.Type,
                    "Value": t_data2.Value,
                    "Status": t_data2.Status,
                    "UpdatedOn": t_data2.UpdatedOn,
                })
        self.y.duan_domain_list = r_data
        return r_data


if __name__ == '__main__':

    tx = TXCloud("xxx",
                "xxx")
    # x = tx.get_domain_list()
    x = tx.get_duan_domain_list()
    print(f'x: {x}')
    print(f'x: {x}')
