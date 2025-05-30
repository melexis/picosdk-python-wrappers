#
# Copyright (C) 2015-2018 Pico Technology Ltd. See LICENSE file for terms.
#
"""
This is a Python module defining the functions from the ps4000aApi.h C header
file for PicoScope 4000 Series oscilloscopes using the ps4000a driver API
functions.
"""

from ctypes import *
from picosdk.library import Library
from picosdk.constants import make_enum
from picosdk.ctypes_wrapper import C_CALLBACK_FUNCTION_FACTORY

class Ps4000alib(Library):
    def __init__(self):
        super(Ps4000alib, self).__init__("ps4000a")


ps4000a = Ps4000alib()

ps4000a.PS4000A_COUPLING = make_enum([
    'PS4000A_AC',
    'PS4000A_DC',
])

# Just use AC and DC.
ps4000a.PICO_COUPLING = {k[-2:]: v for k, v in ps4000a.PS4000A_COUPLING.items()}

# A tuple in an enum like this is 2 names for the same value.
ps4000a.PS4000A_CHANNEL = {
    "PS4000A_CHANNEL_A" : 0,
    "PS4000A_CHANNEL_B" : 1,
    "PS4000A_CHANNEL_C" : 2,
    "PS4000A_CHANNEL_D" : 3,
    ("PS4000A_CHANNEL_E", "PS4000A_MAX_4_CHANNELS") : 4,
    "PS4000A_CHANNEL_F" : 5,
    "PS4000A_CHANNEL_G" : 6 ,
    "PS4000A_CHANNEL_H" : 7,
    ("PS4000A_MAX_CHANNELS", "PS4000A_EXTERNAL") : 8,
    "PS4000A_TRIGGER_AUX" : 9,
    "PS4000A_MAX_TRIGGER_SOURCES" : 10,
    "PS4000A_PULSE_WIDTH_SOURCE" : 0x10000000
}

ps4000a.PICO_CHANNEL = {}
prefix = "PS4000A_CHANNEL_"
for key, value in ps4000a.PS4000A_CHANNEL.items():
    if isinstance(key, tuple):
        key = key[0]  # Use the first name in the tuple.
    if key.startswith(prefix):
        key = key[len(prefix):]
        ps4000a.PICO_CHANNEL[key] = value  # Only channels are included (A, B, C, D, E, F, G, H).

# The voltage ranges for this driver are so oddly defined, that it is easier to describe them as a literal than trying
# to use make_enum:

def _define_ranges():
    # These are lower case to keep the python style police happy. They are available in the range dictionary with their
    # usual upper case names precisely as in the C header file.
    pico_x1_probe_10mv = 0
    pico_x1_probe_20mv = 1
    pico_x1_probe_50mv = 2
    pico_x1_probe_100mv = 3
    pico_x1_probe_200mv = 4
    pico_x1_probe_500mv = 5
    pico_x1_probe_1v = 6
    pico_x1_probe_2v = 7
    pico_x1_probe_5v = 8
    pico_x1_probe_10v = 9
    pico_x1_probe_20v = 10
    pico_x1_probe_50v = 11
    pico_x1_probe_100v = 12
    pico_x1_probe_200v = 13
    pico_x1_probe_ranges = (pico_x1_probe_200v + 1) - pico_x1_probe_10mv

    pico_ps4000a_resistance_315k = 0x00000200
    pico_ps4000a_resistance_1100k = pico_ps4000a_resistance_315k + 1
    pico_ps4000a_resistance_10m = pico_ps4000a_resistance_315k + 2
    pico_ps4000a_max_resistance_ranges = (pico_ps4000a_resistance_10m + 1) - pico_ps4000a_resistance_315k
    pico_ps4000a_resistance_adcv_flag = 0x10000000

    pico_connect_probe_off = 1024

    pico_d9_bnc_10mv = 0
    pico_d9_bnc_20mv = 1
    pico_d9_bnc_50mv = 2
    pico_d9_bnc_100mv = 3
    pico_d9_bnc_200mv = 4
    pico_d9_bnc_500mv = 5
    pico_d9_bnc_1v = 6
    pico_d9_bnc_2v = 7
    pico_d9_bnc_5v = 8
    pico_d9_bnc_10v = 9
    pico_d9_bnc_20v = 10
    pico_d9_bnc_50v = 11
    pico_d9_bnc_100v = 12
    pico_d9_bnc_200v = 13
    pico_max_d9_bnc_ranges = (pico_d9_bnc_200v + 1) - pico_d9_bnc_10mv

    pico_d9_2x_bnc_10mv = pico_d9_bnc_10mv
    pico_d9_2x_bnc_20mv = pico_d9_bnc_20mv
    pico_d9_2x_bnc_50mv = pico_d9_bnc_50mv
    pico_d9_2x_bnc_100mv = pico_d9_bnc_100mv
    pico_d9_2x_bnc_200mv = pico_d9_bnc_200mv
    pico_d9_2x_bnc_500mv = pico_d9_bnc_500mv
    pico_d9_2x_bnc_1v = pico_d9_bnc_1v
    pico_d9_2x_bnc_2v = pico_d9_bnc_2v
    pico_d9_2x_bnc_5v = pico_d9_bnc_5v
    pico_d9_2x_bnc_10v = pico_d9_bnc_10v
    pico_d9_2x_bnc_20v = pico_d9_bnc_20v
    pico_d9_2x_bnc_50v = pico_d9_bnc_50v
    pico_d9_2x_bnc_100v = pico_d9_bnc_100v
    pico_d9_2x_bnc_200v = pico_d9_bnc_200v
    pico_max_d9_2x_bnc_ranges = (pico_d9_2x_bnc_200v + 1) - pico_d9_2x_bnc_10mv

    pico_differential_10mv = pico_d9_bnc_10mv
    pico_differential_20mv = pico_d9_bnc_20mv
    pico_differential_50mv = pico_d9_bnc_50mv
    pico_differential_100mv = pico_d9_bnc_100mv
    pico_differential_200mv = pico_d9_bnc_200mv
    pico_differential_500mv = pico_d9_bnc_500mv
    pico_differential_1v = pico_d9_bnc_1v
    pico_differential_2v = pico_d9_bnc_2v
    pico_differential_5v = pico_d9_bnc_5v
    pico_differential_10v = pico_d9_bnc_10v
    pico_differential_20v = pico_d9_bnc_20v
    pico_differential_50v = pico_d9_bnc_50v
    pico_differential_100v = pico_d9_bnc_100v
    pico_differential_200v = pico_d9_bnc_200v
    pico_max_differential_ranges = (pico_differential_200v + 1) - pico_differential_10mv,

    pico_current_clamp_200a_2ka_1a = 4000
    pico_current_clamp_200a_2ka_2a = pico_current_clamp_200a_2ka_1a + 1
    pico_current_clamp_200a_2ka_5a = pico_current_clamp_200a_2ka_1a + 2
    pico_current_clamp_200a_2ka_10a = pico_current_clamp_200a_2ka_1a + 3
    pico_current_clamp_200a_2ka_20a = pico_current_clamp_200a_2ka_1a + 4
    pico_current_clamp_200a_2ka_50a = pico_current_clamp_200a_2ka_1a + 5
    pico_current_clamp_200a_2ka_100a = pico_current_clamp_200a_2ka_1a + 6
    pico_current_clamp_200a_2ka_200a = pico_current_clamp_200a_2ka_1a + 7
    pico_current_clamp_200a_2ka_500a = pico_current_clamp_200a_2ka_1a + 8
    pico_current_clamp_200a_2ka_1000a = pico_current_clamp_200a_2ka_1a + 9
    pico_current_clamp_200a_2ka_2000a = pico_current_clamp_200a_2ka_1a + 10
    pico_max_current_clamp_200a_2ka_ranges = (pico_current_clamp_200a_2ka_2000a + 1) - pico_current_clamp_200a_2ka_1a

    pico_current_clamp_40a_100ma = 5000
    pico_current_clamp_40a_200ma = pico_current_clamp_40a_100ma + 1
    pico_current_clamp_40a_500ma = pico_current_clamp_40a_100ma + 2
    pico_current_clamp_40a_1a = pico_current_clamp_40a_100ma + 3
    pico_current_clamp_40a_2a = pico_current_clamp_40a_100ma + 4
    pico_current_clamp_40a_5a = pico_current_clamp_40a_100ma + 5
    pico_current_clamp_40a_10a = pico_current_clamp_40a_100ma + 6
    pico_current_clamp_40a_20a = pico_current_clamp_40a_100ma + 7
    pico_current_clamp_40a_40a = pico_current_clamp_40a_100ma + 8
    pico_max_current_clamp_40a_ranges = (pico_current_clamp_40a_40a + 1) - pico_current_clamp_40a_100ma

    pico_1kv_2_5v = 6003
    pico_1kv_5v = pico_1kv_2_5v + 1
    pico_1kv_12_5v = pico_1kv_2_5v + 2
    pico_1kv_25v = pico_1kv_2_5v + 3
    pico_1kv_50v = pico_1kv_2_5v + 4
    pico_1kv_125v = pico_1kv_2_5v + 5
    pico_1kv_250v = pico_1kv_2_5v + 6
    pico_1kv_500v = pico_1kv_2_5v + 7
    pico_1kv_1000v = pico_1kv_2_5v + 8
    pico_max_1kv_ranges = (pico_1kv_1000v + 1) - pico_1kv_2_5v

    return {k.upper(): v for k, v in locals().items() if k.startswith("pico")}


ps4000a.PICO_CONNECT_PROBE_RANGE = _define_ranges()


def process_enum(enum):
    """The PS4000a range enum is complicated enough that we need some clearer logic:"""
    import re
    pattern = re.compile(r'PICO_X1_PROBE_([0-9]+M?)V')

    voltage_range = {}

    for enum_item_name, enum_item_value in enum.items():
        match = pattern.match(enum_item_name)
        if match is None:
            continue
        voltage_string = match.group(1)
        voltage = float(voltage_string) if voltage_string[-1] != 'M' else (0.001 * float(voltage_string[:-1]))

        voltage_range[enum_item_value] = voltage

    return voltage_range


ps4000a.PICO_VOLTAGE_RANGE = process_enum(ps4000a.PICO_CONNECT_PROBE_RANGE)

class PS4000A_USER_PROBE_INTERACTIONS(Structure):
    _pack_ = 1
    _fields_ = [    ("connected", c_uint16),

                    ("channel", c_int32),
                    ("enabled", c_uint16),

                    ("probeName", c_uint32),

                    ("requiresPower_", c_uint8),
                    ("isPowered_", c_uint8),

                    ("status", c_uint32),

                    ("probeOff", c_uint32),

                    ("rangeFirst_", c_uint32),
                    ("rangeLast_", c_uint32),
                    ("rangeCurrent_", c_uint32),

                    ("couplingFirst_", c_uint32),
                    ("couplingLast_", c_uint32),
                    ("couplingCurrent_", c_uint32),
                    ("couplingLast_", c_uint32),

                    ("filterFlags_", c_uint32),
                    ("filterCurrent_", c_uint32),
                    ("defaultFilter_", c_uint32)]
ps4000a.PS4000A_USER_PROBE_INTERACTIONS = PS4000A_USER_PROBE_INTERACTIONS

ps4000a.PS4000A_RATIO_MODE = {
    'PS4000A_RATIO_MODE_NONE': 0,
    'PS4000A_RATIO_MODE_AGGREGATE': 1,
    'PS4000A_RATIO_MODE_DECIMATE': 2,
    'PS4000A_RATIO_MODE_AVERAGE': 4,
}

ps4000a.PICO_RATIO_MODE = {k[19:]: v for k, v in ps4000a.PS4000A_RATIO_MODE.items()}

ps4000a.PS4000A_TIME_UNITS = make_enum([
    'PS4000A_FS',
    'PS4000A_PS',
    'PS4000A_NS',
    'PS4000A_US',
    'PS4000A_MS',
    'PS4000A_S',
    'PS4000A_MAX_TIME_UNITS',
])

ps4000a.PS4000A_WAVE_TYPE = make_enum([
	'PS4000A_SINE',
	'PS4000A_SQUARE',
	'PS4000A_TRIANGLE',
	'PS4000A_RAMP_UP',
	'PS4000A_RAMP_DOWN',
	'PS4000A_SINC',
	'PS4000A_GAUSSIAN',
	'PS4000A_HALF_SINE',
	'PS4000A_DC_VOLTAGE',
	'PS4000A_WHITE_NOISE',
	'PS4000A_MAX_WAVE_TYPES',
])

ps4000a.PS4000A_SWEEP_TYPE = make_enum([
	'PS4000A_UP',
	'PS4000A_DOWN',
	'PS4000A_UPDOWN',
	'PS4000A_DOWNUP',
	'PS4000A_MAX_SWEEP_TYPES',
])

ps4000a.PS4000A_SIGGEN_TRIG_TYPE = make_enum([
	'PS4000A_SIGGEN_RISING',
	'PS4000A_SIGGEN_FALLING',
	'PS4000A_SIGGEN_GATE_HIGH',
	'PS4000A_SIGGEN_GATE_LOW',
])

ps4000a.PS4000A_SIGGEN_TRIG_SOURCE = make_enum([
	'PS4000A_SIGGEN_NONE',
	'PS4000A_SIGGEN_SCOPE_TRIG',
	'PS4000A_SIGGEN_AUX_IN',
	'PS4000A_SIGGEN_EXT_IN',
	'PS4000A_SIGGEN_SOFT_TRIG',
])

ps4000a.PS4000A_INDEX_MODE = make_enum([
	'PS4000A_SINGLE',
	'PS4000A_DUAL',
	'PS4000A_QUAD',
	'PS4000A_MAX_INDEX_MODES',
])

ps4000a.PS4000A_EXTRA_OPERATIONS = make_enum([
	'PS4000A_ES_OFF',
	'PS4000A_WHITENOISE',
	'PS4000A_PRBS',
])

def _define_conditions_info():
    PICO_CLEAR = 0x00000001
    PICO_ADD = 0x00000002

    return {k.upper(): v for k, v in locals().items() if k.startswith("PICO")}

ps4000a.PS4000A_CONDITIONS_INFO = _define_conditions_info()

ps4000a.PS4000A_THRESHOLD_DIRECTION = make_enum([
    ("PS4000A_ABOVE", "PS4000A_INSIDE"),
    ("PS4000A_BELOW", "PS4000A_OUTSIDE"),
    ("PS4000A_RISING", "PS4000A_ENTER", "PS4000A_NONE"),
    ("PS4000A_FALLING", "PS4000A_EXIT"),
    ("PS4000A_RISING_OR_FALLING", "PS4000A_ENTER_OR_EXIT"),
    "PS4000A_ABOVE_LOWER",
    "PS4000A_BELOW_LOWER",
    "PS4000A_RISING_LOWER",
    "PS4000A_FALLING_LOWER",
    "PS4000A_POSITIVE_RUNT",
    "PS4000A_NEGATIVE_RUNT",
])

ps4000a.PS4000A_THRESHOLD_MODE = make_enum([
    "PS4000A_LEVEL",
    "PS4000A_WINDOW"
])

ps4000a.PS4000A_TRIGGER_STATE = make_enum([
    "PS4000A_DONT_CARE",
    "PS4000A_TRUE",
    "PS4000A_FALSE"
])

ps4000a.PS4000A_PULSE_WIDTH_TYPE = make_enum([
    "PW_TYPE NONE",
    "PW_TYPE_LESS_THAN",
    "PW_TYPE_GREATER_THAN",
    "PW_TYPE_IN_RANGE",
    "PW_TYPE_OUT_OF_RANGE"
])

class PS4000A_CONDITION (Structure):
	_pack_ = 1
	_fields_ = [("source", c_int32),
	("condition", c_int32)]

ps4000a.PS4000A_CONDITION = PS4000A_CONDITION

class PS4000A_DIRECTION(Structure):
    _pack_ = 1
    _fields_ = [("channel", c_int32),
                ("direction", c_int32)]

ps4000a.PS4000A_DIRECTION = PS4000A_DIRECTION

class PS4000A_TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [("thresholdUpper", c_int16),
                ("thresholdUpperHysteresis", c_uint16),
                ("thresholdLower", c_int16),
                ("thresholdLowerHysteresis", c_uint16),
                ("channel", c_int32),
                ("thresholdMode", c_int32)]

ps4000a.PS4000A_TRIGGER_CHANNEL_PROPERTIES = PS4000A_TRIGGER_CHANNEL_PROPERTIES

doc = """ PICO_STATUS ps4000aOpenUnit
    (
        int16_t *handle,
        int8_t  *serial
    ); """
ps4000a.make_symbol("_open_unit", "ps4000aOpenUnit", c_uint32, [c_void_p, c_char_p], doc)

doc = """ PICO_STATUS ps4000aOpenUnitAsync
    (
        int16_t *status,
        int8_t  *serial
    ); """
ps4000a.make_symbol("_open_unit_async", "ps4000aOpenUnitAsync", c_uint32, [c_void_p, c_char_p], doc)

doc = """ PICO_STATUS ps4000aOpenUnitProgress
    (
        int16_t *handle,
        int16_t *progressPercent,
        int16_t *complete
    ); """
ps4000a.make_symbol("_open_unit_progress", "ps4000aOpenUnitProgress", c_uint32, [c_void_p, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetUnitInfo
    (
        int16_t    handle,
        int8_t    *string,
        int16_t    stringLength,
        int16_t   *requiredSize,
        PICO_INFO  info
    ); """
ps4000a.make_symbol("_get_unit_info", "ps4000aGetUnitInfo", c_uint32, [c_int16, c_char_p, c_int16, c_void_p, c_uint32],
                    doc)

doc = """ PICO_STATUS ps4000aFlashLed
    (
        int16_t  handle,
        int16_t  start
    ); """
ps4000a.make_symbol("_flash_led", "ps4000aFlashLed", c_uint32, [c_int16, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetChannelLed
    (
        int16_t                      handle,
        PS4000A_CHANNEL_LED_SETTING *ledStates,
        uint16_t                     nLedStates
    ); """
ps4000a.make_symbol("_set_channel_led", "ps4000aSetChannelLed", c_uint32, [c_int16, c_void_p, c_uint16], doc)

doc = """ PICO_STATUS ps4000aIsLedFlashing
    (
        int16_t  handle,
        int16_t *status
    ); """
ps4000a.make_symbol("_is_led_flashing", "ps4000aIsLedFlashing", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aCloseUnit
    (
        int16_t  handle
    ); """
ps4000a.make_symbol("_close_unit", "ps4000aCloseUnit", c_uint32, [c_int16, ], doc)

doc = """ PICO_STATUS ps4000aMemorySegments
    (
        int16_t   handle,
        uint32_t  nSegments,
        int32_t  *nMaxSamples
    ); """
ps4000a.make_symbol("_memory_segments", "ps4000aMemorySegments", c_uint32, [c_int16, c_uint32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSetChannel
    (
        int16_t           handle,
        PS4000A_CHANNEL   channel,
        int16_t           enabled,
        PS4000A_COUPLING  type,
        PS4000A_RANGE     range,
        float             analogOffset
    ); """
ps4000a.make_symbol("_set_channel", "ps4000aSetChannel", c_uint32,
                    [c_int16, c_int32, c_int16, c_int32, c_int32, c_float], doc)

doc = """ PICO_STATUS ps4000aSetBandwidthFilter
    (
        int16_t                    handle,
        PS4000A_CHANNEL            channel,
        PS4000A_BANDWIDTH_LIMITER  bandwidth
    ); """
ps4000a.make_symbol("_set_bandwidth_filter", "ps4000aSetBandwidthFilter", c_uint32, [c_int16, c_int32, c_int32], doc)

doc = """ PICO_STATUS ps4000aApplyResistanceScaling
    (
        int16_t          handle,
        PS4000A_CHANNEL  channel,
        PS4000A_RANGE    range,
        int16_t         *bufferMax,
        int16_t         *bufferMin,
        uint32_t         buffertLth,
        int16_t         *overflow
    ); """
ps4000a.make_symbol("_apply_resistance_scaling", "ps4000aApplyResistanceScaling", c_uint32,
                    [c_int16, c_int32, c_int32, c_int16, c_int16, c_uint32, c_int16], doc)

doc = """ PICO_STATUS ps4000aGetTimebase
    (
        int16_t   handle,
        uint32_t  timebase,
        int32_t   noSamples,
        int32_t  *timeIntervalNanoseconds,
        int32_t  *maxSamples,
        uint32_t  segmentIndex
    ); """
ps4000a.make_symbol('_get_timebase', 'ps4000aGetTimebase', c_uint32,
                    [c_int16, c_uint32, c_int32, c_void_p, c_void_p, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetTimebase2
    (
        int16_t   handle,
        uint32_t  timebase,
        int32_t   noSamples,
        float    *timeIntervalNanoseconds,
        int32_t  *maxSamples,
        uint32_t  segmentIndex
    ); """
ps4000a.make_symbol("_get_timebase2", "ps4000aGetTimebase2", c_uint32,
                    [c_int16, c_uint32, c_int32, c_void_p, c_void_p, c_uint32], doc)

doc = """ PICO_STATUS ps4000aSetSigGenArbitrary
    (
        int16_t                     handle,
        int32_t                     offsetVoltage,
        uint32_t                    pkToPk,
        uint32_t                    startDeltaPhase,
        uint32_t                    stopDeltaPhase,
        uint32_t                    deltaPhaseIncrement,
        uint32_t                    dwellCount,
        int16_t                    *arbitraryWaveform,
        int32_t                     arbitraryWaveformSize,
        PS4000A_SWEEP_TYPE          sweepType,
        PS4000A_EXTRA_OPERATIONS    operation,
        PS4000A_INDEX_MODE          indexMode,
        uint32_t                    shots,
        uint32_t                    sweeps,
        PS4000A_SIGGEN_TRIG_TYPE    triggerType,
        PS4000A_SIGGEN_TRIG_SOURCE  triggerSource,
        int16_t                     extInThreshold
    ); """
ps4000a.make_symbol("_set_sig_gen_arbitrary", "ps4000aSetSigGenArbitrary", c_uint32,
                    [c_int16, c_int32, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p,
                     c_int32, c_int32, c_int32, c_int32, c_uint32, c_uint32, c_int32, c_int32, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetSigGenBuiltIn
    (
        int16_t                     handle,
        int32_t                     offsetVoltage,
        uint32_t                    pkToPk,
        PS4000A_WAVE_TYPE           waveType,
        double                      startFrequency,
        double                      stopFrequency,
        double                      increment,
        double                      dwellTime,
        PS4000A_SWEEP_TYPE          sweepType,
        PS4000A_EXTRA_OPERATIONS    operation,
        uint32_t                    shots,
        uint32_t                    sweeps,
        PS4000A_SIGGEN_TRIG_TYPE    triggerType,
        PS4000A_SIGGEN_TRIG_SOURCE  triggerSource,
        int16_t                     extInThreshold
    ); """
ps4000a.make_symbol("_set_sig_gen_built_in", "ps4000aSetSigGenBuiltIn", c_uint32,
                    [c_int16, c_int32, c_uint32, c_int32, c_double, c_double, c_double, c_double,
                     c_int32, c_int32, c_uint32, c_uint32, c_int32, c_int32, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetSigGenPropertiesArbitrary
    (
        int16_t                     handle,
        uint32_t                    startDeltaPhase,
        uint32_t                    stopDeltaPhase,
        uint32_t                    deltaPhaseIncrement,
        uint32_t                    dwellCount,
        PS4000A_SWEEP_TYPE          sweepType,
        uint32_t                    shots,
        uint32_t                    sweeps,
        PS4000A_SIGGEN_TRIG_TYPE    triggerType,
        PS4000A_SIGGEN_TRIG_SOURCE  triggerSource,
        int16_t                     extInThreshold
    ); """
ps4000a.make_symbol("_set_sig_gen_properties_arbitrary", "ps4000aSetSigGenPropertiesArbitrary", c_uint32,
                    [c_int16, c_uint32, c_uint32, c_uint32, c_uint32, c_int32, c_uint32, c_uint32, c_int32, c_int32,
                     c_int16], doc)

doc = """ PICO_STATUS ps4000aSetSigGenPropertiesBuiltIn
    (
        int16_t                     handle,
        double                      startFrequency,
        double                      stopFrequency,
        double                      increment,
        double                      dwellTime,
        PS4000A_SWEEP_TYPE          sweepType,
        uint32_t                    shots,
        uint32_t                    sweeps,
        PS4000A_SIGGEN_TRIG_TYPE    triggerType,
        PS4000A_SIGGEN_TRIG_SOURCE  triggerSource,
        int16_t                     extInThreshold
    ); """
ps4000a.make_symbol("_set_sig_gen_properties_built_in", "ps4000aSetSigGenPropertiesBuiltIn", c_uint32,
                    [c_int16, c_double, c_double, c_double, c_double, c_int32, c_uint32, c_uint32, c_int32, c_int32,
                     c_int16], doc)

doc = """ PICO_STATUS ps4000aSigGenFrequencyToPhase
    (
        int16_t             handle,
        double              frequency,
        PS4000A_INDEX_MODE  indexMode,
        uint32_t            bufferLength,
        uint32_t           *phase
    ); """
ps4000a.make_symbol("_sig_gen_frequency_to_phase", "ps4000aSigGenFrequencyToPhase", c_uint32,
                    [c_int16, c_double, c_int32, c_uint32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSigGenArbitraryMinMaxValues
    (
        int16_t   handle,
        int16_t  *minArbitraryWaveformValue,
        int16_t  *maxArbitraryWaveformValue,
        uint32_t *minArbitraryWaveformSize,
        uint32_t *maxArbitraryWaveformSize
    ); """
ps4000a.make_symbol("_sig_gen_arbitrary_min_max_values", "ps4000aSigGenArbitraryMinMaxValues", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSigGenSoftwareControl
    (
        int16_t  handle,
        int16_t  state
    );"""
ps4000a.make_symbol("_sig_gen_software_control", "ps4000aSigGenSoftwareControl", c_uint32, [c_int16, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetEts
    (
        int16_t           handle,
        PS4000A_ETS_MODE  mode,
        int16_t           etsCycles,
        int16_t           etsInterleave,
        int32_t          *sampleTimePicoseconds
    ); """
ps4000a.make_symbol("_set_ets", "ps4000aSetEts", c_uint32, [c_int16, c_int32, c_int16, c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSetTriggerChannelProperties
    (
        int16_t                             handle,
        PS4000A_TRIGGER_CHANNEL_PROPERTIES *channelProperties,
        int16_t                             nChannelProperties,
        int16_t                             auxOutputEnable,
        int32_t                             autoTriggerMilliseconds
    ); """
ps4000a.make_symbol("_set_trigger_channel_properties", "ps4000aSetTriggerChannelProperties", c_uint32,
                    [c_int16, c_void_p, c_int16, c_int16, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetTriggerChannelConditions
    (
        int16_t                  handle,
        PS4000A_CONDITION       *conditions,
        int16_t                  nConditions,
        PS4000A_CONDITIONS_INFO  info
    ); """
ps4000a.make_symbol("_set_trigger_channel_conditions", "ps4000aSetTriggerChannelConditions", c_uint32,
                    [c_int16, c_void_p, c_int16, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetTriggerChannelDirections
    (
        int16_t            handle,
        PS4000A_DIRECTION *directions,
        int16_t            nDirections
    ); """
ps4000a.make_symbol("_set_trigger_channel_directions", "ps4000aSetTriggerChannelDirections", c_uint32,
                    [c_int16, c_void_p, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetSimpleTrigger
    (
        int16_t                      handle,
        int16_t                      enable,
        PS4000A_CHANNEL              source,
        int16_t                      threshold,
        PS4000A_THRESHOLD_DIRECTION  direction,
        uint32_t                     delay,
        int16_t                      autoTrigger_ms
    ); """
ps4000a.make_symbol("_set_simple_trigger", "ps4000aSetSimpleTrigger", c_uint32,
                    [c_int16, c_int16, c_int32, c_int16, c_int32, c_uint32, c_int16], doc)

doc = """ PICO_STATUS ps4000aSetTriggerDelay
    (
        int16_t   handle,
        uint32_t  delay
    ); """
ps4000a.make_symbol("_set_trigger_delay", "ps4000aSetTriggerDelay", c_uint32, [c_int16, c_uint32], doc)

doc = """ PICO_STATUS ps4000aSetPulseWidthQualifierProperties
    (
        int16_t                      handle,
        PS4000A_THRESHOLD_DIRECTION  direction,
        uint32_t                     lower,
        uint32_t                     upper,
        PS4000A_PULSE_WIDTH_TYPE     type
    ); """
ps4000a.make_symbol("_set_pulse_width_qualifier_properties", "ps4000aSetPulseWidthQualifierProperties", c_uint32,
                    [c_int16, c_int32, c_uint32, c_uint32, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetPulseWidthQualifierConditions
    (
        int16_t                  handle,
        PS4000A_CONDITION       *conditions,
        int16_t                  nConditions,
        PS4000A_CONDITIONS_INFO  info
    ); """
ps4000a.make_symbol("_set_pulse_width_qualifier_conditions", "ps4000aSetPulseWidthQualifierConditions", c_uint32,
                    [c_int16, c_void_p, c_int16, c_int32], doc)

doc = """ PICO_STATUS ps4000aIsTriggerOrPulseWidthQualifierEnabled
    (
        int16_t  handle,
        int16_t *triggerEnabled,
        int16_t *pulseWidthQualifierEnabled
    ); """
ps4000a.make_symbol("_is_trigger_or_pulse_width_qualifier_enabled", "ps4000aIsTriggerOrPulseWidthQualifierEnabled", c_uint32,
                    [c_int16, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetTriggerTimeOffset
    (
        int16_t             handle,
        uint32_t           *timeUpper,
        uint32_t           *timeLower,
        PS4000A_TIME_UNITS *timeUnits,
        uint32_t            segmentIndex
    ); """
ps4000a.make_symbol("_get_trigger_time_offset", "ps4000aGetTriggerTimeOffset", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_void_p, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetTriggerTimeOffset64
    (
        int16_t             handle,
        int64_t            *time,
        PS4000A_TIME_UNITS *timeUnits,
        uint32_t            segmentIndex
    ); """
ps4000a.make_symbol("_get_trigger_time_offset64", "ps4000aGetTriggerTimeOffset64", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetValuesTriggerTimeOffsetBulk
    (
        int16_t             handle,
        uint32_t           *timesUpper,
        uint32_t           *timesLower,
        PS4000A_TIME_UNITS *timeUnits,
        uint32_t            fromSegmentIndex,
        uint32_t            toSegmentIndex
    ); """
ps4000a.make_symbol("_get_values_trigger_time_offset_bulk", "ps4000aGetValuesTriggerTimeOffsetBulk", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_void_p, c_uint32, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetValuesTriggerTimeOffsetBulk64
    (
        int16_t             handle,
        int64_t            *times,
        PS4000A_TIME_UNITS *timeUnits,
        uint32_t            fromSegmentIndex,
        uint32_t            toSegmentIndex
    ); """
ps4000a.make_symbol("_get_values_trigger_time_offset_bulk64", "ps4000aGetValuesTriggerTimeOffsetBulk64", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_uint32, c_uint32], doc)

doc = """ PICO_STATUS ps4000aSetDataBuffers
    (
        int16_t             handle,
        PS4000A_CHANNEL     channel,
        int16_t            *bufferMax,
        int16_t            *bufferMin,
        int32_t             bufferLth,
        uint32_t            segmentIndex,
        PS4000A_RATIO_MODE  mode
    ); """
ps4000a.make_symbol("_set_data_buffers", "ps4000aSetDataBuffers", c_uint32,
                    [c_int16, c_int32, c_void_p, c_void_p, c_int32, c_uint32, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetDataBuffer
    (
        int16_t             handle,
        PS4000A_CHANNEL     channel,
        int16_t            *buffer,
        int32_t             bufferLth,
        uint32_t            segmentIndex,
        PS4000A_RATIO_MODE  mode
    ); """
ps4000a.make_symbol("_set_data_buffer", "ps4000aSetDataBuffer", c_uint32,
                    [c_int16, c_int32, c_void_p, c_int32, c_uint32, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetEtsTimeBuffer
    (
        int16_t  handle,
        int64_t *buffer,
        int32_t  bufferLth
    ); """
ps4000a.make_symbol("_set_ets_time_buffer", "ps4000aSetEtsTimeBuffer", c_uint32, [c_int16, c_void_p, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetEtsTimeBuffers
    (
        int16_t   handle,
        uint32_t *timeUpper,
        uint32_t *timeLower,
        int32_t   bufferLth
    ); """
ps4000a.make_symbol("_set_ets_time_buffers", "ps4000aSetEtsTimeBuffers", c_uint32, [c_int16, c_void_p, c_void_p, c_int32],
                    doc)

doc = """ PICO_STATUS ps4000aIsReady
    (
        int16_t  handle,
        int16_t *ready
    ); """
ps4000a.make_symbol("_is_ready", "ps4000aIsReady", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aRunBlock
    (
        int16_t            handle,
        int32_t            noOfPreTriggerSamples,
        int32_t            noOfPostTriggerSamples,
        uint32_t           timebase,
        int32_t           *timeIndisposedMs,
        uint32_t           segmentIndex,
        ps4000aBlockReady  lpReady,
        void              *pParameter
    ); """
ps4000a.make_symbol("_run_block", "ps4000aRunBlock", c_uint32,
                    [c_int16, c_int32, c_int32, c_uint32, c_void_p, c_uint32, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aRunStreaming
    (
        int16_t             handle,
        uint32_t           *sampleInterval,
        PS4000A_TIME_UNITS  sampleIntervalTimeUnits,
        uint32_t            maxPreTriggerSamples,
        uint32_t            maxPostTriggerSamples,
        int16_t             autoStop,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            overviewBufferSize
    ); """
ps4000a.make_symbol("_run_streaming", "ps4000aRunStreaming", c_uint32,
                    [c_int16, c_void_p, c_int32, c_uint32, c_uint32, c_int16, c_uint32, c_int32, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetStreamingLatestValues
    (
        int16_t                handle,
        ps4000aStreamingReady  lpPs4000aReady,
        void                  *pParameter
    ); """
ps4000a.make_symbol("_get_streaming_latest_values", "ps4000aGetStreamingLatestValues", c_uint32,
                    [c_int16, c_void_p, c_void_p], doc)

doc = """ void *ps4000aStreamingReady
    (
        int16_t   handle,
        int32_t   noOfSamples,
        uint32_t  startIndex,
        int16_t   overflow,
        uint32_t  triggerAt,
        int16_t   triggered,
        int16_t   autoStop,
        void     *pParameter
    );
    define a python function which accepts the correct arguments, and pass it to the constructor of this type.
    """

ps4000a.StreamingReadyType = C_CALLBACK_FUNCTION_FACTORY(None,
                                                         c_int16,
                                                         c_int32,
                                                         c_uint32,
                                                         c_int16,
                                                         c_uint32,
                                                         c_int16,
                                                         c_int16,
                                                         c_void_p)

ps4000a.StreamingReadyType.__doc__ = doc


doc = """ PICO_STATUS ps4000aNoOfStreamingValues
    (
        int16_t   handle,
        uint32_t *noOfValues
    ); """
ps4000a.make_symbol("_no_of_streaming_values", "ps4000aNoOfStreamingValues", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetMaxDownSampleRatio
    (
        int16_t             handle,
        uint32_t            noOfUnaggreatedSamples,
        uint32_t           *maxDownSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            segmentIndex
    ); """
ps4000a.make_symbol("_get_max_down_sample_ratio", "ps4000aGetMaxDownSampleRatio", c_uint32,
                    [c_int16, c_uint32, c_void_p, c_int32, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetValues
    (
        int16_t             handle,
        uint32_t            startIndex,
        uint32_t           *noOfSamples,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            segmentIndex,
        int16_t            *overflow
    ); """
ps4000a.make_symbol("_get_values", "ps4000aGetValues", c_uint32,
                    [c_int16, c_uint32, c_void_p, c_uint32, c_int32, c_uint32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetValuesAsync
    (
        int16_t             handle,
        uint32_t            startIndex,
        uint32_t            noOfSamples,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            segmentIndex,
        void               *lpDataReady,
        void               *pParameter
    ); """
ps4000a.make_symbol("_get_values_async", "ps4000aGetValuesAsync", c_uint32,
                    [c_int16, c_uint32, c_uint32, c_uint32, c_int32, c_uint32, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetValuesBulk
    (
        int16_t             handle,
        uint32_t           *noOfSamples,
        uint32_t            fromSegmentIndex,
        uint32_t            toSegmentIndex,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        int16_t            *overflow
    ); """
ps4000a.make_symbol("_get_values_bulk", "ps4000aGetValuesBulk", c_uint32,
                    [c_int16, c_void_p, c_uint32, c_uint32, c_uint32, c_int32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetValuesOverlapped
    (
        int16_t             handle,
        uint32_t            startIndex,
        uint32_t           *noOfSamples,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            segmentIndex,
        int16_t            *overflow
    ); """
ps4000a.make_symbol("_get_values_overlapped", "ps4000aGetValuesOverlapped", c_uint32,
                    [c_int16, c_uint32, c_void_p, c_uint32, c_int32, c_uint32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetValuesOverlappedBulk
    (
        int16_t             handle,
        uint32_t            startIndex,
        uint32_t           *noOfSamples,
        uint32_t            downSampleRatio,
        PS4000A_RATIO_MODE  downSampleRatioMode,
        uint32_t            fromSegmentIndex,
        uint32_t            toSegmentIndex,
        int16_t            *overflow
    ); """
ps4000a.make_symbol("_get_values_overlapped_bulk", "ps4000aGetValuesOverlappedBulk", c_uint32,
                    [c_int16, c_uint32, c_void_p, c_uint32, c_int32, c_uint32, c_uint32, c_void_p], doc)

doc = """ PICO_STATUS ps4000aEnumerateUnits
    (
        int16_t *count,
        int8_t  *serials,
        int16_t *serialLth
    ); """
ps4000a.make_symbol("_enumerate_units", "ps4000aEnumerateUnits", c_uint32, [c_void_p, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetChannelInformation
    (
        int16_t               handle,
        PS4000A_CHANNEL_INFO  info,
        int32_t               probe,
        int32_t              *ranges,
        int32_t              *length,
        int32_t               channels
    ); """
ps4000a.make_symbol("_get_channel_information", "ps4000aGetChannelInformation", c_uint32,
                    [c_int16, c_int32, c_int32, c_void_p, c_void_p, c_int32], doc)

doc = """ PICO_STATUS ps4000aConnectDetect
    (
        int16_t                 handle,
        PS4000A_CONNECT_DETECT *sensor,
        int16_t                 nSensors
    ); """
ps4000a.make_symbol("_connect_detect", "ps4000aConnectDetect", c_uint32, [c_int16, c_void_p, c_int16], doc)

doc = """ PICO_STATUS ps4000aMaximumValue
    (
        int16_t  handle,
        int16_t *value
    ); """
ps4000a.make_symbol("_maximum_value", "ps4000aMaximumValue", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aMinimumValue
    (
        int16_t		handle,
        int16_t * value
    ); """
ps4000a.make_symbol("_minimum_value", "ps4000aMinimumValue", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetAnalogueOffset
    (
        int16_t           handle,
        PS4000A_RANGE     range,
        PS4000A_COUPLING  coupling,
        float            *maximumVoltage,
        float            *minimumVoltage
    ); """
ps4000a.make_symbol("_get_analogue_offset", "ps4000aGetAnalogueOffset", c_uint32,
                    [c_int16, c_int32, c_int32, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetMaxSegments
    (
        int16_t   handle,
        uint32_t *maxSegments
    ); """
ps4000a.make_symbol("_get_max_segments", "ps4000aGetMaxSegments", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aChangePowerSource
    (
        int16_t      handle,
        PICO_STATUS  powerState
    ); """
ps4000a.make_symbol("_change_power_source", "ps4000aChangePowerSource", c_uint32, [c_int16, c_uint32], doc)

doc = """ PICO_STATUS ps4000aCurrentPowerSource
    (
        int16_t  handle
    ); """
ps4000a.make_symbol("_current_power_source", "ps4000aCurrentPowerSource", c_uint32, [c_int16, ], doc)

doc = """ PICO_STATUS ps4000aStop
    (
        int16_t  handle
    ); """
ps4000a.make_symbol("_stop", "ps4000aStop", c_uint32, [c_int16, ], doc)

doc = """ PICO_STATUS ps4000aPingUnit
    (
        int16_t  handle
    ); """
ps4000a.make_symbol("_ping_unit", "ps4000aPingUnit", c_uint32, [c_int16, ], doc)

doc = """ PICO_STATUS ps4000aSetNoOfCaptures
    (
        int16_t   handle,
        uint32_t  nCaptures
    ); """
ps4000a.make_symbol("_set_no_of_captures", "ps4000aSetNoOfCaptures", c_uint32, [c_int16, c_uint32], doc)

doc = """ PICO_STATUS ps4000aGetNoOfCaptures
    (
        int16_t   handle,
        uint32_t *nCaptures
    ); """
ps4000a.make_symbol("_get_no_of_captures", "ps4000aGetNoOfCaptures", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetNoOfProcessedCaptures
    (
        int16_t   handle,
        uint32_t *nProcessedCaptures
    ); """
ps4000a.make_symbol("_get_no_of_processed_captures", "ps4000aGetNoOfProcessedCaptures", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aDeviceMetaData
    (
        int16_t                 handle,
        int8_t                 *settings,
        int32_t                *nSettingsLength,
        PS4000A_META_TYPE       type,
        PS4000A_META_OPERATION  operation,
        PS4000A_META_FORMAT     format
    ); """
ps4000a.make_symbol("_device_meta_data", "ps4000aDeviceMetaData", c_uint32,
                    [c_int16, c_void_p, c_void_p, c_int32, c_int32, c_int32], doc)

doc = """ PICO_STATUS ps4000aGetString
    (
        int16_t            handle,
        PICO_STRING_VALUE  stringValue,
        int8_t            *string,
        int32_t           *stringLength
    ); """
ps4000a.make_symbol("_get_string", "ps4000aGetString", c_uint32, [c_int16, c_int32, c_void_p, c_void_p], doc)

doc = """ PICO_STATUS ps4000aGetCommonModeOverflow
    (
        int16_t   handle,
        uint16_t *overflow
    ); """
ps4000a.make_symbol("_get_common_mode_overflow", "ps4000aGetCommonModeOverflow", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSetFrequencyCounter
    (
        int16_t                          handle,
        PS4000A_CHANNEL                  channel,
        int16_t                          enabled,
        PS4000A_FREQUENCY_COUNTER_RANGE  range,
        int16_t                          thresholdMajor,
        int16_t                          thresholdMinor
    ); """
ps4000a.make_symbol("_set_frequency_counter", "ps4000aSetFrequencyCounter", c_uint32,
                    [c_int16, c_int32, c_int16, c_int32, c_int16, c_int16], doc)

doc = """ PICO_STATUS ps4000aOpenUnitWithResolution
    (
	    int16_t    *handle,
		int8_t     *serial,
		PS4000A_DEVICE_RESOLUTION    resolution
	); """
ps4000a.make_symbol("_open_unit_with_resolution", "ps4000aOpenUnitWithResolution", c_uint32, [c_void_p, c_void_p, c_int32], doc)

doc = """ PICO_STATUS ps4000aGetDeviceResolution
    (
	    int16_t    handle,
		PS4000A_DEVICE_RESOLUTION    *resolution
	); """
ps4000a.make_symbol("_get_resolution", "ps4000aGetDeviceResolution", c_uint32, [c_int16, c_void_p], doc)

doc = """ PICO_STATUS ps4000aSetDeviceResolution
    (
	    int16_t    handle,
		PS4000A_DEVICE_RESOLUTION    resolution
	); """
ps4000a.make_symbol("_set_resolution", "ps4000aSetDeviceResolution", c_uint32, [c_int16, c_int32], doc)

doc = """ PICO_STATUS ps4000aSetProbeInteractionCallback
    (
	    int16_t    handle,
		ps4000aProbeInteractions callback
	); """
ps4000a.make_symbol("_set_probe_interaction_callback", "ps4000aSetProbeInteractionCallback", c_uint32, [c_int16, c_void_p], doc)

doc = """ void *ps4000aProbeInteractions
    (
		int16_t    												handle,
		PICO_STATUS												status,
		PS4000A_USER_PROBE_INTERACTIONS * probes,
		uint32_t													nProbes
    );
    define a python function which accepts the correct arguments, and pass it to the constructor of this type.
    """

ps4000a.ps4000aProbeInteractions = C_CALLBACK_FUNCTION_FACTORY(None,
                                                         c_int16,
                                                        c_uint32,
                                                        POINTER(PS4000A_USER_PROBE_INTERACTIONS),
                                                        c_uint32
                                                        )

ps4000a.ps4000aProbeInteractions.__doc__ = doc
