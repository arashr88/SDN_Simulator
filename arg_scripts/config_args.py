import ast


def str_to_bool(string: str):
    """
    Convert any giving string to a boolean.

    :param string: The input string.
    :return: True or False
    :rtype: bool
    """
    return string.lower() in ['true', 'yes', '1']


YUE_REQUIRED_OPTIONS = {
    'general_settings': {
        'sim_type': str,
        'holding_time': float,
        'arrival_rate': ast.literal_eval,
        'thread_erlangs': str_to_bool,
        'guard_slots': int,
        'num_requests': int,
        'request_distribution': ast.literal_eval,
        'max_iters': int,
        'max_segments': int,
        'dynamic_lps': str_to_bool,
        'allocation_method': str,
        'route_method': str,
        'save_snapshots': str_to_bool,
        'snapshot_step': int,
        'print_step': int,
    },
    'topology_settings': {
        'network': str,
        'bw_per_slot': float,
        'cores_per_link': int,
        'const_link_weight': str_to_bool,
    },
    'spectrum_settings': {
        'c_band': int,
    },
    'file_settings': {
        'file_type': str,
    },
}

ARASH_REQUIRED_OPTIONS = {
    'general_settings': {
        'sim_type': str,
        'holding_time': float,
        'erlangs': ast.literal_eval,
        'thread_erlangs': str_to_bool,
        'guard_slots': int,
        'num_requests': int,
        'request_distribution': ast.literal_eval,
        'max_iters': int,
        'max_segments': int,
        'dynamic_lps': str_to_bool,
        'route_method': str,
        'allocation_method': str,
        'save_snapshots': str_to_bool,
        'snapshot_step': int,
        'print_step': int,
    },
    'topology_settings': {
        'network': str,
        'bw_per_slot': float,
        'cores_per_link': int,
        'const_link_weight': str_to_bool,
    },
    'spectrum_settings': {
        'c_band': int,
    },
    'snr_settings': {
        'requested_xt': ast.literal_eval,
        'xt_noise': str_to_bool,
        'theta': float,
        'egn_model': str_to_bool,
        'phi': ast.literal_eval,
        'snr_type': str,
        'xt_type': str,
        'beta': float,
        'input_power': float,
    },
    'file_settings': {
        'file_type': str,
    },
}

OTHER_OPTIONS = {
    'general_settings': {
        'seeds': list,
        'k_paths': int,
        'filter_mods': bool,
        'snapshot_step': int,
        'print_step': int,
    },
    'topology_settings': {
        'bi_directional': str_to_bool,
    },
    'snr_settings': {
        'snr_type': str,
        'xt_type': str,
        'theta': float,
        'beta': float,
        'input_power': float,
        'egn_model': str_to_bool,
        'phi': ast.literal_eval,
        'xt_noise': str_to_bool,
        'requested_xt': ast.literal_eval,
    },
    'spectrum_settings': {
        'o_band': int,
        'e_band': int,
        's_band': int,
        'l_band': int,
    },
    'rl_settings': {
        'device': str,
        'optimize': str_to_bool,
        'optimize_hyperparameters': str_to_bool,
        'is_training': str_to_bool,
        'path_algorithm': str,
        'path_model': str,
        'core_algorithm': str,
        'core_model': str,
        'spectrum_algorithm': str,
        'spectrum_model': str,
        'super_channel_space': int,
        'alpha_update': str,
        'alpha_start': float,
        'alpha_end': float,
        'discount_factor': float,
        'epsilon_update': str,
        'epsilon_start': float,
        'epsilon_end': float,
        'reward': float,
        'penalty': float,
        'dynamic_reward': str_to_bool,
        'path_levels': int,
        'core_beta': float,
        'decay_rate': float,
    },
    'ml_settings': {
        'output_train_data': str_to_bool,
        'ml_training': str_to_bool,
        'deploy_model': str_to_bool,
        'train_file_path': str,
        'ml_model': str,
        'test_size': float,
    },
    'file_settings': {
    },
}

COMMAND_LINE_PARAMS = [
    ['epsilon_start', float, ''],
    ['epsilon_end', float, ''],
    ['learn_rate', float, ''],
    ['discount_factor', float, ''],
    ['is_training', bool, ''],
    ['seeds', list, ''],
    ['beta', float, ''],
    ['train_file', str, ''],
    ['snr_type', str, ''],
    ['input_power', float, ''],
    ['egn_model', bool, ''],
    ['phi', dict, ''],
    ['bi_directional', bool, ''],
    ['xt_noise', bool, ''],
    ['requested_xt', dict, ''],
    ['k_paths', int, ''],
    ['sim_type', str, ''],
    ['network', str, ''],
    ['holding_time', float, ''],
    ['erlangs', dict, ''],
    ['thread_erlangs', bool, ''],
    ['num_requests', int, ''],
    ['max_iters', int, ''],
    ['c_band', int, ''],
    ['e_band', int, ''],
    ['o_band', int, ''],
    ['l_band', int, ''],
    ['s_band', int, ''],
    ['bw_per_slot', float, ''],
    ['cores_per_link', int, ''],
    ['const_link_weight', bool, ''],
    ['guard_slots', int, ''],
    ['max_segments', int, ''],
    ['dynamic_lps', bool, ''],
    ['allocation_method', str, ''],
    ['route_method', str, ''],
    ['request_distribution', dict, ''],
    ['arrival_rate', dict, ''],
    ['save_snapshots', bool, ''],
    ['xt_type', str, ''],
    ['snapshot_step', int, ''],
    ['print_step', int, ''],
    ['file_type', str, ''],
    ['theta', float, ''],
    ['filter_mods', bool, ''],
    ['super_channel_space', int, ''],
    ['policy', str, ''],
    ['path_model', str, ''],
    ['core_model', str, ''],
    ['spectrum_model', str, ''],
    ['path_algorithm', str, ''],
    ['core_algorithm', str, ''],
    ['spectrum_algorithm', str, ''],
    ['optimize_hyperparameters', str, ''],
    ['reward', float, ''],
    ['penalty', float, ''],
    ['output_train_data', bool, ''],
    ['ml_training', bool, ''],
    ['train_file_path', str, ''],
    ['ml_model', str, ''],
    ['test_size', float, ''],
    ['deploy_model', bool, ''],
    ['path_levels', int, ''],
    ['core_beta', float, ''],
    ['gamma', float, ''],
    ['decay_factor', float, ''],
    ['dynamic_reward', bool, ''],
    ['config_path', str, ''],
    ['alpha_update', str, ''],
    ['alpha_start', float, ''],
    ['alpha_end', float, ''],
    ['epsilon_update', str, ''],
    ['decay_rate', float, ''],

    # StableBaselines3 arguments
    ['algo', str, ''],
    ['env-id', str, ''],
    ['env', str, ''],
    ['log-folder', str, ''],
    ['tensorboard-log', str, ''],
    ['n-timesteps', int, ''],
    ['eval-freq', int, ''],
    ['n-eval-episodes', int, ''],
    ['save-freq', int, ''],
    ['hyperparams', dict, ''],
    ['env-kwargs', str, ''],
    ['eval-env-kwargs', dict, ''],
    ['trained-agent', str, ''],
    ['optimize-hyperparameters', bool, ''],
    ['storage', str, ''],
    ['study-name', str, ''],
    ['n-trials', int, ''],
    ['max-total-trials', int, ''],
    ['n-jobs', int, ''],
    ['sampler', str, ''],
    ['pruner', str, ''],
    ['optimization-log-path', str, ''],
    ['n-startup-trials', int, ''],
    ['n-evaluations', int, ''],
    ['truncate-last-trajectory', bool, ''],
    ['uuid-str', str, ''],
    ['seed', int, ''],
    ['log-interval', int, ''],
    ['save-replay-buffer', bool, ''],
    ['verbose', int, ''],
    ['vec-env-type', int, ''],
    ['n-eval-envs', int, ''],
    ['no-optim-plots', bool, ''],
    ['device', str, ''],
    ['config', str, ''],
    ['show-progress', bool, ''],
    ['conf-file', str, ''],
    ['eval-episodes', int, ''],
]
