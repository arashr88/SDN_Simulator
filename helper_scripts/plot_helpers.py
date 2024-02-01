import os
import json
import numpy as np
from statistics import mean

from helper_scripts.sim_helpers import dict_to_list
from arg_scripts.plot_args import empty_plot_dict


# TODO: Move needed variables to the constructor
class PlotHelpers:
    def __init__(self, plot_props: dict):
        self.plot_props = plot_props

        self.file_info = None

    # TODO: Definitely make this better
    def _find_misc_stats(self):
        path_lens = self._dict_to_list(self.erlang_dict['misc_stats'], 'mean', ['path_lengths'])
        hops = self._dict_to_list(self.erlang_dict['misc_stats'], 'mean', ['hops'])
        times = self._dict_to_list(self.erlang_dict['misc_stats'], 'route_times') * 10 ** 3

        cong_block = self._dict_to_list(self.erlang_dict['misc_stats'], 'congestion', ['block_reasons'])
        dist_block = self._dict_to_list(self.erlang_dict['misc_stats'], 'distance', ['block_reasons'])

        average_len = np.mean(path_lens)
        average_hop = np.mean(hops)
        average_times = np.mean(times)
        average_cong_block = np.mean(cong_block)
        average_dist_block = np.mean(dist_block)

        self.plot_dict[self.time][self.sim_num]['path_lengths'].append(average_len)
        self.plot_dict[self.time][self.sim_num]['hops'].append(average_hop)
        self.plot_dict[self.time][self.sim_num]['route_times'].append(average_times)
        self.plot_dict[self.time][self.sim_num]['cong_block'].append(average_cong_block)
        self.plot_dict[self.time][self.sim_num]['dist_block'].append(average_dist_block)

    @staticmethod
    def _dict_to_np_array(snap_val_list: list, key: str):
        return np.nan_to_num([d.get(key, np.nan) for d in snap_val_list])

    def _process_snapshots(self, snap_val_list: list):
        active_req_list, block_req_list, occ_slot_list = [], [], []
        active_req_list.append(self._dict_to_np_array(snap_val_list=snap_val_list, key='active_requests'))
        block_req_list.append(self._dict_to_np_array(snap_val_list=snap_val_list, key='blocking_prob'))
        occ_slot_list.append(self._dict_to_np_array(snap_val_list=snap_val_list, key='occ_slots'))

        return active_req_list, block_req_list, occ_slot_list

    def _find_snapshot_usage(self, erlang_dict: dict, time: str, sim_num: str):
        req_num_list, active_req_matrix, block_req_matrix, occ_slot_matrix = [], [], [], []
        for iteration, stats_dict in erlang_dict['iter_stats'].items():
            snapshots_dict = stats_dict['snapshots_dict']
            req_num_list = [int(req_num) for req_num in snapshots_dict.keys()]

            snap_val_list = list(snapshots_dict.values())
            active_req_list, block_req_list, occ_slot_list = self._process_snapshots(snap_val_list=snap_val_list)
            active_req_matrix.append(active_req_list)
            block_req_matrix.append(block_req_list)
            occ_slot_matrix.append(occ_slot_list)

        self.plot_props['plot_dict'][time][sim_num]['req_num_list'] = req_num_list
        self.plot_props['plot_dict'][time][sim_num]['active_req_matrix'].append(np.mean(active_req_matrix, axis=0))
        self.plot_props['plot_dict'][time][sim_num]['block_req_matrix'].append(np.mean(block_req_matrix, axis=0))
        self.plot_props['plot_dict'][time][sim_num]['occ_slot_matrix'].append(np.mean(occ_slot_matrix, axis=0))

    def _find_mod_info(self, time: str, sim_num: str, erlang_dict: dict):
        mods_used_dict = erlang_dict['iter_stats']['0']['mods_used_dict']
        for bandwidth, mod_dict in mods_used_dict.items():
            for modulation in mod_dict:
                filters = ['mods_used_dict', bandwidth]
                mod_usages = dict_to_list(data_dict=erlang_dict['iter_stats'], nested_key=modulation, path=filters)

                modulations_dict = self.plot_props['plot_dict'][time][sim_num]['modulations_dict']
                modulations_dict.setdefault(bandwidth, {})
                modulations_dict[bandwidth].setdefault(modulation, []).append(mean(mod_usages))

    def _find_sim_info(self, time: str, sim_num: str, input_dict: dict):
        info_item_list = ['holding_time', 'cores_per_link', 'spectral_slots', 'network', 'num_requests',
                          'cores_per_link']
        for info_item in info_item_list:
            self.plot_props['plot_dict'][time][sim_num][info_item] = input_dict[info_item]

    def _update_plot_dict(self, time: str, sim_num: str):
        if self.plot_props['plot_dict'] is None:
            self.plot_props['plot_dict'] = {time: {}}
        elif self.plot_props[time] not in self.plot_props['plot_dict']:
            self.plot_props['plot_dict'][time] = {}

        self.plot_props['plot_dict'][time][sim_num] = empty_plot_dict

    @staticmethod
    def _read_json_file(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file_obj:
            return json.load(file_obj)

    def _read_input_output(self, time: str, sim_num: str, data_dict: dict, erlang: float):
        base_fp = os.path.join(data_dict['network'], data_dict['date'], time)
        file_name = f'{erlang}_erlang.json'
        output_fp = os.path.join(self.plot_props['output_dir'], base_fp, sim_num, file_name)
        erlang_dict = self._read_json_file(file_path=output_fp)

        file_name = f'sim_input_{sim_num}.json'
        input_fp = os.path.join(self.plot_props['input_dir'], base_fp, file_name)
        input_dict = self._read_json_file(file_path=input_fp)

        return input_dict, erlang_dict

    def _get_data(self):
        for time, data_dict in self.file_info.items():
            for sim_num, erlang_list in data_dict['sim_dict'].items():
                self._update_plot_dict(time=time, sim_num=sim_num)
                for erlang in erlang_list:
                    input_dict, erlang_dict = self._read_input_output(time=time, sim_num=sim_num, data_dict=data_dict,
                                                                      erlang=erlang)
                    erlang = int(erlang.split('.')[0])
                    self.plot_props['plot_dict'][time][sim_num]['erlang_list'].append(erlang)

                    self.plot_props['erlang_dict'] = erlang_dict
                    blocking_mean = self.plot_props['erlang_dict']['blocking_mean']
                    self.plot_props['plot_dict'][time][sim_num]['blocking_list'].append(blocking_mean)

                    self._find_sim_info(time=time, sim_num=sim_num, input_dict=input_dict)
                    self._find_mod_info(time=time, sim_num=sim_num, erlang_dict=erlang_dict)
                    self._find_snapshot_usage(time=time, sim_num=sim_num, erlang_dict=erlang_dict)
                    self._find_misc_stats()

    def get_file_info(self, sims_info_dict: dict):
        self.file_info = dict()
        matrix_count = 0
        networks_matrix = sims_info_dict['networks_matrix']
        dates_matrix = sims_info_dict['dates_matrix']
        times_matrix = sims_info_dict['times_matrix']

        for network_list, dates_list, times_list in zip(networks_matrix, dates_matrix, times_matrix):
            for network, date, time, in zip(network_list, dates_list, times_list):
                self.file_info[time] = {'network': network, 'date': date, 'sim_dict': dict()}
                curr_dir = os.path.join(self.plot_props['output_dir'], network, date, time)
                # Sort by sim number
                sim_dirs_list = os.listdir(curr_dir)
                sim_dirs_list = sorted(sim_dirs_list, key=lambda x: int(x[1:]))

                for sim in sim_dirs_list:
                    # User selected to not run this simulation
                    if sim not in sims_info_dict['sims_matrix'][matrix_count]:
                        continue

                    curr_fp = os.path.join(curr_dir, sim)
                    self.file_info[time]['sim_dict'][sim] = list()
                    files_list = os.listdir(curr_fp)
                    sorted_files_list = sorted(files_list, key=lambda x: float(x.split('_')[0]))

                    for erlang_file in sorted_files_list:
                        self.file_info[time]['sim_dict'][sim].append(erlang_file.split('_')[0])

            matrix_count += 1

        self._get_data()


def _not_filters(filter_dict: dict, file_dict: dict):
    keep_config = True
    for flags_list in filter_dict['not_filter_list']:
        params_dict = file_dict.get('sim_params')
        keys_list = flags_list[0:-1]
        check_value = flags_list[-1]

        for curr_key in keys_list:
            params_dict = params_dict.get(curr_key)

        if params_dict == check_value:
            keep_config = False
            break

        keep_config = True

    return keep_config


def _or_filters(filter_dict: dict, file_dict: dict):
    keep_config = True
    for flags_list in filter_dict['or_filter_list']:
        params_dict = file_dict.get('sim_params')
        keys_list = flags_list[0:-1]
        check_value = flags_list[-1]

        for curr_key in keys_list:
            params_dict = params_dict.get(curr_key)

        if params_dict == check_value:
            keep_config = True
            break

        keep_config = False

    return keep_config


def _and_filters(filter_dict: dict, file_dict: dict):
    keep_config = True
    params_dict = file_dict.get('sim_params')
    for flags_list in filter_dict['and_filter_list']:
        keys_list = flags_list[0:-1]
        check_value = flags_list[-1]

        for curr_key in keys_list:
            params_dict = params_dict.get(curr_key)

        if params_dict != check_value:
            keep_config = False
            break

    return keep_config


def _check_filters(file_dict: dict, filter_dict: dict):
    keep_config = _and_filters(filter_dict=filter_dict, file_dict=file_dict)

    if keep_config:
        keep_config = _or_filters(filter_dict=filter_dict, file_dict=file_dict)

        if keep_config:
            keep_config = _not_filters(filter_dict=filter_dict, file_dict=file_dict)

    return keep_config


def find_times(dates_dict: dict, filter_dict: dict):
    resp = {
        'times_matrix': list(),
        'sims_matrix': list(),
        'networks_matrix': list(),
        'dates_matrix': list(),
    }
    info_dict = dict()
    for date, network in dates_dict.items():
        times_path = os.path.join('..', 'data', 'output', network, date)
        times_list = [curr_dir for curr_dir in os.listdir(times_path)
                      if os.path.isdir(os.path.join(times_path, curr_dir))]

        for curr_time in times_list:
            sims_path = os.path.join(times_path, curr_time)
            sim_num_list = [curr_dir for curr_dir in os.listdir(sims_path) if
                            os.path.isdir(os.path.join(sims_path, curr_dir))]

            # TODO: Put this to a sub-function
            for sim in sim_num_list:
                file_path = os.path.join(sims_path, sim)
                files = [file for file in os.listdir(file_path)
                         if os.path.isfile(os.path.join(file_path, file))]
                # All Erlangs will have the same configuration, just take the first file's config
                file_name = os.path.join(file_path, files[0])
                with open(file_name, 'r', encoding='utf-8') as file_obj:
                    file_dict = json.load(file_obj)

                keep_config = _check_filters(file_dict=file_dict, filter_dict=filter_dict)
                if keep_config:
                    if curr_time not in dates_dict:
                        info_dict[curr_time] = {'sim_list': list(), 'network_list': list(), 'dates_list': list()}
                    info_dict[curr_time]['sim_list'].append(sim)
                    info_dict[curr_time]['network_list'].append(network)
                    info_dict[curr_time]['dates_list'].append(date)

    # Convert info dict to lists
    for time, obj in info_dict.items():
        resp['times_matrix'].append([time])
        resp['sims_matrix'].append(obj['sim_list'])
        resp['networks_matrix'].append(obj['network_list'])
        resp['dates_matrix'].append(obj['dates_list'])

    return resp