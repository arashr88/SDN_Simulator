from gymnasium import spaces


class AIHelpers:
    """
    Contains methods to assist with AI simulations.
    """

    def __init__(self, ai_props: dict, engine_obj: object):
        self.ai_props = ai_props
        self.engine_obj = engine_obj

        self.topology = None
        self.net_spec_dict = None
        self.reqs_status_dict = None

        self.path_index = None
        self.core_num = None
        self.slice_request = None
        # TODO: Probably need to use this
        self.mod_format = None
        # TODO: Probably need to use this
        self.bandwidth = None

    def get_obs_space(self, algorithm: str):
        # TODO: May need to change this to A2C, PPO, etc...
        if algorithm in ('dqn', 'ppo'):
            resp_obs = spaces.Dict({
                'source': spaces.Discrete(self.ai_props['num_nodes'], start=0),
                'destination': spaces.Discrete(self.ai_props['num_nodes'], start=0),
                'bandwidth': spaces.MultiBinary(len(self.ai_props['bandwidth_list'])),
                'cores_matrix': spaces.Box(low=0.01, high=1.01, shape=(self.ai_props['k_paths'],
                                                                       self.ai_props['cores_per_link'], 2)),
            })
        elif algorithm == 'q_learning':
            resp_obs = None
        else:
            raise NotImplementedError

        return resp_obs

    def get_action_space(self, algorithm: str):
        # TODO: May need to change this to A2C, PPO, etc...
        if algorithm in ('dqn', 'ppo'):
            action_space = spaces.MultiDiscrete([self.ai_props['k_paths'], self.ai_props['cores_per_link'],
                                                 self.ai_props['slice_space']])
        elif algorithm == 'q_learning':
            action_space = None
        else:
            raise NotImplementedError

        return action_space

    def handle_releases(self):
        """
        Checks if a request or multiple requests need to be released.
        """
        curr_time = self.ai_props['arrival_list'][self.ai_props['arrival_count']]['arrive']
        index_list = list()

        for i, req_obj in enumerate(self.ai_props['depart_list']):
            if req_obj['depart'] <= curr_time:
                index_list.append(i)
                self.engine_obj.handle_release(curr_time=req_obj['depart'])

        for index in index_list:
            self.ai_props['depart_list'].pop(index)

    def allocate(self, route_obj: object):
        """
        Attempts to allocate a given request.

        :param route_obj: The Routing class.
        """
        path_matrix = [route_obj.route_props['paths_list'][self.path_index]]
        curr_time = self.ai_props['arrival_list'][self.ai_props['arrival_count']]['arrive']
        self.engine_obj.handle_arrival(curr_time=curr_time, force_route_matrix=path_matrix,
                                       force_slicing=self.slice_request)

    def update_mock_sdn(self, curr_req: dict):
        """
        Updates the mock sdn dictionary to find select routes.
        :param curr_req: The current request.
        """
        mock_sdn = {
            'req_id': curr_req['req_id'],
            'source': curr_req['source'],
            'destination': curr_req['destination'],
            'bandwidth': curr_req['bandwidth'],
            'net_spec_dict': self.net_spec_dict,
            'topology': self.topology,
            'mod_formats': curr_req['mod_formats'],
            'num_trans': 1.0,
            'route_time': 0.0,
            'block_reason': None,
            'stat_key_list': ['modulation_list', 'xt_list', 'core_list'],
            'modulation_list': list(),
            'xt_list': list(),
            'is_sliced': False,
            'core_list': list(),
            'bandwidth_list': list(),
            'path_weight': list(),
            'spectrum_dict': {'modulation': None}
        }

        return mock_sdn
