from arg_scripts.grooming_args import GroomingProps


class Grooming:
    """
    This class contains methods related to traffic grooming.
    """
    def __init__(self, engine_props: dict, sdn_props: object):
        self.grooming_props = GroomingProps()
        self.engine_props = engine_props
        self.sdn_props = sdn_props

    def _end_to_end_grooming(self):
        """
        Function to groom the arrival requests to already established lightpaths.

        :return: If the requested is groomed to established lightpath.
        :rtype: bool
        """
                
        light_id = tuple(sorted([self.sdn_props.source, self.sdn_props.destination]))

        if light_id in self.sdn_props.lightpath_status_dict:
            if sum(item['remaining_bandwidth'] for item in self.sdn_props.lightpath_status_dict[light_id].values()) >= int(self.sdn_props.bandwidth):
                remaining_bw = int(self.sdn_props.bandwidth)
                for lp_id in self.sdn_props.lightpath_status_dict[light_id].keys():
                    if self.sdn_props.lightpath_status_dict[light_id][lp_id]["remaining_bandwidth"] == 0:
                        continue
                    if self.sdn_props.lightpath_status_dict[light_id][lp_id]["remaining_bandwidth"] > remaining_bw :
                        tmp_remaining_bw = remaining_bw
                        remaining_bw = 0
                    else:
                        tmp_remaining_bw = self.sdn_props.lightpath_status_dict[light_id][lp_id]["remaining_bandwidth"]
                        remaining_bw -= self.sdn_props.lightpath_status_dict[light_id][lp_id]["remaining_bandwidth"]
                        self.sdn_props.is_sliced = True
                    self.sdn_props.lightpath_status_dict[light_id][lp_id]["requests_dict"].update({self.sdn_props.req_id:tmp_remaining_bw})
                    self.sdn_props.lightpath_status_dict[light_id][lp_id]["remaining_bandwidth"] -= tmp_remaining_bw
                    self.sdn_props.bandwidth_list.append(str(tmp_remaining_bw))
                    self.sdn_props.core_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["core"])
                    self.sdn_props.band_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["band"])
                    self.sdn_props.start_slot_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["start_slot"])
                    self.sdn_props.end_slot_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["end_slot"])
                    self.sdn_props.modulation_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["mod_format"])
                    self.sdn_props.path_list = self.sdn_props.lightpath_status_dict[light_id][lp_id]["path"]
                    self.sdn_props.xt_list.append(self.sdn_props.lightpath_status_dict[light_id][lp_id]["snr_cost"])
                    # self.sdn_props.was_routed =True
                    self.sdn_props.lightpath_id_list.append(lp_id)
                    if remaining_bw == 0:
                        self.sdn_props.was_routed = True
                        self.sdn_props.was_groomed = True
                        self.sdn_props.num_trans = 0
                        self.sdn_props.was_new_lp_established = False
                        return True         
        return False
    def _release_service(self):
        """
        Removes a previously allocated request from the lightpaths.
        
		:return: list of the lightpaths which are not carried any request.
        :rtype: list
        """

        release_lp = []
        light_id = tuple(sorted([self.sdn_props.source, self.sdn_props.destination]))

        for lp_id in self.sdn_props.lightpath_id_list:
            req_bw = self.sdn_props.lightpath_status_dict[light_id][lp_id]['requests_dict'][self.sdn_props.req_id]
            self.sdn_props.lightpath_status_dict[light_id][lp_id]['requests_dict'].pop(self.sdn_props.req_id)
            self.sdn_props.lightpath_status_dict[light_id][lp_id]['remaining_bandwidth'] += req_bw
            if self.sdn_props.lightpath_status_dict[light_id][lp_id]['remaining_bandwidth'] == self.sdn_props.lightpath_status_dict[light_id][lp_id]['lightpath_bandwidth'] :
                release_lp.append(lp_id)
        return release_lp

    def handle_grooming(self, request_type):
        """
        Controls the methods of this class.
        """

        if request_type == "release":
            return self._release_service()
        else:
            return self._end_to_end_grooming()
