import os
import json
import numpy as np
import matplotlib.pyplot as plt  # pylint: disable=import-error

from useful_functions.handle_dirs_files import create_dir


# TODO: Neaten this script, it's terrible


class Blocking:
    """
    Creates and saves plot of blocking percentage vs. Erlang.
    """

    def __init__(self):
        # Change these variables for the desired plot you'd like
        # TODO: Document the structure of how things are saved
        # TODO: Default to latest one if none is chosen (mark this on the graph)
        # solo/400/0208_15:54:51_5
        # self.des_times = ['0217_11:07:30', '0217_11:07:32', '0217_11:07:34', '0217_11:07:36', '0217_11:07:38']
        self.des_times = ['0217_10:33:18', '0217_10:33:20', '0217_10:33:22', '0217_10:33:24', '0217_10:33:26']
        self.network_name = 'USNet'
        self.base_path = f'../data/output/{self.network_name}'
        self.files = self.get_file_names()

        self.erlang_arr = np.array([])
        self.blocking_arr = np.array([])
        self.plot_dict = dict()
        self.mu = None  # pylint: disable=invalid-name
        self.num_cores = None
        self.spectral_slots = None
        self.max_lps = None
        self.trans_arr = np.array([])
        self.dist_arr = np.array([])
        self.cong_arr = np.array([])

        self.band_one = np.array([])
        self.band_two = np.array([])
        self.band_three = np.array([])

        self.lps = True

    def get_file_names(self):
        """
        Obtains all the filenames of the output data for each Erlang.
        """
        res_dict = dict()
        for curr_time in self.des_times:
            curr_fp = f'{self.base_path}/{curr_time}/'
            tmp_list = sorted([float(f.split('_')[0]) for f in os.listdir(curr_fp)
                               if os.path.isfile(os.path.join(curr_fp, f))])
            res_dict[curr_time] = tmp_list

        return res_dict

    def plot_blocking_means(self):
        """
        Plots blocking means vs. Erlang values.
        """
        for curr_time, lst in self.files.items():
            self.plot_dict[curr_time] = dict()

            for erlang in lst:
                curr_fp = f'{self.base_path}/{curr_time}/'
                with open(f'{curr_fp}/{erlang}_erlang.json', 'r', encoding='utf-8') as curr_f:
                    curr_dict = json.load(curr_f)

                blocking_mean = curr_dict['stats']['mean']
                # Only one iteration occurred, no mean calculated for now
                if blocking_mean is None:
                    blocking_mean = curr_dict['simulations']['0']

                blocking_mean = float(blocking_mean)

                self.erlang_arr = np.append(self.erlang_arr, erlang)
                # TODO: Change
                # self.blocking_arr = np.append(self.blocking_arr, blocking_mean)
                # block_50 = 0.3 * curr_dict['stats']['misc_info']['blocking_obj']['50']
                # block_100 = 0.5 * curr_dict['stats']['misc_info']['blocking_obj']['100']
                # block_400 = 0.2 * curr_dict['stats']['misc_info']['blocking_obj']['400']

                block_50 = 50 * curr_dict['stats']['misc_info']['blocking_obj']['50']
                block_100 = 100 * curr_dict['stats']['misc_info']['blocking_obj']['100']
                block_400 = 400 * curr_dict['stats']['misc_info']['blocking_obj']['400']

                total_50 = 50 * (0.3 * curr_dict['stats']['num_req'])
                total_100 = 100 * (0.5 * curr_dict['stats']['num_req'])
                total_400 = 400 * (0.2 * curr_dict['stats']['num_req'])

                # blocking_mean = ((block_50 + block_100 + block_400) / (curr_dict['stats']['num_req']))
                blocking_mean = ((block_50 + block_100 + block_400) / (total_50 + total_100 + total_400))
                self.blocking_arr = np.append(self.blocking_arr, blocking_mean)
                self.num_cores = curr_dict['stats']['misc_info']['cores_used']

                if erlang == 50:
                    self.mu = curr_dict['stats']['misc_info']['mu']
                    self.num_cores = curr_dict['stats']['misc_info']['cores_used']
                    self.spectral_slots = curr_dict['stats']['misc_info']['spectral_slots']
                    if self.lps:
                        self.max_lps = curr_dict['stats']['misc_info']['max_lps']

            self.plot_dict[curr_time]['erlang'] = self.erlang_arr
            self.plot_dict[curr_time]['blocking'] = self.blocking_arr
            self.plot_dict[curr_time]['max_lps'] = self.max_lps

            self.erlang_arr = np.array([])
            self.blocking_arr = np.array([])

        self.save_plot()

    def plot_transponders(self):
        """
        Will change.
        :return:
        """
        for curr_time, lst in self.files.items():
            self.plot_dict[curr_time] = dict()

            for erlang in lst:
                curr_fp = f'{self.base_path}/{curr_time}/'
                with open(f'{curr_fp}/{erlang}_erlang.json', 'r', encoding='utf-8') as curr_f:
                    curr_dict = json.load(curr_f)

                self.erlang_arr = np.append(self.erlang_arr, erlang)
                self.trans_arr = np.append(self.trans_arr, curr_dict['stats']['misc_info']['av_transponders'])
                self.max_lps = curr_dict['stats']['misc_info']['max_lps']
                self.num_cores = curr_dict['stats']['misc_info']['cores_used']

            self.plot_dict[curr_time]['erlang'] = self.erlang_arr
            self.plot_dict[curr_time]['max_lps'] = self.max_lps
            self.plot_dict[curr_time]['av_trans'] = self.trans_arr

            self.erlang_arr = np.array([])
            self.trans_arr = np.array([])

        self.save_plot(plot_trans=True)

    def plot_block_percents(self):
        """
        Will change
        :return:
        """
        for curr_time, lst in self.files.items():
            self.plot_dict[curr_time] = dict()

            for erlang in lst:
                curr_fp = f'{self.base_path}/{curr_time}/'
                with open(f'{curr_fp}/{erlang}_erlang.json', 'r', encoding='utf-8') as curr_f:
                    curr_dict = json.load(curr_f)

                self.erlang_arr = np.append(self.erlang_arr, erlang)
                self.dist_arr = np.append(self.dist_arr, curr_dict['stats']['misc_info']['dist_block'])
                self.cong_arr = np.append(self.cong_arr, curr_dict['stats']['misc_info']['cong_block'])
                self.max_lps = curr_dict['stats']['misc_info']['max_lps']
                self.num_cores = curr_dict['stats']['misc_info']['cores_used']

            self.plot_dict[curr_time]['erlang'] = self.erlang_arr
            self.plot_dict[curr_time]['max_lps'] = self.max_lps
            self.plot_dict[curr_time]['cong_block'] = self.cong_arr
            self.plot_dict[curr_time]['dist_block'] = self.dist_arr

            self.dist_arr = np.array([])
            self.cong_arr = np.array([])
            self.erlang_arr = np.array([])

        self.save_plot(plot_percents=True)

    def plot_bandwidths(self):
        """
        Will change
        :return:
        """
        for curr_time, lst in self.files.items():
            self.plot_dict[curr_time] = dict()

            for erlang in lst:
                curr_fp = f'{self.base_path}/{curr_time}/'
                with open(f'{curr_fp}/{erlang}_erlang.json', 'r', encoding='utf-8') as curr_f:
                    curr_dict = json.load(curr_f)

                self.erlang_arr = np.append(self.erlang_arr, erlang)
                self.dist_arr = np.append(self.dist_arr, curr_dict['stats']['misc_info']['dist_block'])
                self.cong_arr = np.append(self.cong_arr, curr_dict['stats']['misc_info']['cong_block'])

                obj_one = curr_dict['stats']['misc_info']['bandwidth_block']['50']
                obj_two = curr_dict['stats']['misc_info']['bandwidth_block']['100']
                obj_three = curr_dict['stats']['misc_info']['bandwidth_block']['400']

                self.band_one = np.array([self.band_one, (float(obj_one['blocked']) / float(obj_one['total']) * 100.0)])
                self.band_two = np.array([self.band_one, (float(obj_two['blocked']) / float(obj_two['total']) * 100.0)])
                self.band_three = np.array(
                    [self.band_one, (float(obj_three['blocked']) / float(obj_three['total']) * 100.0)])

                self.max_lps = curr_dict['stats']['misc_info']['max_lps']
                self.num_cores = curr_dict['stats']['misc_info']['cores_used']

            self.plot_dict[curr_time]['erlang'] = self.erlang_arr
            self.plot_dict[curr_time]['max_lps'] = self.max_lps
            self.plot_dict[curr_time]['50'] = self.band_one
            self.plot_dict[curr_time]['100'] = self.band_two
            self.plot_dict[curr_time]['400'] = self.band_three

            self.band_one = np.array([])
            self.band_two = np.array([])
            self.band_three = np.array([])
            self.erlang_arr = np.array([])

        self.save_plot(plot_bands=True)

    def save_plot(self, plot_trans=False, plot_percents=False, plot_bands=False):
        """
        Saves and shows the plot.
        """
        if plot_trans:
            plt.title(f'{self.network_name} Transponders vs. Erlang (Core = {self.num_cores})')
            plt.ylabel('Transponders per Request')
        elif plot_percents or plot_bands:
            figure, axis = plt.subplots(2, 2)  # pylint: disable=unused-variable
            plt.subplots_adjust(left=0.1,
                                bottom=0.1,
                                right=0.9,
                                top=0.9,
                                wspace=0.4,
                                hspace=0.4)
            tmp_lst = [[0, 0], [0, 1], [1, 0], [1, 1]]
        else:
            # plt.title(f'{self.network_name} BP vs. Erlang (Core, BW = {self.num_cores}, 50 Gbps)')
            plt.title(f'{self.network_name} BP vs. Erlang')
            plt.ylabel('Blocking Probability')
            plt.yscale('log')

            plt.grid()
            plt.xlabel('Erlang')

        create_dir(f'./output/{self.network_name}')

        legend_list = list()
        cnt = 0
        for curr_time, obj in self.plot_dict.items():  # pylint: disable=unused-variable
            if plot_trans:
                plt.plot(obj['erlang'], obj['av_trans'])
                legend_list.append(f"LS = {obj['max_lps']}")
            elif plot_percents or plot_bands:
                axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].grid()
                axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].set_yticks([20, 40, 60, 80, 100])

                if plot_percents:
                    axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].plot(obj['erlang'], obj['cong_block'])
                    axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].plot(obj['erlang'], obj['dist_block'])
                else:
                    axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].plot(obj['erlang'], obj['50'])
                    axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].plot(obj['erlang'], obj['100'])
                    axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].plot(obj['erlang'], obj['400'])

                if cnt == 0:
                    if plot_percents:
                        axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].legend(['Congestion', 'Distance'])
                    else:
                        axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].legend(['50', '100', '200', '400'])

                    plt.ylabel('Percent')
                    plt.xlabel('Erlang')

                axis[tmp_lst[cnt][0], tmp_lst[cnt][1]].set_title(
                    # f"{self.network_name} (Core, LS = {self.num_cores}, {obj['max_lps']})")
                    f"{self.network_name} (BW, LS = 50, {obj['max_lps']})")
            else:
                plt.plot(obj['erlang'], obj['blocking'])
                legend_list.append(f"LS = {obj['max_lps']}")

            cnt += 1

        if not plot_trans and not plot_percents:
            plt.yticks([10 ** -4, 10 ** -3, 10 ** -2, 10 ** -1, 1])
            plt.xticks(list(range(10, 810, 100)))
            plt.legend(legend_list)

        # Always saves based on the last time in the list
        # plt.savefig(f'./output/{self.network_name}/{self.des_times[-1]}.png')
        plt.show()


if __name__ == '__main__':
    blocking_obj = Blocking()
    blocking_obj.plot_blocking_means()
    # blocking_obj.plot_transponders()
    # blocking_obj.plot_block_percents()
    # blocking_obj.plot_bandwidths()
