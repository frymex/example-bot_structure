"""Utility functions for dealing with env variables and reading variables from env file"""
import os
import logging
import json

BOOLEAN_TYPE = 'boolean'
INT_TYPE = 'int'
FLOAT_TYPE = 'float'
STRING_TYPE = 'str'
LIST_TYPE = 'list'
DICT_TYPE = 'dict'


def get_envvars(env_file='.env', set_environ=True, ignore_not_found_error=False, exclude_override=()):
    """
    Set env vars from a file
    :param env_file:
    :param set_environ:
    :param ignore_not_found_error: ignore not found error
    :param exclude_override: if parameter found in this list, don't overwrite environment
    :return: list of tuples, env vars
    """
    env_vars = []
    try:

        with open(env_file) as f:
            for line in f:
                line = line.replace('\n', '')

                if not line or line.startswith('#'):
                    continue

                # Remove leading `export `
                if line.lower().startswith('export '):
                    key, value = line.replace('export ', '', 1).strip().split('=', 1)
                else:
                    try:
                        key, value = line.strip().split('=', 1)
                    except ValueError:
                        logging.error(f"envar_utils.get_envvars error parsing line: '{line}'")
                        raise

                if set_environ and key not in exclude_override:
                    os.environ[key] = value

                if key in exclude_override:
                    env_vars.append({'name': key, 'value': os.getenv(key)})
                else:
                    env_vars.append({'name': key, 'value': value})
    except FileNotFoundError:
        if not ignore_not_found_error:
            raise

    return env_vars


def create_envvar_file(env_file_path, envvars):
    """
    Writes envvar file using env var dict
    :param env_file_path: str, path to file to write to
    :param envvars: dict, env vars
    :return:
    """
    with open(env_file_path, "w+") as f:
        for key, value in envvars.items():
            f.write("{}={}\n".format(key, value))
    return True


class Enver:
    """ made by @cazqev for https://daty.me/ (kolibri)"""

    def __init__(self, **kwargs):
        self.env_vars: list = get_envvars(**kwargs)
        self.env_var_dict = self.__convert_to_dict()

    def __convert_to_dict(self) -> dict:
        r = {}
        for env_var in self.env_vars:
            r[env_var['name']] = env_var['value']
        return r

    def __get_env_var_flag_to(self, key, required_type, default_value):
        env_var_orginal_value = self.env_var_dict[key]
        env_var_value = default_value

        try:
            if required_type == INT_TYPE:
                env_var_value = int(env_var_orginal_value)
            elif required_type == FLOAT_TYPE:
                env_var_value = float(env_var_orginal_value)
            elif required_type == BOOLEAN_TYPE:
                env_var_value = bool(int(env_var_orginal_value))
            elif required_type == STRING_TYPE:
                env_var_value = str(env_var_orginal_value)
            elif required_type == LIST_TYPE:
                env_var_value = env_var_orginal_value.split(',') if len(env_var_orginal_value) > 0 else default_value
            elif required_type == DICT_TYPE:
                try:
                    env_var_value = json.loads(env_var_orginal_value) if env_var_orginal_value else default_value
                except Exception as e:
                    logging.error(f"self.__get_env_var_flag_to: failed loading {env_var_orginal_value} error {e}")
                    env_var_value = default_value
            else:
                logging.error("Unrecognized type {} for env var {}".format(required_type, key))

        except ValueError:
            env_var_value = default_value
            logging.warning("{} is {}".format(key, env_var_orginal_value))

        return env_var_value

    def str(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'str', default)

    def int(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'int', default)

    def list(self, key: str, default=None, default_type=str):
        values = self.__get_env_var_flag_to(key, 'list', default)
        casted = map(default_type, values)

        return list(casted)

    def dict(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'dict', default)

    def boolean(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'boolean', default)

    def float(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'float', default)

    def dict(self, key: str, default=None):
        return self.__get_env_var_flag_to(key, 'dict', default)