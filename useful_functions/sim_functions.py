# Standard library imports
import copy
from typing import List

# Third-party library imports
import networkx as nx
import numpy as np

# Local application imports
import sim_scripts.spectrum_assignment
from sim_scripts.routing import Routing


def get_path_mod(mod_formats: dict, path_len: int):
    """
    Given an object of modulation formats and maximum lengths, choose the one that satisfies the requirements.

    :param mod_formats: The modulation object, holds needed information for maximum reach
    :type mod_formats: dict

    :param path_len: The length of the path to be taken
    :type path_len: int

    :return: The chosen modulation format, or false
    """
    if mod_formats['QPSK']['max_length'] >= path_len > mod_formats['16-QAM']['max_length']:
        resp = 'QPSK'
    elif mod_formats['16-QAM']['max_length'] >= path_len > mod_formats['64-QAM']['max_length']:
        resp = '16-QAM'
    elif mod_formats['64-QAM']['max_length'] >= path_len:
        resp = '64-QAM'
    else:
        return False

    return resp


def sort_dict_keys(dictionary: dict):
    """
    Given a dictionary with key-value pairs, return a new dictionary with the same pairs, sorted by keys in descending
    order.

    :param dictionary: The dictionary to sort.
    :type dictionary: dict

    :return: A new dictionary with the same pairs as the input dictionary, but sorted by keys in descending order.
    :rtype: dict
    """
    sorted_keys = sorted(map(int, dictionary.keys()), reverse=True)
    sorted_dict = {str(key): dictionary[str(key)] for key in sorted_keys}

    return sorted_dict


def find_path_len(path: List[str], topology: nx.Graph):
    """
    Finds the length of a path in a physical topology.

    :param path: A list of integers representing the nodes in the path.
    :type path: list of str

    :param topology: A networkx graph object representing the physical topology of the simulation.
    :type topology: networkx.Graph

    :return: The length of the path.
    """
    path_len = 0
    for i in range(len(path) - 1):
        path_len += topology[path[i]][path[i + 1]]['length']

    return path_len


def get_channel_overlaps(free_channels: dict, free_slots: dict):
    """
    Given the free channels and free slots on a given path, find the number of overlapping and non-overlapping channels
    between adjacent cores.

    :param free_channels: The free channels found on the given path.
    :type free_channels: dict

    :param free_slots: All free slots on the path.
    :type free_slots: dict

    :return: The overlapping and non-overlapping channels for every core.
    :rtype: dict
    """
    resp = {'overlap_channels': {}, 'other_channels': {}}
    num_cores = int(len(free_channels.keys()))

    for core_num, channels in free_channels.items():
        resp['overlap_channels'][core_num] = list()
        resp['other_channels'][core_num] = list()

        for curr_channel in channels:
            overlap = False
            for sub_core in range(0, num_cores):
                if sub_core == core_num:
                    continue

                for _, slots_dict in free_slots.items():
                    # The final core overlaps with all other cores
                    if core_num == num_cores - 1:
                        result = np.isin(curr_channel, slots_dict[sub_core])
                    else:
                        # Only certain cores neighbor each other on a fiber
                        first_neighbor = 5 if core_num == 0 else core_num - 1
                        second_neighbor = 0 if core_num == 5 else core_num + 1

                        result = np.isin(curr_channel, slots_dict[first_neighbor])
                        result = np.append(result, np.isin(curr_channel, slots_dict[second_neighbor]))
                        result = np.append(result, np.isin(curr_channel, slots_dict[num_cores - 1]))

                    if np.any(result):
                        resp['overlap_channels'][core_num].append(curr_channel)
                        overlap = True
                        break

                    # TODO: We may not want to break if we'd like to use this
                    resp['other_channels'][core_num].append(curr_channel)

                # No need to check other cores, we already determined this channel overlaps with other channels
                if overlap:
                    break

    return resp


def find_free_slots(net_spec_db: dict, des_link: tuple):
    """
    Find every unallocated spectral slot for a given link.

    :param net_spec_db: The most updated network spectrum database.
    :type net_spec_db: dict

    :param des_link: The link to find the free slots on.
    :type des_link: tuple

    :return: The indexes of the free spectral slots on the link for each core.
    :rtype: dict
    """
    link = net_spec_db[des_link]['cores_matrix']
    resp = {}
    for core_num, _ in enumerate(link):
        indexes = np.where(link[core_num] == 0)[0]
        resp.update({core_num: indexes})

    return resp


def find_free_channels(net_spec_db: dict, slots_needed: int, des_link: tuple):
    """
    Finds the free super-channels on a given link.

    :param net_spec_db: The most updated network spectrum database.
    :type net_spec_db: dict

    :param slots_needed: The number of slots needed for the request.
    :type slots_needed: int

    :param des_link: The link to search on.
    :type des_link: tuple

    :return: A matrix containing the indexes for available super-channels for that request for every core.
    :rtype: dict
    """
    resp = {}
    cores_matrix = copy.deepcopy(net_spec_db[des_link]['cores_matrix'])
    for core_num, link in enumerate(cores_matrix):
        indexes = np.where(link == 0)[0]
        channels = []
        curr_channel = []

        for i, free_index in enumerate(indexes):
            if i == 0:
                curr_channel.append(free_index)
            elif free_index == indexes[i - 1] + 1:
                curr_channel.append(free_index)
                if len(curr_channel) == slots_needed:
                    channels.append(curr_channel.copy())
                    curr_channel.pop(0)
            else:
                curr_channel = [free_index]

        resp.update({core_num: channels})

    return resp


def find_taken_channels(net_spec_db: dict, des_link: tuple):
    """
    Finds the taken super-channels on a given link.

    :param net_spec_db: The most updated network spectrum database.
    :type net_spec_db: dict

    :param des_link: The link to search on.
    :type des_link: tuple

    :return: A matrix containing the indexes for unavailable super-channels for that request for every core.
    :rtype: dict
    """
    resp = {}
    cores_matrix = copy.deepcopy(net_spec_db[des_link]['cores_matrix'])
    for core_num, link in enumerate(cores_matrix):
        channels = []
        curr_channel = []

        for value in link:
            if value > 0:
                curr_channel.append(value)
            elif value < 0 and curr_channel:
                channels.append(curr_channel)
                curr_channel = []

        if curr_channel:
            channels.append(curr_channel)

        resp[core_num] = channels

    return resp


def get_route(source: str, destination: str, topology: nx.Graph, net_spec_db: dict, mod_per_bw: dict, chosen_bw: str,
              guard_slots: int, beta: float, route_method: str, ai_obj: object):
    """
    Given request information, attempt to find a route for the request for various routing methods.

    :param source: The source node.
    :type source: str

    :param destination: The destination node.
    :type destination: str

    :param topology: The network topology information.
    :type topology: nx.Graph

    :param net_spec_db: The network spectrum database.
    :type net_spec_db: dict

    :param mod_per_bw: The modulation formats for each bandwidth.
    :type mod_per_bw: dict

    :param chosen_bw: The chosen bandwidth.
    :type chosen_bw: str

    :param guard_slots: The number of slots to be allocated for the guard band.
    :type guard_slots: int

    :param beta: A metric used for calculations in different routing method types.
    :type beta: float

    :param route_method: The desired routing method.
    :type route_method: str

    :param ai_obj: The object for artificial intelligence, if it's being used.
    :type ai_obj: object


    :return: The selected path and path modulation.
    :rtype: tuple
    """
    routing_obj = Routing(source=source, destination=destination,
                          topology=topology, net_spec_db=net_spec_db,
                          mod_formats=mod_per_bw[chosen_bw], bandwidth=chosen_bw,
                          guard_slots=guard_slots)

    # TODO: Change constant QPSK modulation formats
    if route_method == 'nli_aware':
        slots_needed = mod_per_bw[chosen_bw]['QPSK']['slots_needed']
        routing_obj.slots_needed = slots_needed
        routing_obj.beta = beta
        selected_path, path_mod = routing_obj.nli_aware()
    elif route_method == 'xt_aware':
        # TODO: Add xt_type to the configuration file
        selected_path, path_mod = routing_obj.xt_aware(beta=beta, xt_type='with_length')
    elif route_method == 'least_congested':
        selected_path = routing_obj.least_congested_path()
        # TODO: Constant QPSK for now
        path_mod = 'QPSK'
    elif route_method == 'shortest_path':
        selected_path, path_mod = routing_obj.shortest_path()
    elif route_method == 'ai':
        # Used for routing related to artificial intelligence
        selected_path = ai_obj.route(source=int(source), destination=int(destination),
                                     net_spec_db=net_spec_db, chosen_bw=chosen_bw,
                                     guard_slots=guard_slots)

        # A path could not be found, assign None to path modulation
        if not selected_path:
            path_mod = None
        else:
            path_len = find_path_len(path=selected_path, topology=topology)
            path_mod = get_path_mod(mod_formats=mod_per_bw[chosen_bw], path_len=path_len)
    else:
        raise NotImplementedError(f'Routing method not recognized, got: {route_method}.')

    return selected_path, path_mod


def get_spectrum(mod_per_bw: dict, chosen_bw: str, path: list, net_spec_db: dict, guard_slots: int, alloc_method: str,
                 modulation: str, check_snr: bool, snr_obj: object, path_mod: str, spectral_slots: int):
    """
    Given relevant request information, find a given spectrum for various allocation methods.

    :param mod_per_bw: The modulation formats for each bandwidth.
    :type mod_per_bw: dict

    :param chosen_bw: The chosen bandwidth for this request.
    :type chosen_bw: str

    :param path: The chosen path for this request.
    :type path: list

    :param net_spec_db: The network spectrum database.
    :type net_spec_db: dict

    :param guard_slots: The number of slots to be allocated to the guard band.
    :type guard_slots: int

    :param alloc_method: The desired allocation method.
    :type alloc_method: str

    :param modulation: The modulation format chosen for this request.
    :type modulation: str

    :param check_snr: A flag to check signal-to-noise ratio calculations or not.
    :type check_snr: bool

    :param snr_obj: If check_snr is true, the object containing all snr related methods.
    :type snr_obj: object

    :param path_mod: The modulation format for the given path.
    :type path_mod: str

    :param spectral_slots: The number of spectral slots needed for the request.
    :type spectral_slots: int

    :return: The information related to the spectrum found for allocation, false otherwise.
    :rtype: dict
    """
    slots_needed = mod_per_bw[chosen_bw][modulation]['slots_needed']
    spectrum_assignment = sim_scripts.spectrum_assignment.SpectrumAssignment(path=path, slots_needed=slots_needed,
                                                                             net_spec_db=net_spec_db,
                                                                             guard_slots=guard_slots,
                                                                             is_sliced=False, alloc_method=alloc_method)

    spectrum = spectrum_assignment.find_free_spectrum()

    if spectrum is not False:
        if check_snr:
            _update_snr_obj(snr_obj=snr_obj, spectrum=spectrum, path=path, path_mod=path_mod,
                            spectral_slots=spectral_slots, net_spec_db=net_spec_db)
            snr_check = handle_snr(check_snr=check_snr, snr_obj=snr_obj)

            if not snr_check:
                return False

        return spectrum

    return False


def _update_snr_obj(snr_obj: object, spectrum: dict, path: list, path_mod: str, spectral_slots: int, net_spec_db: dict):
    """
    Updates variables in the signal-to-noise ratio calculation object.

    :param snr_obj: The object whose variables are updated.
    :type snr_obj: object

    :param spectrum: The spectrum chosen for the request.
    :type spectrum: dict

    :param path: The chosen path for the request.
    :type path: list

    :param path_mod: The modulation format chosen for the request.
    :type path_mod: str

    :param spectral_slots: The total number of spectral slots for each core in the network.
    :type spectral_slots: int

    :param net_spec_db: The network spectrum database.
    :type net_spec_db: dict
    """
    snr_obj.path = path
    snr_obj.path_mod = path_mod
    snr_obj.spectrum = spectrum
    snr_obj.assigned_slots = spectrum['end_slot'] - spectrum['start_slot'] + 1
    snr_obj.spectral_slots = spectral_slots
    snr_obj.net_spec_db = net_spec_db


def handle_snr(check_snr: str, snr_obj: object):
    """
    Determines which type of signal-to-noise ratio calculation is used and calculates it.

    :param check_snr: The type of SNR calculation for every request.
    :type check_snr: str

    :param snr_obj: Object containing all methods for SNR calculation.
    :type snr_obj: object

    :return: If the SNR threshold can be met or not.
    :rtype: bool
    """
    if check_snr == "snr_calculation_nli":
        snr_check = snr_obj.check_snr()
    elif check_snr == "xt_calculation":
        snr_check = snr_obj.check_xt()
    elif check_snr == "snr_calculation_xt":
        snr_check = snr_obj.check_snr_xt()
    else:
        raise NotImplementedError(f'Unexpected check_snr flag got: {check_snr}')

    return snr_check
