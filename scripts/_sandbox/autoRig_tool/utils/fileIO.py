import os


def get_files_by_type(directory, ext):
    result = list()
    for f in os.listdir(directory):
        if f.endswith(ext):
            result.append(f)
    result.sort()

    return result


def get_folders_in_directory(directory):
    return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]


def get_increment_file_path(directory, prefix, ext):
    last_version = 0

    files = get_files_by_type(directory, ext)

    if files:
        last_version = int(files[-1].split(".")[0].split("_v")[-1])

    file_name = "%s_v%03d.%s" % (prefix, (last_version + 1), ext)

    result = os.path.abspath(os.path.join(directory, file_name))

    return result
