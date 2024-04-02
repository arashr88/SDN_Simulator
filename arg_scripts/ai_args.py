# TODO: If any variable is used in both algorithms you could argue they should be in the
#   run_ai_sim constructor
import numpy as np

empty_q_props = {
    'epsilon': None,
    'epsilon_start': None,
    'epsilon_end': None,
    'epsilon_list': list(),
    'is_training': None,

    'rewards_dict': {
        'routes_dict': {'average': [], 'min': [], 'max': [], 'rewards': {}},
        'cores_dict': {'average': [], 'min': [], 'max': [], 'rewards': {}}
    },
    'errors_dict': {
        'routes_dict': {'average': [], 'min': [], 'max': [], 'errors': {}},
        'cores_dict': {'average': [], 'min': [], 'max': [], 'errors': {}}
    },
    'sum_rewards_dict': dict(),
    'sum_errors_dict': dict(),

    'routes_matrix': None,
    'cores_matrix': None,
    'num_nodes': None,

    'save_params_dict': {
        'q_params_list': ['rewards_dict', 'errors_dict', 'epsilon_list', 'sum_rewards_dict', 'sum_errors_dict'],
        'engine_params_list': ['epsilon_start', 'epsilon_end', 'max_iters', 'learn_rate', 'discount_factor']
    }
}

empty_drl_props = {
    'k_paths': None,
    'cores_per_link': None,
    'spectral_slots': None,
    'num_nodes': -1,
    'min_arrival': np.inf,
    'max_arrival': -1 * np.inf,
    'min_depart': np.inf,
    'max_depart': -1 * np.inf,
    'bandwidth_list': list(),
    'max_slots_needed': 0,
    'max_length': 0,
    'slice_space': 2,
    'mock_sdn_dict': dict(),
    'arrival_list': list(),
    'depart_list': list(),
}
