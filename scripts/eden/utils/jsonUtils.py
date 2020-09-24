import os
import json

def save_dict_to_json(filepath, d):
    with open(filepath, 'w') as f:
        json.dump(d, f, sort_keys=True, indent=4)


def get_dict_from_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def list_json_files(dirpath):
    return [os.path.join(dirpath, f) for f in os.listdir(dirpath) if f.endswith(".json")]


def list_dicts_from_jsons(jsons):
    return [get_dict_from_json(f) for f in jsons]


def filter_dicts_by_key(dicts, key):
    return [d for d in dicts if key in d]


def filter_jsons_by_key(jsons, key):
    return [f for f in jsons if key in get_dict_from_json(f)]


def sort_dicts_by_key(dicts, key):
    filteredDicts = filter_dicts_by_key(dicts, key)
    return sorted(filteredDicts, key=lambda x: x[key])


def sort_jsons_by_key(jsons, key):
    filteredJsons = filter_jsons_by_key(jsons, key)
    dicts = list()
    for f in filteredJsons:
        d = get_dict_from_json(f)
        d["__filepath"] = f
        dicts.append(d)

    sortedDicts = sort_dicts_by_key(dicts, key)
    return [d["__filepath"] for d in sortedDicts]


if __name__ == "__main__":
    data1 = {"a": 1, "b": 30, "c": 300, "f": 1}
    filepath1 = "D:\\data\\test_dict1.json"

    data2 = {"a": 2, "b": 80, "c": 200, "f": 2}
    filepath2 = "D:\\data\\test_dict2.json"

    data3 = {"a": 5, "b": 50, "c": 100}
    filepath3 = "D:\\data\\test_dict3.json"

    save_dict_to_json(filepath1, data1)
    save_dict_to_json(filepath2, data2)
    save_dict_to_json(filepath3, data3)

    jsons1 = list_json_files("D:\\data")
    dicts1 = list_dicts_from_jsons(jsons1)

    # print sort_dicts_by_key(dicts1, "c")
    print sort_jsons_by_key(jsons1, "b")
