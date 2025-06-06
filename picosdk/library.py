#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
"""
Definition of the Library class, which is the abstract representation of a picotech device driver.
Note: Many of the functions in this class are missing: these are populated by the psN000(a).py modules, which subclass
this type and attach the missing methods.
"""

from __future__ import print_function

import sys
from ctypes import c_int16, c_int32, c_uint32, c_float, c_double, c_void_p, create_string_buffer, byref
from ctypes.util import find_library
import collections
import picosdk.constants as constants
import numpy

from picosdk.errors import PicoError, CannotFindPicoSDKError, CannotOpenPicoSDKError, DeviceNotFoundError, \
    ArgumentOutOfRangeError, ValidRangeEnumValueNotValidForThisDevice, DeviceCannotSegmentMemoryError, \
    InvalidMemorySegmentsError, InvalidTimebaseError, InvalidTriggerParameters, InvalidCaptureParameters


from picosdk.device import Device


"""TimebaseInfo: A type for holding the particulars of a timebase configuration.
"""
TimebaseInfo = collections.namedtuple('TimebaseInfo', ['timebase_id',
                                                       'time_interval',
                                                       'time_units',
                                                       'max_samples',
                                                       'segment_id'])


def requires_device(error_message="This method requires a Device instance registered to this Library instance."):
    def check_device_decorator(method):
        def check_device_impl(self, device, *args, **kwargs):
            if not isinstance(device, Device) or device.driver != self:
                raise TypeError(error_message)
            return method(self, device, *args, **kwargs)
        return check_device_impl
    return check_device_decorator


def voltage_to_logic_level(voltage):
    """Convert a voltage value into logic level for digital channels.

    Range: –32767 (–5 V) to 32767 (5 V).

    Args:
        voltage (float): Voltage in volts.

    Returns:
        int: The calculated logic level count.
    """
    clamped_voltage = min(max(-5, voltage), 5)
    logic_level = int((clamped_voltage) * (32767 / 5))
    return logic_level


class Library(object):
    def __init__(self, name):
        self.name = name
        self._clib = self._load()
        # ! some drivers will replace these dicts at import time, where they have different constants (notably ps2000).
        self.PICO_INFO = constants.PICO_INFO
        self.PICO_STATUS = constants.PICO_STATUS
        self.PICO_STATUS_LOOKUP = constants.PICO_STATUS_LOOKUP
        # these must be set in each driver file.
        self.PICO_CHANNEL = {}
        self.PICO_COUPLING = {}
        self.PICO_VOLTAGE_RANGE = {}

        # most series of scopes top out at 512MS.
        self.MAX_MEMORY = 2**29

        # These are set in some driver files, but not all.
        self.PICO_RATIO_MODE = {}
        self.PICO_THRESHOLD_DIRECTION = {}

    def _load(self):
        library_path = find_library(self.name)

        # 'find_library' fails in Cygwin.
        if not sys.platform == 'cygwin':
            if library_path is None:
                env_var_name = "PATH" if sys.platform == 'win32' else "LD_LIBRARY_PATH"
                raise CannotFindPicoSDKError("PicoSDK (%s) not found, check %s" % (self.name, env_var_name))

        try:
            if sys.platform == 'win32':
                from ctypes import WinDLL
                result = WinDLL(library_path)
            elif sys.platform == 'cygwin':
                from ctypes import CDLL
                library_path = self.name
                result = CDLL(library_path + ".dll")
            else:
                from ctypes import cdll
                result = cdll.LoadLibrary(library_path)
        except OSError as e:
            raise CannotOpenPicoSDKError("PicoSDK (%s) not compatible (check 32 vs 64-bit): %s" % (self.name, e))
        return result

    def __str__(self):
        return "picosdk %s library" % self.name

    def make_symbol(self, python_name, c_name, return_type, argument_types, docstring=None):
        """Used by python wrappers for particular drivers to register C functions on the class."""
        c_function = getattr(self._clib, c_name)
        c_function.restype = return_type
        c_function.argtypes = argument_types
        if docstring is not None:
            c_function.__doc__ = docstring
        # make the functions available under *both* their original and generic names
        setattr(self, python_name, c_function)
        setattr(self, c_name, c_function)
        # AND if the function is camel case, add an "underscore-ized" version:
        if python_name.lower() != python_name:
            acc = []
            python_name = python_name.lstrip('_')
            for c in python_name:
                # Be careful to exclude both digits (lower index) and lower case (higher index).
                if ord('A') <= ord(c) <= ord('Z'):
                    c = "_" + c.lower()
                acc.append(c)
            new_python_name = "".join(acc)
            if not new_python_name.startswith('_'):
                new_python_name = "_" + new_python_name
            setattr(self, "".join(acc), c_function)

    def list_units(self):
        """Returns: a list of dictionaries which identify connected devices which use this driver."""
        handles = []
        device_infos = []
        try:
            while True:
                handle = self._python_open_unit()
                device_infos.append(self._python_get_unit_info_wrapper(handle, []))
                handles.append(handle)
        except DeviceNotFoundError:
            pass

        for handle in handles:
            self._python_close_unit(handle)

        return device_infos

    def open_unit(self, serial=None, resolution=None):
        """optional arguments:
        serial: If no serial number is provided, this function opens the first device discovered.
        resolution: for some devices, you may specify a resolution as you open the device. You should retrieve this
            numeric constant from the relevant driver module.
        returns: a Device instance, which has functions on it for collecting data and using the waveform generator (if
            present).
        Note: Either use this object in a context manager, or manually call .close() on it when you are finished."""
        return Device(self, self._python_open_unit(serial=serial, resolution=resolution))

    @requires_device("close_unit requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def close_unit(self, device):
        self._python_close_unit(device.handle)

    @requires_device("get_unit_info requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def get_unit_info(self, device, *args):
        return self._python_get_unit_info_wrapper(device.handle, args)

    def _python_open_unit(self, serial=None, resolution=None):
        if serial is None:
            handle, status = self._python_open_any_unit(resolution)
        else:
            handle, status = self._python_open_specific_unit(serial, resolution)

        if handle < 1:
            message = ("Driver %s could find no device" % self.name) + ("s" if serial is None else
                                                                        (" matching %s" % serial))
            if status is not None:
                message += " (%s)" % constants.pico_tag(status)
            raise DeviceNotFoundError(message)

        return handle

    def _python_open_any_unit(self, resolution):
        status = None
        if len(self._open_unit.argtypes) == 3:
            if resolution is None:
                resolution = self.DEFAULT_RESOLUTION
            chandle = c_int16()
            cresolution = c_int32()
            cresolution.value = resolution
            status = self._open_unit(byref(chandle), None, cresolution)
            handle = chandle.value
        elif len(self._open_unit.argtypes) == 2:
            chandle = c_int16()
            status = self._open_unit(byref(chandle), None)
            handle = chandle.value
        else:
            handle = self._open_unit()

        return handle, status

    def _python_open_specific_unit(self, serial, resolution):
        handle = -1
        status = None
        if len(self._open_unit.argtypes) == 3:
            if resolution is None:
                resolution = self.DEFAULT_RESOLUTION
            chandle = c_int16()
            cresolution = c_int32()
            cresolution.value = resolution
            cserial = create_string_buffer(serial)
            status = self._open_unit(byref(chandle), cserial, cresolution)
            handle = chandle.value
        elif len(self._open_unit.argtypes) == 2:
            chandle = c_int16()
            cserial = create_string_buffer(serial)
            status = self._open_unit(byref(chandle), cserial)
            handle = chandle.value
        else:
            open_handles = []
            temp_handle = self._open_unit()

            while temp_handle > 0:
                this_serial = self._python_get_unit_info(temp_handle, self.PICO_INFO["PICO_BATCH_AND_SERIAL"])
                if this_serial == serial:
                    handle = temp_handle
                    break
                open_handles.append(temp_handle)
                temp_handle = self._open_unit()

            for temp_handle in open_handles:
                self._python_close_unit(temp_handle)

        return handle, status

    def _python_close_unit(self, handle):
        return self._close_unit(c_int16(handle))

    @staticmethod
    def _create_empty_string_buffer():
        try:
            return create_string_buffer("\0", 255)
        except TypeError:
            return create_string_buffer("\0".encode('utf8'), 255)

    def _python_get_unit_info(self, handle, info_type):
        string_size = 255
        info = self._create_empty_string_buffer()
        if len(self._get_unit_info.argtypes) == 4:
            info_len = self._get_unit_info(c_int16(handle), info, c_int16(string_size), c_int16(info_type))
            if info_len > 0:
                return info.value[:info_len]
        elif len(self._get_unit_info.argtypes) == 5:
            required_size = c_int16(0)
            status = self._get_unit_info(c_int16(handle),
                                         info,
                                         c_int16(string_size),
                                         byref(required_size),
                                         c_uint32(info_type))
            if status == self.PICO_STATUS['PICO_OK']:
                if required_size.value < string_size:
                    return info.value[:required_size.value]
        return ""

    def _python_get_unit_info_wrapper(self, handle, keys):
        # verify that the requested keys are valid for this driver:
        invalid_info_lines = list(set(keys) - set(self.PICO_INFO.keys()))
        if invalid_info_lines:
            raise ArgumentOutOfRangeError("%s not available for %s devices" % (",".join(invalid_info_lines), self.name))

        if not keys:
            # backwards compatible behaviour from first release of this wrapper, which works on all drivers.
            UnitInfo = collections.namedtuple('UnitInfo', ['driver', 'variant', 'serial'])
            return UnitInfo(
                driver=self,
                variant=self._python_get_unit_info(handle, self.PICO_INFO["PICO_VARIANT_INFO"]),
                serial=self._python_get_unit_info(handle, self.PICO_INFO["PICO_BATCH_AND_SERIAL"])
            )

        # make a new type here, with the relevant keys.
        UnitInfo = collections.namedtuple('UnitInfo', list(keys))

        info_lines = {}

        for line in keys:
            info_lines[line] = self._python_get_unit_info(handle, self.PICO_INFO[line])

        return UnitInfo(**info_lines)

    @requires_device("set_channel requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def set_channel(self, device, channel_name='A', enabled=True, coupling='DC', range_peak=float('inf'),
                    analog_offset=None):
        """optional arguments:
        channel_name: a single channel (e.g. 'A')
        enabled: whether to enable the channel (boolean)
        coupling: string of the relevant enum member for your driver less the driver name prefix. e.g. 'DC' or 'AC'.
        range_peak: float which is the largest value you expect in the input signal. We will throw an exception if no
                    range on the device is large enough for that value.
        analog_offset: the meaning of 0 for this channel.
        return value: Max voltage of new range. Raises an exception in error cases."""

        excluded = ()
        reliably_resolved = False

        max_voltage = None

        while not reliably_resolved:
            if enabled:
                range_id, max_voltage = self._resolve_range(range_peak, excluded)
            else:
                range_id = 0
                max_voltage = None

            try:
                self._python_set_channel(device.handle,
                                         self.PICO_CHANNEL[channel_name],
                                         1 if enabled else 0,
                                         self.PICO_COUPLING[coupling],
                                         range_id,
                                         analog_offset)

                reliably_resolved = True
            except ValidRangeEnumValueNotValidForThisDevice:
                excluded += (range_id,)

        return max_voltage

    @requires_device("set_digital_port requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def set_digital_port(self, device, port_number=0, enabled=True, voltage_level=1.8):
        """Set the digital port

        Args:
            port_number (int): identifies the port for digital data. (e.g. 0 for digital channels 0-7)
            enabled (bool): whether or not to enable the channel (boolean)
            voltage_level (float): the voltage at which the state transitions between 0 and 1. Range: –5.0 to 5.0 (V).
        Raises:
            NotImplementedError: This device doesn't support digital ports.
            PicoError: set_digital_port failed
        """
        if hasattr(self, '_set_digital_port') and len(self._set_digital_port.argtypes) == 4:
            logic_level = voltage_to_logic_level(voltage_level)
            digital_ports = getattr(self, self.name.upper() + '_DIGITAL_PORT', None)
            if not digital_ports:
                raise NotImplementedError("This device doesn't support digital ports")
            port_id = digital_ports[self.name.upper() + "_DIGITAL_PORT" + str(port_number)]
            args = (device.handle, port_id, enabled, logic_level)
            converted_args = self._convert_args(self._set_digital_port, args)
            status = self._set_digital_port(*converted_args)
            if status != self.PICO_STATUS['PICO_OK']:
                raise PicoError(
                    f"set_digital_port failed ({constants.pico_tag(status)})")
        else:
            raise NotImplementedError("This device doesn't support digital ports or is not implemented yet")

    def _resolve_range(self, signal_peak, exclude=()):
        # we use >= so that someone can specify the range they want precisely.
        # we allow exclude so that if the smallest range in the header file isn't available on this device (or in this
        # configuration) we can exclude it from the collection. It should be the numerical enum constant (the key in
        # PICO_VOLTAGE_RANGE).
        possibilities = list(filter(lambda tup: tup[1] >= signal_peak and tup[0] not in exclude,
                                    self.PICO_VOLTAGE_RANGE.items()))

        if not possibilities:
            raise ArgumentOutOfRangeError("%s device doesn't support a range as wide as %sV" % (self.name, signal_peak))

        return min(possibilities, key=lambda i: i[1])

    def _python_set_channel(self, handle, channel_id, enabled, coupling_id, range_id, analog_offset):
        if len(self._set_channel.argtypes) == 5 and self._set_channel.argtypes[1] == c_int16:
            if analog_offset is not None:
                raise ArgumentOutOfRangeError("This device doesn't support analog offset")

            args = (handle, channel_id, enabled, coupling_id, range_id)
            converted_args = self._convert_args(self._set_channel, args)
            return_code = self._set_channel(*converted_args)

            if return_code == 0:
                raise ValidRangeEnumValueNotValidForThisDevice(
                    f"{self.PICO_VOLTAGE_RANGE[range_id]}V is out of range for this device.")
        elif len(self._set_channel.argtypes) == 5 and self._set_channel.argtypes[1] == c_int32 or (
             len(self._set_channel.argtypes) == 6):
            status = self.PICO_STATUS['PICO_OK']
            if len(self._set_channel.argtypes) == 6:
                if analog_offset is None:
                    analog_offset = 0.0
                args = (handle, channel_id, enabled, coupling_id, range_id, analog_offset)
                converted_args = self._convert_args(self._set_channel, args)
                status = self._set_channel(*converted_args)

            elif len(self._set_channel.argtypes) == 5 and self._set_channel.argtypes[1] == c_int32:
                if analog_offset is not None:
                    raise ArgumentOutOfRangeError("This device doesn't support analog offset")
                args = (handle, channel_id, enabled, coupling_id, range_id)
                converted_args = self._convert_args(self._set_channel, args)
                status = self._set_channel(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                if status == self.PICO_STATUS['PICO_INVALID_VOLTAGE_RANGE']:
                    raise ValidRangeEnumValueNotValidForThisDevice(
                        f"{self.PICO_VOLTAGE_RANGE[range_id]}V is out of range for this device.")
                if status == self.PICO_STATUS['PICO_INVALID_CHANNEL'] and not enabled:
                    # don't throw errors if the user tried to disable a missing channel.
                    return
                raise ArgumentOutOfRangeError(f"problem configuring channel ({constants.pico_tag(status)})")
        else:
            raise NotImplementedError("not done other driver types yet")

    @requires_device("memory_segments requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def memory_segments(self, device, number_segments):
        if not hasattr(self, '_memory_segments'):
            raise DeviceCannotSegmentMemoryError()
        max_samples = c_int32(0)
        status = self._memory_segments(c_int16(device.handle), c_uint32(number_segments), byref(max_samples))
        if status != self.PICO_STATUS['PICO_OK']:
            raise InvalidMemorySegmentsError("could not segment the device memory into (%s) segments (%s)" % (
                                              number_segments, constants.pico_tag(status)))
        return max_samples

    @requires_device("get_timebase requires a picosdk.device.Device instance, passed to the correct owning driver.")
    def get_timebase(self, device, timebase_id, no_of_samples, oversample=1, segment_index=0):
        """query the device about what time precision modes it can handle.
        note: the driver returns the timebase in nanoseconds, this function converts that into SI units (seconds)"""
        nanoseconds_result = self._python_get_timebase(device.handle,
                                                       timebase_id,
                                                       no_of_samples,
                                                       oversample,
                                                       segment_index)

        return TimebaseInfo(nanoseconds_result.timebase_id,
                            nanoseconds_result.time_interval * 1.e-9,
                            nanoseconds_result.time_units,
                            nanoseconds_result.max_samples,
                            nanoseconds_result.segment_id)

    def _python_get_timebase(self, handle, timebase_id, no_of_samples, oversample, segment_index):
        # We use get_timebase on ps2000 and ps3000 and parse the nanoseconds-int into a float.
        # on other drivers, we use get_timebase2, which gives us a float in the first place.
        if len(self._get_timebase.argtypes) == 7 and self._get_timebase.argtypes[1] == c_int16:
            time_interval = c_int32(0)
            time_units = c_int16(0)
            max_samples = c_int32(0)

            args = (handle, timebase_id, no_of_samples, time_interval,
                   time_units, oversample, max_samples)
            converted_args = self._convert_args(self._get_timebase, args)
            return_code = self._get_timebase(*converted_args)

            if return_code == 0:
                raise InvalidTimebaseError()

            return TimebaseInfo(timebase_id, float(time_interval.value), time_units.value, max_samples.value, None)
        elif hasattr(self, '_get_timebase2') and (
                len(self._get_timebase2.argtypes) == 7 and self._get_timebase2.argtypes[1] == c_uint32):
            time_interval = c_float(0.0)
            max_samples = c_int32(0)

            args = (handle, timebase_id, no_of_samples, time_interval,
                    oversample, max_samples, segment_index)
            converted_args = self._convert_args(self._get_timebase2, args)
            status = self._get_timebase2(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidTimebaseError(f"get_timebase2 failed ({constants.pico_tag(status)})")

            return TimebaseInfo(timebase_id, time_interval.value, None, max_samples.value, segment_index)
        else:
            raise NotImplementedError("not done other driver types yet")

    @requires_device()
    def set_null_trigger(self, device):
        auto_trigger_after_millis = 1
        if hasattr(self, '_set_trigger') and len(self._set_trigger.argtypes) == 6:
            PS2000_NONE = 5
            args = (device.handle, PS2000_NONE, 0, 0, 0, auto_trigger_after_millis)
            converted_args = self._convert_args(self._set_trigger, args)
            return_code = self._set_trigger(*converted_args)

            if return_code == 0:
                raise InvalidTriggerParameters()
        elif hasattr(self, '_set_simple_trigger') and len(self._set_simple_trigger.argtypes) == 7:
            threshold_direction_id = None
            if not self.PICO_THRESHOLD_DIRECTION:
                threshold_directions = getattr(self, self.name.upper() + '_THRESHOLD_DIRECTION', None)
                if not threshold_directions:
                    raise NotImplementedError("This device doesn't support threshold direction")
                threshold_direction_id = threshold_directions[self.name.upper() + '_NONE']
            else:
                threshold_direction_id = self.PICO_THRESHOLD_DIRECTION['NONE']
            args = (device.handle, False, self.PICO_CHANNEL['A'], 0,
                   threshold_direction_id, 0, auto_trigger_after_millis)
            converted_args = self._convert_args(self._set_simple_trigger, args)
            status = self._set_simple_trigger(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidTriggerParameters(f"set_simple_trigger failed ({constants.pico_tag(status)})")
        else:
            raise NotImplementedError("not done other driver types yet")

    @requires_device()
    def run_block(self, device, pre_trigger_samples, post_trigger_samples, timebase_id, oversample=1, segment_index=0):
        """tell the device to arm any triggers and start capturing in block mode now.
        returns: the approximate time (in seconds) which the device will take to capture with these settings."""
        return self._python_run_block(device.handle,
                                      pre_trigger_samples,
                                      post_trigger_samples,
                                      timebase_id,
                                      oversample,
                                      segment_index)

    def _python_run_block(self, handle, pre_samples, post_samples, timebase_id, oversample, segment_index):
        time_indisposed = c_int32(0)
        if len(self._run_block.argtypes) == 5:
            args = (handle, pre_samples + post_samples, timebase_id,
                   oversample, time_indisposed)
            converted_args = self._convert_args(self._run_block, args)
            return_code = self._run_block(*converted_args)

            if return_code == 0:
                raise InvalidCaptureParameters()
        elif len(self._run_block.argtypes) == 8:
            args = (handle, pre_samples, post_samples, timebase_id,
                    time_indisposed, segment_index, None, None)
            converted_args = self._convert_args(self._run_block, args)
            status = self._run_block(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidCaptureParameters(f"run_block failed ({constants.pico_tag(status)})")
        elif len(self._run_block.argtypes) == 9:
            args = (handle, pre_samples, post_samples, timebase_id,
                   oversample, time_indisposed, segment_index, None, None)
            converted_args = self._convert_args(self._run_block, args)
            status = self._run_block(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidCaptureParameters(f"run_block failed ({constants.pico_tag(status)})")
        else:
            raise NotImplementedError("not done other driver types yet")

        return float(time_indisposed.value) * 0.001

    @requires_device()
    def is_ready(self, device):
        """poll this function to find out when block mode is ready or has triggered.
        returns: True if data is ready, False otherwise."""
        if hasattr(self, '_ready') and len(self._ready.argtypes) == 1:
            return_code = self._ready(c_int16(device.handle))
            return bool(return_code)
        elif hasattr(self, '_is_ready') and len(self._is_ready.argtypes) == 2:
            is_ready = c_int16(0)
            status = self._is_ready(c_int16(device.handle), byref(is_ready))
            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidCaptureParameters("is_ready failed (%s)" % constants.pico_tag(status))
            return bool(is_ready.value)
        else:
            raise NotImplementedError("not done other driver types yet")

    @requires_device()
    def maximum_value(self, device):
        """Get the maximum ADC value for this device."""
        if not hasattr(self, '_maximum_value'):
            return (2**15)-1
        max_adc = c_int16(0)
        args = (device.handle, max_adc)
        converted_args = self._convert_args(self._maximum_value, args)
        self._maximum_value(*converted_args)
        return max_adc.value

    @requires_device()
    def get_values(self, device, active_channels, no_of_samples, segment_index=0):
        """Get captured data from the device.

        Args:
            device: Device instance
            active_channels: List of channels to get data from (port numbers included)
            no_of_samples: Number of samples to get
            segment_index: Memory segment to get data from

        Returns:
            Tuple of (results dict, overflow warnings dict)
        """
        if isinstance(active_channels, int):
            active_channels = [active_channels]
        results = {channel: numpy.empty(no_of_samples, numpy.dtype('int16'))
                  for channel in active_channels}
        overflow = c_int16(0)

        if len(self._get_values.argtypes) == 7 and self._get_timebase.argtypes[1] == c_int16:
            inputs = {k: None for k in 'ABCD'}
            for k, arr in results.items():
                inputs[k] = arr.ctypes.data

            args = (device.handle, inputs['A'], inputs['B'], inputs['C'],
                   inputs['D'], overflow, no_of_samples)
            converted_args = self._convert_args(self._get_values, args)
            return_code = self._get_values(*converted_args)

            if return_code == 0:
                raise InvalidCaptureParameters()
        elif len(self._get_values.argtypes) == 7 and self._get_timebase.argtypes[1] == c_uint32:
            # For this function pattern, we first call a function (self._set_data_buffer) to register each buffer. Then,
            # we can call self._get_values to actually populate them.
            available_channels = self.PICO_CHANNEL
            digital_ports = getattr(self, self.name.upper() + '_DIGITAL_PORT', None)
            if digital_ports:
                for digital_port, value in digital_ports.items():
                    if digital_port.startswith(self.name.upper() + '_DIGITAL_PORT'):
                        port_number = int(digital_port[-1])
                        available_channels[port_number] = value
            for channel, array in results.items():
                args = (device.handle, available_channels[channel], array.ctypes.data,
                       no_of_samples, segment_index, self.PICO_RATIO_MODE['NONE'])
                converted_args = self._convert_args(self._set_data_buffer, args)
                status = self._set_data_buffer(*converted_args)

                if status != self.PICO_STATUS['PICO_OK']:
                    raise InvalidCaptureParameters(f"set_data_buffer failed ({constants.pico_tag(status)})")

            samples_collected = c_uint32(no_of_samples)
            args = (device.handle, 0, samples_collected, 1,
                   self.PICO_RATIO_MODE['NONE'], segment_index, overflow)
            converted_args = self._convert_args(self._get_values, args)
            status = self._get_values(*converted_args)

            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidCaptureParameters(f"get_values failed ({constants.pico_tag(status)})")

        overflow_warning = {}
        if overflow.value:
            for channel in results.keys():
                if overflow.value & (1 >> self.PICO_CHANNEL[channel]):
                    overflow_warning[channel] = True

        return results, overflow_warning

    @requires_device()
    def stop(self, device):
        """Stop data capture."""
        args = (device.handle,)
        converted_args = self._convert_args(self._stop, args)

        if self._stop.restype == c_int16:
            return_code = self._stop(*converted_args)
            if isinstance(return_code, c_int16) and return_code == 0:
                raise InvalidCaptureParameters()
        else:
            status = self._stop(*converted_args)
            if status != self.PICO_STATUS['PICO_OK']:
                raise InvalidCaptureParameters(f"stop failed ({constants.pico_tag(status)})")

    @requires_device()
    def set_sig_gen_built_in(self, device, offset_voltage=0, pk_to_pk=2000000, wave_type="SINE",
                             start_frequency=1000.0, stop_frequency=1000.0, increment=0.0,
                             dwell_time=1.0, sweep_type="UP", operation='ES_OFF', shots=1, sweeps=1,
                             trigger_type="RISING", trigger_source="NONE", ext_in_threshold=0):
        """Set up the signal generator to output a built-in waveform.

        Args:
            device: Device instance
            offset_voltage: Offset voltage in microvolts (default 0)
            pk_to_pk: Peak-to-peak voltage in microvolts (default 2000000)
            wave_type: Type of waveform (e.g. "SINE", "SQUARE", "TRIANGLE")
            start_frequency: Start frequency in Hz (default 1000.0)
            stop_frequency: Stop frequency in Hz (default 1000.0)
            increment: Frequency increment in Hz (default 0.0)
            dwell_time: Time at each frequency in seconds (default 1.0)
            sweep_type: Sweep type (e.g. "UP", "DOWN", "UPDOWN")
            operation: Configures the white noise/PRBS (e.g. "ES_OFF", "WHITENOISE", "PRBS")
            shots: Number of shots per trigger (default 1)
            sweeps: Number of sweeps (default 1)
            trigger_type: Type of trigger (e.g. "RISING", "FALLING")
            trigger_source: Source of trigger (e.g. "NONE", "SCOPE_TRIG")
            ext_in_threshold: External trigger threshold in ADC counts

        Returns:
            None

        Raises:
            ArgumentOutOfRangeError: If parameters are invalid for device
        """
        prefix = self.name.upper()

        # Convert string parameters to enum values
        try:
            wave_type_val = getattr(self, f"{prefix}_WAVE_TYPE")[f"{prefix}_{wave_type.upper()}"]
            sweep_type_val = getattr(self, f"{prefix}_SWEEP_TYPE")[f"{prefix}_{sweep_type.upper()}"]
        except (AttributeError, KeyError) as e:
            raise ArgumentOutOfRangeError(f"Invalid wave_type or sweep_type for this device: {e}")

        # Check function signature and call appropriate version
        if len(self._set_sig_gen_built_in.argtypes) == 10:
            args = (device.handle, offset_voltage, pk_to_pk, wave_type_val,
                   start_frequency, stop_frequency, increment, dwell_time,
                   sweep_type_val, sweeps)
            converted_args = self._convert_args(self._set_sig_gen_built_in, args)
            status = self._set_sig_gen_built_in(*converted_args)

        elif len(self._set_sig_gen_built_in.argtypes) == 15:
            try:
                trigger_type_val = getattr(self, f"{prefix}_SIGGEN_TRIG_TYPE")[f"{prefix}_SIGGEN_{trigger_type.upper()}"]
                trigger_source_val = getattr(self, f"{prefix}_SIGGEN_TRIG_SOURCE")[f"{prefix}_SIGGEN_{trigger_source.upper()}"]
                extra_ops_val = getattr(self, f"{prefix}_EXTRA_OPERATIONS")[f"{prefix}_{operation.upper()}"]
            except (AttributeError, KeyError) as e:
                raise ArgumentOutOfRangeError(f"Invalid trigger parameters for this device: {e}")

            args = (device.handle, offset_voltage, pk_to_pk, wave_type_val,
                   start_frequency, stop_frequency, increment, dwell_time,
                   sweep_type_val, extra_ops_val, shots, sweeps,
                   trigger_type_val, trigger_source_val, ext_in_threshold)
            converted_args = self._convert_args(self._set_sig_gen_built_in, args)
            status = self._set_sig_gen_built_in(*converted_args)

        else:
            raise NotImplementedError("Signal generator not supported on this device")

        if status != self.PICO_STATUS["PICO_OK"]:
            raise PicoError(f"set_sig_gen_built_in failed: {constants.pico_tag(status)}")

    def _convert_args(self, func, args):
        """Convert arguments to match function argtypes.

        Args:
            func: The C function with argtypes defined
            args: Tuple of arguments to convert

        Returns:
            Tuple of converted arguments matching argtypes
        """
        if not hasattr(func, 'argtypes'):
            return args

        converted = []
        for arg, argtype in zip(args, func.argtypes):
            # Handle byref parameters
            if argtype == c_void_p and isinstance(arg, (c_int16, c_int32, c_uint32, c_float, c_double)):
                converted.append(byref(arg))
            # Handle normal parameters
            elif arg is not None:
                converted.append(argtype(arg))
            else:
                converted.append(None)
        return tuple(converted)

