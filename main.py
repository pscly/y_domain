# yaml
# from yaml import load, dump
# from json import dump, load
import yaml
import json
from addict import Dict
from ym import TXCloud


def load_yaml_file(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def save_dict_to_json_file(dict_data, file_name):
    with open(file_name, "w", encoding='utf-8') as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    y_config = Dict(load_yaml_file('y_data.yaml'))['COMMON']
    tx1 = TXCloud(y_config.DNS_SID, y_config.DNS_SKEY)

    # x = tx1.get_domain_list()
    x = tx1.get_duan_domain_list()
    save_dict_to_json_file(tx1.y.duan_domain_list, 'TX_duan.json')
    save_dict_to_json_file(tx1.y.all_dict, 'TX_chang.json')
