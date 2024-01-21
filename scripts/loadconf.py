
import pprint

printer = pprint.PrettyPrinter(indent= 4)

def conf_to_dict(confpath):
    conf = {}
    with open(confpath, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            parts = line.split(' ', 1)
            # print(parts)
            name, value = parts[0], parts[1]
            name = name.lower()
            if name not in conf:
                conf[name] = value
            else:
                exist_value = conf[name]
                if isinstance(exist_value, (list, tuple)):
                    exist_value.append(value)
                else:
                    conf[name] = [exist_value, value]
    return conf



if __name__ == '__main__':
    printer.pprint(conf_to_dict('./redis.conf'))