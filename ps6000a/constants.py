"""PicoScope API enumerations, flags, and constants."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: constants.py
#
# PicoScope API enumerations, flags, and constants.
#
# Portions Copyright 2018-2019 Pico Technology Ltd. (ISC Licensed)
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Created                                        jrowley
#   20240322       Added new error codes                          aanderson
#
###############################################################################

# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
# We need _SimpleCData for typing to work right. API stability unknown.
from ctypes import _SimpleCData, c_int8, c_int16, c_int32, c_int64, c_uint32
from typing import Optional, Type, cast

import numpy as np

from ps6000a.util import FlexIntEnum, FlexIntFlag


class PicoRatioMode(FlexIntFlag):
	"""
	Downsampling mode.

	Various methods of data reduction, or downsampling, are possible with the
	PicoScope 6000E Series oscilloscopes. The downsampling is done at high speed
	by dedicated hardware inside the scope, making your application faster and
	more responsive than if you had to do all the data processing in software.

	You specify the downsampling mode when you call one of the data collection
	functions, such as ``get_values``. The following modes are available:

	:cvar AGGREGATE: Reduces every block of n values to just two values: a
		minimum and a maximum. The minimum and maximum values are returned in
		two separate buffers.
	:cvar AVERAGE: Reduces every block of n values to a single value
		representing the average (arithmetic mean) of all the values.
	:cvar DECIMATE: Reduces every block of n values to just the first value in
		the block, discarding all the other values.
	:cvar DISTRIBUTION: Not implemented.
	:cvar TRIGGER: Gets 20 samples either side of the trigger point.
	:cvar RAW: No downsampling. Returns raw data values.

	No documentation is provided for the other values. They may not be
	applicable to this model of oscilloscope.
	"""

	AGGREGATE = 0x00000001
	DECIMATE = 0x00000002
	AVERAGE = 0x00000004
	DISTRIBUTION = 0x00000008
	SUM = 0x00000010
	TRIGGER_DATA_FOR_TIME_CALCULATION = 0x10000000
	SEGMENT_HEADER = 0x20000000
	TRIGGER = 0x40000000
	RAW = 0x80000000


class PicoChannel(FlexIntEnum):
	"""An oscilloscope channel, either analog or digital."""

	CHANNEL_A = 0x00
	CHANNEL_B = 0x01
	CHANNEL_C = 0x02
	CHANNEL_D = 0x03
	CHANNEL_E = 0x04
	CHANNEL_F = 0x05
	CHANNEL_G = 0x06
	CHANNEL_H = 0x07
	PORT0 = 0x80
	PORT1 = 0x81
	PORT2 = 0x82
	PORT3 = 0x83
	EXTERNAL = 0x3E8
	TRIGGER_AUX = 0x3E9
	PULSE_WIDTH_SOURCE = 0x10000000
	DIGITAL_SOURCE = 0x10000001

	@property
	def flag(self) -> "PicoChannelFlags":
		"""Get the corresponding flag for this channel."""
		if self.CHANNEL_A <= self <= self.CHANNEL_H:
			out = PicoChannelFlags.CHANNEL_A << (self - self.CHANNEL_A)
		elif self.PORT0 <= self <= self.PORT3:
			out = PicoChannelFlags.PORT0 << (self - self.PORT0)
		else:
			out = 0
		return PicoChannelFlags(out)


class PicoChannelFlags(FlexIntFlag):
	"""A bit field indicating a combination of channels."""

	CHANNEL_A = 0x00000001
	CHANNEL_B = 0x00000002
	CHANNEL_C = 0x00000004
	CHANNEL_D = 0x00000008
	CHANNEL_E = 0x00000010
	CHANNEL_F = 0x00000020
	CHANNEL_G = 0x00000040
	CHANNEL_H = 0x00000080
	PORT0 = 0x00010000
	PORT1 = 0x00020000
	PORT2 = 0x00040000
	PORT3 = 0x00080000


class PicoPortDigitalChannel(FlexIntEnum):
	"""A channel/pin within a digital port."""

	CHANNEL0 = 0
	CHANNEL1 = 1
	CHANNEL2 = 2
	CHANNEL3 = 3
	CHANNEL4 = 4
	CHANNEL5 = 5
	CHANNEL6 = 6
	CHANNEL7 = 7


class PicoDataType(FlexIntEnum):
	"""Unified data type specifier."""

	INT8_T = 0
	INT16_T = 1
	INT32_T = 2
	UINT32_T = 3
	INT64_T = 4

	_np_types: dict["PicoDataType", type]
	_ctypes: dict["PicoDataType", Type[_SimpleCData]]
	_type_min: dict["PicoDataType", int]
	_type_max: dict["PicoDataType", int]

	@property
	def numpy_type(self) -> type:
		"""
		Get appropriate numpy datatype for this PicoDataType.

		:return: Appropriate numpy datatype for this PicoDataType.
		:rtype: type (should be numpy dtype)
		:raises ValueError: Will raise if no dtype is known for this value.
		"""
		if self in self._np_types:
			return self._np_types[self]
		else:
			raise ValueError(f"No known datatype for PicoDataType {self}")

	@property
	def ctype(self) -> Type[_SimpleCData]:
		"""
		Get appropriate ctypes datatype for this PicoDataType.

		:return: Appropriate ctypes datatype for this PicoDataType.
		:rtype: _SimpleCData
		:raises ValueError: Will raise if no ctype is known for this value.
		"""
		if self in self._ctypes:
			return self._ctypes[self]
		else:
			raise ValueError(f"No known ctype for PicoDataType {self}")

	@property
	def min(self) -> int:
		"""
		Get the minimum value of this PicoDataType.

		:return: The minimum value of this PicoDataType.
		:rtype: int
		:raises ValueError: Will raise if the information is not available.
		"""
		if self in self._type_min:
			return self._type_min[self]
		else:
			raise ValueError(f"No information available for PicoDataType {self}")

	@property
	def max(self) -> int:
		"""
		Get the maximum value of this PicoDataType.

		:return: The maximum value of this PicoDataType.
		:rtype: int
		:raises ValueError: Will raise if the information is not available.
		"""
		if self in self._type_max:
			return self._type_max[self]
		else:
			raise ValueError(f"No information available for PicoDataType {self}")


PicoDataType._np_types = {
	PicoDataType.INT8_T: np.int8,
	PicoDataType.INT16_T: np.int16,
	PicoDataType.INT32_T: np.int32,
	PicoDataType.UINT32_T: np.uint32,
	PicoDataType.INT64_T: np.int64,
}

PicoDataType._ctypes = {
	PicoDataType.INT8_T: c_int8,
	PicoDataType.INT16_T: c_int16,
	PicoDataType.INT32_T: c_int32,
	PicoDataType.UINT32_T: c_uint32,
	PicoDataType.INT64_T: c_int64,
}

PicoDataType._type_min = {
	PicoDataType.INT8_T: -0x80,
	PicoDataType.INT16_T: -0x8000,
	PicoDataType.INT32_T: -0x80000000,
	PicoDataType.UINT32_T: 0x0,
	PicoDataType.INT64_T: -0x8000000000000000,
}

PicoDataType._type_max = {
	PicoDataType.INT8_T: 0x7F,
	PicoDataType.INT16_T: 0x7FFF,
	PicoDataType.INT32_T: 0x7FFFFFFF,
	PicoDataType.UINT32_T: 0xFFFFFFFF,
	PicoDataType.INT64_T: 0x7FFFFFFFFFFFFFFF,
}


class PicoCoupling(FlexIntEnum):
	"""
	The impedance and coupling type.

	:cvar AC: 1 MΩ impedance, AC coupling. The channel accepts input frequencies
		from about 1 hertz up to its maximum -3 dB analog bandwidth.
	:cvar DC: 1 MΩ impedance, DC coupling. The scope accepts all input
		frequencies from zero (DC) up to its maximum -3 dB analog bandwidth.
	:cvar DC_50OHM: 50 Ω impedance, DC coupling. The higher-voltage input ranges
		may not be available in this mode - consult data sheet.
	"""

	AC = 0
	DC = 1
	DC_50OHM = 50


class PicoBandwidthLimiter(FlexIntEnum):
	"""The bandwidth limiter setting."""

	BW_FULL = 0
	BW_100KHZ = 100000
	BW_20KHZ = 20000
	BW_1MHZ = 1000000
	BW_20MHZ = 20000000
	BW_25MHZ = 25000000
	BW_50MHZ = 50000000
	BW_250MHZ = 250000000
	BW_500MHZ = 500000000


class PicoPulseWidthType(FlexIntEnum):
	"""
	The pulse width qualifier type.

	:cvar NONE: No pulse width qualifier required.
	:cvar LESS_THAN: Pulse width must be less than threshold.
	:cvar GREATER_THAN: Pulse width must be greater than threshold.
	:cvar IN_RANGE: Pulse width must be between two thresholds.
	:cvar OUT_OF_RANGE: Pulse width must not be between two thresholds.
	"""

	NONE = 0
	LESS_THAN = 1
	GREATER_THAN = 2
	IN_RANGE = 3
	OUT_OF_RANGE = 4


class PicoSweepType(FlexIntEnum):
	"""
	The direction of the sweep.

	:cvar UP: To sweep from the start frequency up to the stop frequency and
		then repeat.
	:cvar DOWN: To sweep from the start frequency down to the stop frequency and
		then repeat.
	:cvar UPDOWN: To sweep from the start frequency up to the stop frequency,
		then down to the start frequency, and then repeat.
	:cvar DOWNUP: To sweep from the start frequency down to the stop frequency,
		then up to the start frequency, and then repeat.
	"""

	UP = 0
	DOWN = 1
	UPDOWN = 2
	DOWNUP = 3


class PicoWaveType(FlexIntEnum):
	"""Specifies the type of waveform to generate."""

	SINE = 0x00000011
	SQUARE = 0x00000012
	TRIANGLE = 0x00000013
	RAMP_UP = 0x00000014
	RAMP_DOWN = 0x00000015
	SINC = 0x00000016
	GAUSSIAN = 0x00000017
	HALF_SINE = 0x00000018
	DC_VOLTAGE = 0x00000400
	PWM = 0x00001000
	WHITENOISE = 0x00002001
	PRBS = 0x00002002
	ARBITRARY = 0x10000000


class PicoSigGenTrigType(FlexIntEnum):
	"""
	The type of trigger for the signal generator.

	Either an edge trigger (starts on a specified edge) or a gated trigger
	(runs while trigger is in the specified state).
	"""

	RISING = 0
	FALLING = 1
	GATE_HIGH = 2
	GATE_LOW = 3


class PicoSigGenTrigSource(FlexIntEnum):
	"""The signal used as a trigger."""

	NONE = 0
	SCOPE_TRIG = 1
	AUX_IN = 2
	EXT_IN = 3
	SOFT_TRIG = 4
	TRIGGER_RAW = 5


class PicoSigGenFilterState(FlexIntEnum):
	"""The state of the signal generator output filter."""

	AUTO = 0
	OFF = 1
	ON = 2


class PicoSigGenParameter(FlexIntEnum):
	"""
	Specifies a signal generator parameter.

	:cvar OUTPUT_VOLTS: The signal generator output voltage.
	:cvar SAMPLE: The value of a sample in the arbitrary waveform buffer.
	:cvar BUFFER_LENGTH: The length of the arbitrary waveform buffer, in
		samples.
	"""

	OUTPUT_VOLTS = 0
	SAMPLE = 1
	BUFFER_LENGTH = 2


class PicoTimeUnits(FlexIntEnum):
	"""Unit of time."""

	FS = 0
	PS = 1
	NS = 2
	US = 3
	MS = 4
	S = 5

	_scale_factors: dict["PicoTimeUnits", float]

	@property
	def scale_factor(self) -> float:
		"""
		Get scaling factor this PicoTimeUnits member, with respect to seconds.

		Multiplying a raw time value by the corresponding factor will give a
		result in seconds.

		:return: Scaling factor for this PicoTimeUnits member.
		:rtype: float
		:raises ValueError: Will raise if no scale is known for this value.
		"""
		if self in self._scale_factors:
			return self._scale_factors[self]
		else:
			raise ValueError(f"No known scale for PicoTimeUnits {self}")


PicoTimeUnits._scale_factors = {
	PicoTimeUnits.FS: 1000000000000000.0,
	PicoTimeUnits.PS: 1000000000000.0,
	PicoTimeUnits.NS: 1000000000.0,
	PicoTimeUnits.US: 1000000.0,
	PicoTimeUnits.MS: 1000.0,
	PicoTimeUnits.S: 1.0,
}


class PicoThresholdDirection(FlexIntEnum):
	"""
	The direction in which the signal must move to cause a trigger.

	When used with ``PicoThresholdMode.LEVEL``:

	:cvar ABOVE: Gated trigger, upper threshold used. Active when signal above
		threshold.
	:cvar ABOVE_LOWER: Gated trigger, lower threshold used. Active when signal
		above threshold.
	:cvar BELOW: Gated trigger, upper threshold used. Active when signal below
		threshold.
	:cvar ABOVE_LOWER: Gated trigger, lower threshold used. Active when signal
		below threshold.
	:cvar RISING: Threshold trigger, upper threshold used. Active when signal
		rises above threshold.
	:cvar RISING_LOWER: Threshold trigger, lower threshold used. Active when
		signal rises above threshold.
	:cvar FALLING: Threshold trigger, upper threshold used. Active when signal
		falls below threshold.
	:cvar FALLING_LOWER: Threshold trigger, lower threshold used. Active when
		signal falls below threshold.
	:cvar RISING_OR_FALLING: Threshold trigger, both threshold useds. Active
		when signal rises above lower threshold or falls below upper threshold.

	When used with ``PicoThresholdMode.WINDOW``:

	:cvar INSIDE: Window-qualified trigger. Active when signal is between
		thresholds.
	:cvar OUTSIDE: Window-qualified trigger. Active when signal is not between
		thresholds.
	:cvar ENTER: Window trigger. Active when signal enters region between
		thresholds.
	:cvar EXIT: Window trigger. Active when signal exits region between
		thresholds.
	:cvar ENTER_OR_EXIT: Window trigger. Active when signal enters or exits
		region between thresholds.
	:cvar POSITIVE_RUNT: Window-qualified trigger. Active when signal enters
		region between thresholds from below.
	:cvar NEGATIVE_RUNT: Window-qualified trigger. Active when signal enters
		region between thresholds from above.

	Miscellaneous:

	:cvar LOGIC_LOWER: Logic trigger. Lower threshold used.
	:cvar LOGIC_UPPER: Logic trigger. Upper threshold used.
	:cvar NONE: No trigger.
	"""

	ABOVE = INSIDE = 0
	BELOW = OUTSIDE = 1
	RISING = ENTER = NONE = 2
	FALLING = EXIT = 3
	RISING_OR_FALLING = ENTER_OR_EXIT = 4
	ABOVE_LOWER = 5
	BELOW_LOWER = 6
	RISING_LOWER = 7
	FALLING_LOWER = 8
	POSITIVE_RUNT = 9
	NEGATIVE_RUNT = 10
	LOGIC_LOWER = 1000
	LOGIC_UPPER = 1001


class PicoThresholdMode(FlexIntEnum):
	"""
	The type of threshold for triggering.

	:cvar LEVEL: Active when input is above or below a single threshold.
	:cvar WINDOW: Active when input is between two thresholds.
	"""

	LEVEL = 0
	WINDOW = 1


class PicoAction(FlexIntFlag):
	"""How to handle existing items when registering a new item."""

	CLEAR_ALL = 0x00000001
	ADD = 0x00000002

	# Unclear what these ones do. Possibly unimplemented.
	CLEAR_THIS_DATA_BUFFER = 0x00001000
	CLEAR_WAVEFORM_DATA_BUFFERS = 0x00002000
	CLEAR_WAVEFORM_READ_DATA_BUFFERS = 0x00004000


class PicoTriggerState(FlexIntEnum):
	"""The required state of a condition to activate the trigger."""

	DONT_CARE = 0
	TRUE = 1
	FALSE = 2

	@property
	def as_bool(self) -> Optional[bool]:
		"""
		Convert this PicoTriggerState value to a boolean value or None.

		:return: This value as True, False, or None.
		:rtype: Optional[bool]
		"""
		if self == self.TRUE:
			return True
		elif self == self.FALSE:
			return False
		else:
			return None

	@classmethod
	def from_bool(cls, value: Optional[bool]) -> "PicoTriggerState":
		"""
		Convert a boolean (or None) value to a PicoTriggerState.

		:param value: The value to convert.
		:type value: Optional[bool]
		:return: Matching PicoTriggerState.
		:rtype: PicoTriggerState
		"""
		if value is None:
			return cls.DONT_CARE
		elif value:
			return cls.TRUE
		else:
			return cls.FALSE


class PicoDeviceResolution(FlexIntEnum):
	"""The vertical resolution of the oscilloscope (all channels)."""

	DR_8BIT = 0
	DR_12BIT = 1
	DR_14BIT = 2
	DR_15BIT = 3
	DR_16BIT = 4
	DR_10BIT = 10

	_bits_lookup: dict["PicoDeviceResolution", int]
	_type_lookup: dict["PicoDeviceResolution", PicoDataType]

	@property
	def bits(self) -> int:
		"""
		Get number of bits for this PicoDeviceResolution member.

		:return: Number of bits for this PicoDeviceResolution member.
		:rtype: int
		:raises ValueError: Will raise if no bit depth is known for this value.
		"""
		if self in self._bits_lookup:
			return self._bits_lookup[self]
		else:
			raise ValueError(f"No known bits for PicoDeviceResolution {self}")

	@classmethod
	def from_bits(cls, bits: int) -> "PicoDeviceResolution":
		"""
		Get appropriate enum member for given number of bits.

		:param bits: The desired bit depth.
		:type bits: int
		:return: Appropriate PicoDeviceResolution for given number of bits.
		:rtype: PicoDeviceResolution
		"""
		bits_lookup = cast(dict["PicoDeviceResolution", int], cls._bits_lookup)
		for member, value in bits_lookup.items():
			if value == bits:
				return member
		raise ValueError(f"No matching PicoDeviceResolution for {bits} bits")

	@property
	def min_type(self) -> PicoDataType:
		"""
		Get the smallest PicoDataType for this PicoDeviceResolution.

		:return: The smallest PicoDataType for this PicoDeviceResolution.
		:rtype: int
		:raises ValueError: Will raise if the information is not available.
		"""
		if self in self._type_lookup:
			return self._type_lookup[self]
		else:
			raise ValueError(f"No PicoDataType known for PicoDeviceResolution {self}")


PicoDeviceResolution._bits_lookup = {
	PicoDeviceResolution.DR_8BIT: 8,
	PicoDeviceResolution.DR_12BIT: 12,
	PicoDeviceResolution.DR_14BIT: 14,
	PicoDeviceResolution.DR_15BIT: 15,
	PicoDeviceResolution.DR_16BIT: 16,
	PicoDeviceResolution.DR_10BIT: 10,
}


PicoDeviceResolution._type_lookup = {
	PicoDeviceResolution.DR_8BIT: PicoDataType.INT8_T,
	PicoDeviceResolution.DR_12BIT: PicoDataType.INT16_T,
	PicoDeviceResolution.DR_14BIT: PicoDataType.INT16_T,
	PicoDeviceResolution.DR_15BIT: PicoDataType.INT16_T,
	PicoDeviceResolution.DR_16BIT: PicoDataType.INT16_T,
	PicoDeviceResolution.DR_10BIT: PicoDataType.INT16_T,
}


class PicoReadSelection(FlexIntEnum):
	"""
	No documentation available.

	It is an argument to the PicoDataReadyUsingReads callback.
	"""

	NONE = 0
	TRIGGER_READ = 1
	DATA_READ1 = 2
	DATA_READ2 = 3
	DATA_READ3 = 4


class PicoDigitalPortHysteresis(FlexIntEnum):
	"""The hysteresis to apply to all channels in a digital port."""

	VERY_HIGH_400MV = 0
	HIGH_200MV = 1
	NORMAL_100MV = 2
	LOW_50MV = 3


class PicoDigitalDirection(FlexIntEnum):
	"""
	Digital trigger direction.

	:cvar DONT_CARE: Channel has no effect on trigger.
	:cvar LOW: Channel must be low to trigger.
	:cvar HIGH: Channel must be high to trigger.
	:cvar RISING: Channel must transition from low to high to trigger.
	:cvar FALLING: Channel must transition from high to low to trigger.
	:cvar RISING_OR_FALLING: Any transition on channel causes a trigger.
	:cvar MAX_DIRECTION: Not documented.
	"""

	DONT_CARE = 0
	LOW = 1
	HIGH = 2
	RISING = 3
	FALLING = 4
	RISING_OR_FALLING = 5
	MAX_DIRECTION = 6


class PicoClockReference(FlexIntEnum):
	"""
	No documentation available.

	It is an argument to the PicoExternalReferenceInteractions callback.
	"""

	INTERNAL_REF = 0
	EXTERNAL_REF = 1


class PicoTriggerWithinPreTrigger(FlexIntEnum):
	"""State of "trigger within pretrigger" feature."""

	DISABLE = 0
	ARM = 1


class PicoTemperatureReference(FlexIntEnum):
	"""
	No documentation available.

	It is an argument to the PicoTemperatureSensorInteractions callback.
	"""

	UNINITIALIZED = 0
	NORMAL = 1
	WARNING = 2
	CRITICAL = 3
	REFERENCE = 4


class PicoDigitalPort(FlexIntEnum):
	"""The device attached to a digital port."""

	NONE = 0
	MSO_POD = 1000
	UNKNOWN_DEVICE = -2


class PicoStatus(FlexIntEnum):
	"""The status code returned by every API function."""

	NOT_YET_RUN = -1
	OK = 0x00000000
	MAX_UNITS_OPENED = 0x00000001
	MEMORY_FAIL = 0x00000002
	NOT_FOUND = 0x00000003
	FW_FAIL = 0x00000004
	OPEN_OPERATION_IN_PROGRESS = 0x00000005
	OPERATION_FAILED = 0x00000006
	NOT_RESPONDING = 0x00000007
	CONFIG_FAIL = 0x00000008
	KERNEL_DRIVER_TOO_OLD = 0x00000009
	EEPROM_CORRUPT = 0x0000000A
	OS_NOT_SUPPORTED = 0x0000000B
	INVALID_HANDLE = 0x0000000C
	INVALID_PARAMETER = 0x0000000D
	INVALID_TIMEBASE = 0x0000000E
	INVALID_VOLTAGE_RANGE = 0x0000000F
	INVALID_CHANNEL = 0x00000010
	INVALID_TRIGGER_CHANNEL = 0x00000011
	INVALID_CONDITION_CHANNEL = 0x00000012
	NO_SIGNAL_GENERATOR = 0x00000013
	STREAMING_FAILED = 0x00000014
	BLOCK_MODE_FAILED = 0x00000015
	NULL_PARAMETER = 0x00000016
	ETS_MODE_SET = 0x00000017
	DATA_NOT_AVAILABLE = 0x00000018
	STRING_BUFFER_TO_SMALL = 0x00000019
	ETS_NOT_SUPPORTED = 0x0000001A
	AUTO_TRIGGER_TIME_TO_SHORT = 0x0000001B
	BUFFER_STALL = 0x0000001C
	TOO_MANY_SAMPLES = 0x0000001D
	TOO_MANY_SEGMENTS = 0x0000001E
	PULSE_WIDTH_QUALIFIER = 0x0000001F
	DELAY = 0x00000020
	SOURCE_DETAILS = 0x00000021
	CONDITIONS = 0x00000022
	USER_CALLBACK = 0x00000023
	DEVICE_SAMPLING = 0x00000024
	NO_SAMPLES_AVAILABLE = 0x00000025
	SEGMENT_OUT_OF_RANGE = 0x00000026
	BUSY = 0x00000027
	STARTINDEX_INVALID = 0x00000028
	INVALID_INFO = 0x00000029
	INFO_UNAVAILABLE = 0x0000002A
	INVALID_SAMPLE_INTERVAL = 0x0000002B
	TRIGGER_ERROR = 0x0000002C
	MEMORY = 0x0000002D
	SIG_GEN_PARAM = 0x0000002E
	SHOTS_SWEEPS_WARNING = 0x0000002F
	SIGGEN_TRIGGER_SOURCE = 0x00000030
	AUX_OUTPUT_CONFLICT = 0x00000031
	AUX_OUTPUT_ETS_CONFLICT = 0x00000032
	WARNING_EXT_THRESHOLD_CONFLICT = 0x00000033
	WARNING_AUX_OUTPUT_CONFLICT = 0x00000034
	SIGGEN_OUTPUT_OVER_VOLTAGE = 0x00000035
	DELAY_NULL = 0x00000036
	INVALID_BUFFER = 0x00000037
	SIGGEN_OFFSET_VOLTAGE = 0x00000038
	SIGGEN_PK_TO_PK = 0x00000039
	CANCELLED = 0x0000003A
	SEGMENT_NOT_USED = 0x0000003B
	INVALID_CALL = 0x0000003C
	GET_VALUES_INTERRUPTED = 0x0000003D
	NOT_USED = 0x0000003F
	INVALID_SAMPLERATIO = 0x00000040
	INVALID_STATE = 0x00000041
	NOT_ENOUGH_SEGMENTS = 0x00000042
	DRIVER_FUNCTION = 0x00000043
	RESERVED = 0x00000044
	INVALID_COUPLING = 0x00000045
	BUFFERS_NOT_SET = 0x00000046
	RATIO_MODE_NOT_SUPPORTED = 0x00000047
	RAPID_NOT_SUPPORT_AGGREGATION = 0x00000048
	INVALID_TRIGGER_PROPERTY = 0x00000049
	INTERFACE_NOT_CONNECTED = 0x0000004A
	RESISTANCE_AND_PROBE_NOT_ALLOWED = 0x0000004B
	POWER_FAILED = 0x0000004C
	SIGGEN_WAVEFORM_SETUP_FAILED = 0x0000004D
	FPGA_FAIL = 0x0000004E
	POWER_MANAGER = 0x0000004F
	INVALID_ANALOGUE_OFFSET = 0x00000050
	PLL_LOCK_FAILED = 0x00000051
	ANALOG_BOARD = 0x00000052
	CONFIG_FAIL_AWG = 0x00000053
	INITIALISE_FPGA = 0x00000054
	EXTERNAL_FREQUENCY_INVALID = 0x00000056
	CLOCK_CHANGE_ERROR = 0x00000057
	TRIGGER_AND_EXTERNAL_CLOCK_CLASH = 0x0000005
	PWQ_AND_EXTERNAL_CLOCK_CLASH = 0x00000059
	UNABLE_TO_OPEN_SCALING_FILE = 0x0000005A
	MEMORY_CLOCK_FREQUENCY = 0x0000005B
	I2C_NOT_RESPONDING = 0x0000005C
	NO_CAPTURES_AVAILABLE = 0x0000005D
	NOT_USED_IN_THIS_CAPTURE_MODE = 0x0000005E
	TOO_MANY_TRIGGER_CHANNELS_IN_USE = 0x0000005F
	INVALID_TRIGGER_DIRECTION = 0x00000060
	INVALID_TRIGGER_STATES = 0x00000061
	GET_DATA_ACTIVE = 0x00000103
	IP_NETWORKED = 0x00000104
	INVALID_IP_ADDRESS = 0x00000105
	IPSOCKET_FAILED = 0x00000106
	IPSOCKET_TIMEDOUT = 0x00000107
	SETTINGS_FAILED = 0x00000108
	NETWORK_FAILED = 0x00000109
	WS2_32_DLL_NOT_LOADED = 0x0000010A
	INVALID_IP_PORT = 0x0000010B
	COUPLING_NOT_SUPPORTED = 0x0000010C
	BANDWIDTH_NOT_SUPPORTED = 0x0000010D
	INVALID_BANDWIDTH = 0x0000010E
	AWG_NOT_SUPPORTED = 0x0000010F
	ETS_NOT_RUNNING = 0x00000110
	SIG_GEN_WHITENOISE_NOT_SUPPORTED = 0x00000111
	SIG_GEN_WAVETYPE_NOT_SUPPORTED = 0x00000112
	INVALID_DIGITAL_PORT = 0x00000113
	INVALID_DIGITAL_CHANNEL = 0x00000114
	INVALID_DIGITAL_TRIGGER_DIRECTION = 0x00000115
	SIG_GEN_PRBS_NOT_SUPPORTED = 0x00000116
	ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS = 0x00000117
	WARNING_REPEAT_VALUE = 0x00000118
	POWER_SUPPLY_CONNECTED = 0x00000119
	POWER_SUPPLY_NOT_CONNECTED = 0x0000011A
	POWER_SUPPLY_REQUEST_INVALID = 0x0000011B
	POWER_SUPPLY_UNDERVOLTAGE = 0x0000011C
	CAPTURING_DATA = 0x0000011D
	USB3_0_DEVICE_NON_USB3_0_PORT = 0x0000011E
	NOT_SUPPORTED_BY_THIS_DEVICE = 0x0000011F
	INVALID_DEVICE_RESOLUTION = 0x00000120
	INVALID_NUMBER_CHANNELS_FOR_RESOLUTION = 0x00000121
	CHANNEL_DISABLED_DUE_TO_USB_POWERED = 0x00000122
	SIGGEN_DC_VOLTAGE_NOT_CONFIGURABLE = 0x00000123
	NO_TRIGGER_ENABLED_FOR_TRIGGER_IN_PRE_TRIG = 0x00000124
	TRIGGER_WITHIN_PRE_TRIG_NOT_ARMED = 0x00000125
	TRIGGER_WITHIN_PRE_NOT_ALLOWED_WITH_DELAY = 0x00000126
	TRIGGER_INDEX_UNAVAILABLE = 0x00000127
	AWG_CLOCK_FREQUENCY = 0x00000128
	TOO_MANY_CHANNELS_IN_USE = 0x00000129
	NULL_CONDITIONS = 0x0000012A
	DUPLICATE_CONDITION_SOURCE = 0x0000012B
	INVALID_CONDITION_INFO = 0x0000012C
	SETTINGS_READ_FAILED = 0x0000012D
	SETTINGS_WRITE_FAILED = 0x0000012E
	ARGUMENT_OUT_OF_RANGE = 0x0000012F
	HARDWARE_VERSION_NOT_SUPPORTED = 0x00000130
	DIGITAL_HARDWARE_VERSION_NOT_SUPPORTED = 0x00000131
	ANALOGUE_HARDWARE_VERSION_NOT_SUPPORTED = 0x00000132
	UNABLE_TO_CONVERT_TO_RESISTANCE = 0x00000133
	DUPLICATED_CHANNEL = 0x00000134
	INVALID_RESISTANCE_CONVERSION = 0x00000135
	INVALID_VALUE_IN_MAX_BUFFER = 0x00000136
	INVALID_VALUE_IN_MIN_BUFFER = 0x00000137
	SIGGEN_FREQUENCY_OUT_OF_RANGE = 0x00000138
	EEPROM2_CORRUPT = 0x00000139
	EEPROM2_FAIL = 0x0000013A
	SERIAL_BUFFER_TOO_SMALL = 0x0000013B
	SIGGEN_TRIGGER_AND_EXTERNAL_CLOCK_CLASH = 0x0000013C
	WARNING_SIGGEN_AUXIO_TRIGGER_DISABLED = 0x0000013D
	SIGGEN_GATING_AUXIO_NOT_AVAILABLE = 0x00000013E
	SIGGEN_GATING_AUXIO_ENABLED = 0x00000013F
	RESOURCE_ERROR = 0x00000140
	TEMPERATURE_TYPE_INVALID = 0x00000141
	TEMPERATURE_TYPE_NOT_SUPPORTED = 0x00000142
	TIMEOUT = 0x00000143
	DEVICE_NOT_FUNCTIONING = 0x00000144
	INTERNAL_ERROR = 0x00000145
	MULTIPLE_DEVICES_FOUND = 0x00000146
	WARNING_NUMBER_OF_SEGMENTS_REDUCED = 0x00000147
	CAL_PINS_STATES = 0x00000148
	CAL_PINS_FREQUENCY = 0x00000149
	CAL_PINS_AMPLITUDE = 0x0000014A
	CAL_PINS_WAVETYPE = 0x0000014B
	CAL_PINS_OFFSET = 0x0000014C
	PROBE_FAULT = 0x0000014D
	PROBE_IDENTITY_UNKNOWN = 0x0000014E
	PROBE_POWER_DC_POWER_SUPPLE_REQUIRED = 0x0000014F
	PROBE_NOT_POWERED_THROUGH_DC_POWER_SUPPLY = 0x00000150
	PROBE_CONFIG_FAILURE = 0x00000151
	PROBE_INTERACTION_CALLBACK = 0x00000152
	UNKNOWN_INTELLIGENT_PROBE = 0x00000153
	INTELLIGENT_PROBE_CORRUPT = 0x00000154
	PROBE_COLLECTION_NOT_STARTED = 0x00000155
	PROBE_POWER_CONSUMPTION_EXCEEDED = 0x00000156
	WARNING_PROBE_CHANNEL_OUT_OF_SYNC = 0x00000157
	ENDPOINT_MISSING = 0x00000158
	UNKNOWN_ENDPOINT_REQUEST = 0x00000159
	ADC_TYPE_ERROR = 0x0000015A
	FPGA2_FAILED = 0x0000015B
	FPGA2_DEVICE_STATUS = 0x0000015C
	ENABLED_PROGRAM_FPGA2_FAILED = 0x0000015D
	NO_CANNELS_OR_PORTS_ENABLED = 0x0000015E
	INVALID_RATIO_MODE = 0x0000015F
	READS_NOT_SUPPORTED_IN_CURRENT_CAPTURE_MODE = 0x00000160
	TRIGGER_READ_SELECTION_CHECK_FAILED = 0x00000161
	DATA_READ1_SELECTION_CHECK_FAILED = 0x00000162
	DATA_READ2_SELECTION_CHECK_FAILED = 0x00000164
	DATA_READ3_SELECTION_CHECK_FAILED = 0x00000168
	READ_SELECTION_OUT_OF_RANGE = 0x00000170
	MULTIPLE_RATIO_MODES = 0x00000171
	NO_SAMPLES_READ = 0x00000172
	RATIO_MODE_NOT_REQUESTED = 0x00000173
	NO_USER_READ_REQUESTS = 0x00000174
	ZERO_SAMPLES_INVALID = 0x00000175
	ANALOGUE_HARDWARE_MISSING = 0x00000176
	ANALOGUE_HARDWARE_PINS = 0x00000177
	ANALOGUE_SMPS_FAULT = 0x00000178
	DIGITAL_ANALOGUE_HARDWARE_CONFLICT = 0x00000179
	RATIO_MODE_BUFFER_NOT_SET = 0x0000017A
	RESOLUTION_NOT_SUPPORTED_BY_VARIENT = 0x0000017B
	THRESHOLD_OUT_OF_RANGE = 0x0000017C
	INVALID_SIMPLE_TRIGGER_DIRECTION = 0x0000017D
	AUX_NOT_SUPPORTED = 0x0000017E
	NULL_DIRECTIONS = 0x0000017F
	NULL_CHANNEL_PROPERTIES = 0x00000180
	TRIGGER_CHANNEL_NOT_ENABLED = 0x00000181
	CONDITION_HAS_NO_TRIGGER_PROPERTY = 0x00000182
	RATIO_MODE_TRIGGER_MASKING_INVALID = 0x00000183
	TRIGGER_DATA_REQUIRES_MIN_BUFFER_SIZE_OF_40_SAMPLES = 0x00000184
	NO_OF_CAPTURES_OUT_OF_RANGE = 0x00000185
	RATIO_MODE_SEGMENT_HEADER_DOES_NOT_REQUIRE_BUFFERS = 0x00000186
	FOR_SEGMENT_HEADER_USE_GETTRIGGERINFO = 0x00000187
	READ_NOT_SET = 0x00000188
	ADC_SETTING_MISMATCH = 0x00000189
	DATATYPE_INVALID = 0x0000018A
	RATIO_MODE_DOES_NOT_SUPPORT_DATATYPE = 0x0000018B
	CHANNEL_COMBINATION_NOT_VALID_IN_THIS_RESOLUTION = 0x0000018C
	USE_8BIT_RESOLUTION = 0x0000018D
	AGGREGATE_BUFFERS_SAME_POINTER = 0x0000018E
	OVERLAPPED_READ_VALUES_OUT_OF_RANGE = 0x0000018F
	OVERLAPPED_READ_SEGMENTS_OUT_OF_RANGE = 0x00000190
	CHANNELFLAGSCOMBINATIONS_ARRAY_SIZE_TOO_SMALL = 0x00000191
	CAPTURES_EXCEEDS_NO_OF_SUPPORTED_SEGMENTS = 0x00000192
	TIME_UNITS_OUT_OF_RANGE = 0x00000193
	NO_SAMPLES_REQUESTED = 0x00000194
	INVALID_ACTION = 0x00000195
	NO_OF_SAMPLES_NEED_TO_BE_EQUAL_WHEN_ADDING_BUFFERS = 0x00000196
	WAITING_FOR_DATA_BUFFERS = 0x00000197
	STREAMING_ONLY_SUPPORTS_ONE_READ = 0x00000198
	CLEAR_DATA_BUFFER_INVALID = 0x00000199
	INVALID_ACTION_FLAGS_COMBINATION = 0x0000019A
	PICO_MOTH_MIN_AND_MAX_NULL_BUFFERS_CANNOT_BE_ADDED = 0x0000019B
	CONFLICT_IN_SET_DATA_BUFFERS_CALL_REMOVE_DATA_BUFFER_TO_RESET = 0x0000019C
	REMOVING_DATA_BUFFER_ENTRIES_NOT_ALLOWED_WHILE_DATA_PROCESSING = 0x0000019D
	CYUSB_REQUEST_FAILED = 0x00000200
	STREAMING_DATA_REQUIRED = 0x00000201
	INVALID_NUMBER_OF_SAMPLES = 0x00000202
	INALID_DISTRIBUTION = 0x00000203
	BUFFER_LENGTH_GREATER_THAN_INT32_T = 0x00000204
	PLL_MUX_OUT_FAILED = 0x00000209
	ONE_PULSE_WIDTH_DIRECTION_ALLOWED = 0x0000020A
	EXTERNAL_TRIGGER_NOT_SUPPORTED = 0x0000020B
	NO_TRIGGER_CONDITIONS_SET = 0x0000020C
	NO_OF_CHANNEL_TRIGGER_PROPERTIES_OUT_OF_RANGE = 0x0000020D
	PROBE_COMPNENT_ERROR = 0x0000020E
	INVALID_TRIGGER_CHANNELS_FOR_ETS = 0x00000210
	NOT_AVALIABLE_WHEN_STREAMING_IS_RUNNING = 0x00000211
	INVALID_TRIGGER_WITHIN_PRE_TRIGGER_STATE = 0x00000212
	ZERO_NUMBER_OF_CAPTURES_INVALID = 0x00000213
	INVALID_LENGTH = 0x00000214
	TRIGGER_DELAY_OUT_OF_RANGE = 0x00000300
	INVALID_THRESHOLD_DIRECTION = 0x00000301
	INVALID_THRESGOLD_MODE = 0x00000302
	TIMEBASE_NOT_SUPPORTED_BY_RESOLUTION = 0x00000303
	INVALID_VARIANT = 0x00001000
	MEMORY_MODULE_ERROR = 0x00001001
	PULSE_WIDTH_QUALIFIER_LOWER_UPPER_CONFILCT = 0x00002000
	PULSE_WIDTH_QUALIFIER_TYPE = 0x00002001
	PULSE_WIDTH_QUALIFIER_DIRECTION = 0x00002002
	THRESHOLD_MODE_OUT_OF_RANGE = 0x00002003
	TRIGGER_AND_PULSEWIDTH_DIRECTION_IN_CONFLICT = 0x00002004
	THRESHOLD_UPPER_LOWER_MISMATCH = 0x00002005
	PULSE_WIDTH_LOWER_OUT_OF_RANGE = 0x00002006
	PULSE_WIDTH_UPPER_OUT_OF_RANGE = 0x00002007
	FRONT_PANEL_ERROR = 0x00002008
	FRONT_PANEL_MODE = 0x0000200B
	FRONT_PANEL_FEATURE = 0x0000200C
	NO_PULSE_WIDTH_CONDITIONS_SET = 0x0000200D
	TRIGGER_PORT_NOT_ENABLED = 0x0000200E
	DIGITAL_DIRECTION_NOT_SET = 0x0000200F
	I2C_DEVICE_INVALID_READ_COMMAND = 0x00002010
	I2C_DEVICE_INVALID_RESPONSE = 0x00002011
	I2C_DEVICE_INVALID_WRITE_COMMAND = 0x00002012
	I2C_DEVICE_ARGUMENT_OUT_OF_RANGE = 0x00002013
	I2C_DEVICE_MODE = 0x00002014
	I2C_DEVICE_SETUP_FAILED = 0x00002015
	I2C_DEVICE_FEATURE = 0x00002016
	I2C_DEVICE_VALIDATION_FAILED = 0x00002017
	INTERNAL_HEADER_ERROR = 0x00002018
	FAILED_TO_WRITE_HARDWARE_FAULT = 0x00002019
	MSO_TOO_MANY_EDGE_TRANSITIONS_WHEN_USING_PULSE_WIDTH = 0x00003000
	INVALID_PROBE_LED_POSITION = 0x00003001
	PROBE_LED_POSITION_NOT_SUPPORTED = 0x00003002
	DUPLICATE_PROBE_CHANNEL_LED_POSITION = 0x00003003
	PROBE_LED_FAILURE = 0x00003004
	PROBE_NOT_SUPPORTED_BY_THIS_DEVICE = 0x00003005
	INVALID_PROBE_NAME = 0x00003006
	NO_PROBE_COLOUR_SETTINGS = 0x00003007
	NO_PROBE_CONNECTED_ON_REQUESTED_CHANNEL = 0x00003008
	PROBE_DOES_NOT_REQUIRE_CALIBRATION = 0x00003009
	PROBE_CALIBRATION_FAILED = 0x0000300A
	PROBE_VERSION_ERROR = 0x0000300B
	PROBE_DOES_NOT_SUPPORT_FREQUENCY_COUNTER = 0x0000300C
	AUTO_TRIGGER_TIME_TOO_LONG = 0x00004000
	MSO_POD_VALIDATION_FAILED = 0x00005000
	NO_MSO_POD_CONNECTED = 0x00005001
	DIGITAL_PORT_HYSTERESIS_OUT_OF_RANGE = 0x00005002
	MSO_POD_FAILED_UNIT = 0x00005003
	ATTENUATION_FAILED = 0x00005004
	DC_50OHM_OVERVOLTAGE_TRIPPED = 0x00005005
	MSO_OVER_CURRENT_TRIPPED = 0x00005006
	NOT_RESPONDING_OVERHEATED = 0x00005010
	HARDWARE_CAPTURE_TIMEOUT = 0x00006000
	HARDWARE_READY_TIMEOUT = 0x00006001
	HARDWARE_CAPTURING_CALL_STOP = 0x00006002
	TOO_FEW_REQUESTED_STREAMING_SAMPLES = 0x00007000
	STREAMING_REREAD_DATA_NOT_AVAILABLE = 0x00007001
	STREAMING_COMBINATION_OF_RAW_DATA_AND_ONE_AGGREGATION_DATA_TYPE_ALLOWED = 0x00007002
	DEVICE_TIME_STAMP_RESET = 0x01000000
	TRIGGER_TIME_NOT_REQUESTED = 0x02000001
	TRIGGER_TIME_BUFFER_NOT_SET = 0x02000002
	TRIGGER_TIME_FAILED_TO_CALCULATE = 0x02000004
	TRIGGER_WITHIN_A_PRE_TRIGGER_FAILED_TO_CALCULATE = 0x02000008
	TRIGGER_TIME_STAMP_NOT_REQUESTED = 0x02000100
	RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_DOES_NOT_REQUIRE_BUFFERS = 0x02200000
	RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_DOES_NOT_HAVE_BUFFERS = 0x02200001
	RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_USE_GETTRIGGERINFO = 0x02200002
	STREAMING_DOES_NOT_SUPPORT_TRIGGER_RATIO_MODES = 0x02200003
	USE_THE_TRIGGER_READ = 0x02200004
	USE_A_DATA_READ = 0x02200005
	TRIGGER_READ_REQUIRES_INT16_T_DATA_TYPE = 0x02200006
	RATIO_MODE_REQUIRES_NUMBER_OF_SAMPLES_TO_BE_SET = 0x02200007
	SIGGEN_SETTINGS_MISMATCH = 0x03000010
	SIGGEN_SETTINGS_CHANGED_CALL_APPLY = 0x03000011
	SIGGEN_WAVETYPE_NOT_SUPPORTED = 0x03000012
	SIGGEN_TRIGGERTYPE_NOT_SUPPORTED = 0x03000013
	SIGGEN_TRIGGERSOURCE_NOT_SUPPORTED = 0x03000014
	SIGGEN_FILTER_STATE_NOT_SUPPORTED = 0x03000015
	SIGGEN_NULL_PARAMETER = 0x03000020
	SIGGEN_EMPTY_BUFFER_SUPPLIED = 0x03000021
	SIGGEN_RANGE_NOT_SUPPLIED = 0x03000022
	SIGGEN_BUFFER_NOT_SUPPLIED = 0x03000023
	SIGGEN_FREQUENCY_NOT_SUPPLIED = 0x03000024
	SIGGEN_SWEEP_INFO_NOT_SUPPLIED = 0x03000025
	SIGGEN_TRIGGER_INFO_NOT_SUPPLIED = 0x03000026
	SIGGEN_CLOCK_FREQ_NOT_SUPPLIED = 0x03000027
	SIGGEN_TOO_MANY_SAMPLES = 0x03000030
	SIGGEN_DUTYCYCLE_OUT_OF_RANGE = 0x03000031
	SIGGEN_CYCLES_OUT_OF_RANGE = 0x03000032
	SIGGEN_PRESCALE_OUT_OF_RANGE = 0x03000033
	SIGGEN_SWEEPTYPE_INVALID = 0x03000034
	SIGGEN_SWEEP_WAVETYPE_MISMATCH = 0x03000035
	SIGGEN_INVALID_SWEEP_PARAMETERS = 0x03000036
	SIGGEN_SWEEP_PRESCALE_NOT_SUPPORTED = 0x03000037
	AWG_OVER_VOLTAGE_RANGE = 0x03000038
	NOT_LOCKED_TO_REFERENCE_FREQUENCY = 0x03000039
	PERMISSIONS_ERROR = 0x03000040
	PORTS_WITHOUT_ANALOGUE_CHANNELS_ONLY_ALLOWED_IN_8BIT_RESOLUTION = 0x03001000
	ANALOGUE_FRONTEND_MISSING = 0x03003001
	FRONT_PANEL_MISSING = 0x03003002
	ANALOGUE_FRONTEND_AND_FRONT_PANEL_MISSING = 0x03003003
	DIGITAL_BOARD_HARDWARE_ERROR = 0x03003800
	FIRMWARE_UPDATE_REQUIRED_TO_USE_DEVICE_WITH_THIS_DRIVER = 0x03004000
	UPDATE_REQUIRED_NULL = 0x03004001
	FIRMWARE_UP_TO_DATE = 0x03004002
	FLASH_FAIL = 0x03004003
	INTERNAL_ERROR_FIRMWARE_LENGTH_INVALID = 0x03004004
	INTERNAL_ERROR_FIRMWARE_NULL = 0x03004005
	FIRMWARE_FAILED_TO_BE_CHANGED = 0x03004006
	FIRMWARE_FAILED_TO_RELOAD = 0x03004007
	FIRMWARE_FAILED_TO_BE_UPDATE = 0x03004008
	FIRMWARE_VERSION_OUT_OF_RANGE = 0x03004009
	OPTIONAL_BOOTLOADER_UPDATE_AVAILABLE_WITH_THIS_DRIVER = 0x03005000
	BOOTLOADER_VERSION_NOT_AVAILABLE = 0x03005001
	NO_APPS_AVAILABLE = 0x03008000
	UNSUPPORTED_APP = 0x03008001
	ADC_POWERED_DOWN = 0x03002000
	WATCHDOGTIMER = 0x10000000
	IPP_NOT_FOUND = 0x10000001
	IPP_NO_FUNCTION = 0x10000002
	IPP_ERROR = 0x10000003
	SHADOW_CAL_NOT_AVAILABLE = 0x10000004
	SHADOW_CAL_DISABLED = 0x10000005
	SHADOW_CAL_ERROR = 0x10000006
	SHADOW_CAL_CORRUPT = 0x10000007
	DEVICE_MEMORY_OVERFLOW = 0x10000008
	ADC_TEST_FAILURE = 0x10000010
	RESERVED_1 = 0x11000000
	SOURCE_NOT_READY = 0x20000000
	SOURCE_INVALID_BAUD_RATE = 0x20000001
	SOURCE_NOT_OPENED_FOR_WRITE = 0x20000002
	SOURCE_FAILED_TO_WRITE_DEVICE = 0x20000003
	SOURCE_EEPROM_FAIL = 0x20000004
	SOURCE_EEPROM_NOT_PRESENT = 0x20000005
	SOURCE_EEPROM_NOT_PROGRAMMED = 0x20000006
	SOURCE_LIST_NOT_READY = 0x20000007
	SOURCE_FTD2XX_NOT_FOUND = 0x20000008
	SOURCE_FTD2XX_NO_FUNCTION = 0x20000009


class PicoInfo(FlexIntEnum):
	"""A piece of information about an oscilloscope."""

	DRIVER_VERSION = 0x00000000
	USB_VERSION = 0x00000001
	HARDWARE_VERSION = 0x00000002
	VARIANT_INFO = 0x00000003
	BATCH_AND_SERIAL = 0x00000004
	CAL_DATE = 0x00000005
	KERNEL_VERSION = 0x00000006
	DIGITAL_HARDWARE_VERSION = 0x00000007
	ANALOGUE_HARDWARE_VERSION = 0x00000008
	FIRMWARE_VERSION_1 = 0x00000009
	FIRMWARE_VERSION_2 = 0x0000000A
	MAC_ADDRESS = 0x0000000B
	SHADOW_CAL = 0x0000000C
	IPP_VERSION = 0x0000000D


class PicoConnectProbe(FlexIntEnum):
	"""The type of a probe."""

	PICO_CONNECT_PROBE_NONE = 0

	PICO_CONNECT_PROBE_D9_BNC = 4000
	PICO_CONNECT_PROBE_D9_2X_BNC = 4001
	PICO_CONNECT_PROBE_DIFFERENTIAL = 4002
	PICO_CONNECT_PROBE_CURRENT_CLAMP_200_2KA = 4003
	PICO_CONNECT_PROBE_CURRENT_CLAMP_40A = 4004
	PICO_CONNECT_PROBE_CAT3_HV_1KV = 4005
	PICO_CONNECT_PROBE_CURRENT_CLAMP_2000ARMS = 4006

	PICO_BNC_PLUS_PREMIUM_TEST_LEAD_BLUE = 4404
	PICO_BNC_PLUS_PREMIUM_TEST_LEAD_RED = 4405
	PICO_BNC_PLUS_PREMIUM_TEST_LEAD_GREEN = 4406
	PICO_BNC_PLUS_PREMIUM_TEST_LEAD_YELLOW = 4407
	PICO_BNC_PLUS_COP_PROBE = 4408

	PICO_BNC_PLUS_TEMPERATURE_PROBE = 5000
	PICO_BNC_PLUS_100A_CURRENT_CLAMP = 5003
	PICO_BNC_PLUS_HT_PICKUP = 5005
	PICO_BNC_PLUS_X10_SCOPE_PROBE = 5006
	PICO_BNC_PLUS_2000A_CURRENT_CLAMP = 5007
	PICO_BNC_PLUS_PRESSURE_SENSOR = 5008
	PICO_BNC_PLUS_RESISTANCE_LEAD = 5009
	PICO_BNC_PLUS_60A_CURRENT_CLAMP = 5010
	PICO_BNC_PLUS_OPTICAL_SENSOR = 5011
	PICO_BNC_PLUS_60A_CURRENT_CLAMP_V2 = 5012

	PICO_PASSIVE_PROBE_X10 = 6000
	PICO_ACTIVE_X10_750MHZ = 6001
	PICO_ACTIVE_X10_1_3GHZ = 6002

	PICO_CONNECT_PROBE_INTELLIGENT = -3

	PICO_CONNECT_PROBE_UNKNOWN_PROBE = -2
	PICO_CONNECT_PROBE_FAULT_PROBE = -1


class PicoConnectProbeRange(FlexIntEnum):
	"""The range and scale of a channel/probe."""

	X1_PROBE_10MV = 0
	X1_PROBE_20MV = 1
	X1_PROBE_50MV = 2
	X1_PROBE_100MV = 3
	X1_PROBE_200MV = 4
	X1_PROBE_500MV = 5
	X1_PROBE_1V = 6
	X1_PROBE_2V = 7
	X1_PROBE_5V = 8
	X1_PROBE_10V = 9
	X1_PROBE_20V = 10
	X1_PROBE_50V = 11
	X1_PROBE_100V = 12
	X1_PROBE_200V = 13

	X10_PROBE_100MV = 32
	X10_PROBE_200MV = 33
	X10_PROBE_500MV = 34
	X10_PROBE_1V = 35
	X10_PROBE_2V = 36
	X10_PROBE_5V = 37
	X10_PROBE_10V = 38
	X10_PROBE_20V = 39
	X10_PROBE_50V = 40
	X10_PROBE_100V = 41
	X10_PROBE_200V = 42
	X10_PROBE_500V = 43

	CONNECT_PROBE_OFF = 1024

	D9_BNC_10MV = 0
	D9_BNC_20MV = 1
	D9_BNC_50MV = 2
	D9_BNC_100MV = 3
	D9_BNC_200MV = 4
	D9_BNC_500MV = 5
	D9_BNC_1V = 6
	D9_BNC_2V = 7
	D9_BNC_5V = 8
	D9_BNC_10V = 9
	D9_BNC_20V = 10
	D9_BNC_50V = 11
	D9_BNC_100V = 12
	D9_BNC_200V = 13

	D9_2X_BNC_10MV = D9_BNC_10MV
	D9_2X_BNC_20MV = D9_BNC_20MV
	D9_2X_BNC_50MV = D9_BNC_50MV
	D9_2X_BNC_100MV = D9_BNC_100MV
	D9_2X_BNC_200MV = D9_BNC_200MV
	D9_2X_BNC_500MV = D9_BNC_500MV
	D9_2X_BNC_1V = D9_BNC_1V
	D9_2X_BNC_2V = D9_BNC_2V
	D9_2X_BNC_5V = D9_BNC_5V
	D9_2X_BNC_10V = D9_BNC_10V
	D9_2X_BNC_20V = D9_BNC_20V
	D9_2X_BNC_50V = D9_BNC_50V
	D9_2X_BNC_100V = D9_BNC_100V
	D9_2X_BNC_200V = D9_BNC_200V

	DIFFERENTIAL_10MV = D9_BNC_10MV
	DIFFERENTIAL_20MV = D9_BNC_20MV
	DIFFERENTIAL_50MV = D9_BNC_50MV
	DIFFERENTIAL_100MV = D9_BNC_100MV
	DIFFERENTIAL_200MV = D9_BNC_200MV
	DIFFERENTIAL_500MV = D9_BNC_500MV
	DIFFERENTIAL_1V = D9_BNC_1V
	DIFFERENTIAL_2V = D9_BNC_2V
	DIFFERENTIAL_5V = D9_BNC_5V
	DIFFERENTIAL_10V = D9_BNC_10V
	DIFFERENTIAL_20V = D9_BNC_20V
	DIFFERENTIAL_50V = D9_BNC_50V
	DIFFERENTIAL_100V = D9_BNC_100V
	DIFFERENTIAL_200V = D9_BNC_200V

	CURRENT_CLAMP_200A_2kA_1A = 4000
	CURRENT_CLAMP_200A_2kA_2A = 4001
	CURRENT_CLAMP_200A_2kA_5A = 4002
	CURRENT_CLAMP_200A_2kA_10A = 4003
	CURRENT_CLAMP_200A_2kA_20A = 4004
	CURRENT_CLAMP_200A_2kA_50A = 4005
	CURRENT_CLAMP_200A_2kA_100A = 4006
	CURRENT_CLAMP_200A_2kA_200A = 4007
	CURRENT_CLAMP_200A_2kA_500A = 4008
	CURRENT_CLAMP_200A_2kA_1000A = 4009
	CURRENT_CLAMP_200A_2kA_2000A = 4010

	CURRENT_CLAMP_40A_100mA = 5000
	CURRENT_CLAMP_40A_200mA = 5001
	CURRENT_CLAMP_40A_500mA = 5002
	CURRENT_CLAMP_40A_1A = 5003
	CURRENT_CLAMP_40A_2A = 5004
	CURRENT_CLAMP_40A_5A = 5005
	CURRENT_CLAMP_40A_10A = 5006
	CURRENT_CLAMP_40A_20A = 5007
	CURRENT_CLAMP_40A_40A = 5008

	KV_2_5V = 6003
	KV_5V = 6004
	KV_12_5V = 6005
	KV_25V = 6006
	KV_50V = 6007
	KV_125V = 6008
	KV_250V = 6009
	KV_500V = 6010
	KV_1000V = 6011

	CURRENT_CLAMP_2000ARMS_10A = 6500
	CURRENT_CLAMP_2000ARMS_20A = 6501
	CURRENT_CLAMP_2000ARMS_50A = 6502
	CURRENT_CLAMP_2000ARMS_100A = 6503
	CURRENT_CLAMP_2000ARMS_200A = 6504
	CURRENT_CLAMP_2000ARMS_500A = 6505
	CURRENT_CLAMP_2000ARMS_1000A = 6506
	CURRENT_CLAMP_2000ARMS_2000A = 6507
	CURRENT_CLAMP_2000ARMS_5000A = 6508

	CURRENT_CLAMP_100A_2_5A = 10000
	CURRENT_CLAMP_100A_5A = 10001
	CURRENT_CLAMP_100A_10A = 10002
	CURRENT_CLAMP_100A_25A = 10003
	CURRENT_CLAMP_100A_50A = 10004
	CURRENT_CLAMP_100A_100A = 10005

	CURRENT_CLAMP_60A_2A = 10500
	CURRENT_CLAMP_60A_5A = 10501
	CURRENT_CLAMP_60A_10A = 10502
	CURRENT_CLAMP_60A_20A = 10503
	CURRENT_CLAMP_60A_50A = 10504
	CURRENT_CLAMP_60A_60A = 10505

	OPTICAL_SENSOR_10V = 10550

	CURRENT_CLAMP_60A_V2_0_5A = 10600
	CURRENT_CLAMP_60A_V2_1A = 10601
	CURRENT_CLAMP_60A_V2_2A = 10602
	CURRENT_CLAMP_60A_V2_5A = 10603
	CURRENT_CLAMP_60A_V2_10A = 10604
	CURRENT_CLAMP_60A_V2_20A = 10605
	CURRENT_CLAMP_60A_V2_50A = 10606
	CURRENT_CLAMP_60A_V2_60A = 10607

	X10_ACTIVE_PROBE_100MV = 10700
	X10_ACTIVE_PROBE_200MV = 10701
	X10_ACTIVE_PROBE_500MV = 10702
	X10_ACTIVE_PROBE_1V = 10703
	X10_ACTIVE_PROBE_2V = 10704
	X10_ACTIVE_PROBE_5V = 10705

	_full_scale: dict["PicoConnectProbeRange", float]

	@property
	def full_scale(self) -> float:
		"""
		Get full scale value for this PicoConnectProbeRange member.

		If the raw data is normalized to (-1.0, 1.0), multiplying it by this
		value will achieve the correct scaling.

		:return: Full scale for this PicoConnectProbeRange member.
		:rtype: float
		:raises ValueError: Will raise if no scale is known for this value.
		"""
		if self in self._full_scale:
			return self._full_scale[self]
		else:
			raise ValueError(f"No known scale for PicoConnectProbeRange {self}")


PicoConnectProbeRange._full_scale = {
	PicoConnectProbeRange.X1_PROBE_10MV: 0.1,
	PicoConnectProbeRange.X1_PROBE_20MV: 0.2,
	PicoConnectProbeRange.X1_PROBE_50MV: 0.5,
	PicoConnectProbeRange.X1_PROBE_100MV: 0.1,
	PicoConnectProbeRange.X1_PROBE_200MV: 0.2,
	PicoConnectProbeRange.X1_PROBE_500MV: 0.5,
	PicoConnectProbeRange.X1_PROBE_1V: 1.0,
	PicoConnectProbeRange.X1_PROBE_2V: 2.0,
	PicoConnectProbeRange.X1_PROBE_5V: 5.0,
	PicoConnectProbeRange.X1_PROBE_10V: 10.0,
	PicoConnectProbeRange.X1_PROBE_20V: 20.0,
	PicoConnectProbeRange.X1_PROBE_50V: 50.0,
	PicoConnectProbeRange.X1_PROBE_100V: 100.0,
	PicoConnectProbeRange.X1_PROBE_200V: 200.0,
	PicoConnectProbeRange.X10_PROBE_100MV: 0.1,
	PicoConnectProbeRange.X10_PROBE_200MV: 0.2,
	PicoConnectProbeRange.X10_PROBE_500MV: 0.5,
	PicoConnectProbeRange.X10_PROBE_1V: 1.0,
	PicoConnectProbeRange.X10_PROBE_2V: 2.0,
	PicoConnectProbeRange.X10_PROBE_5V: 5.0,
	PicoConnectProbeRange.X10_PROBE_10V: 10.0,
	PicoConnectProbeRange.X10_PROBE_20V: 20.0,
	PicoConnectProbeRange.X10_PROBE_50V: 50.0,
	PicoConnectProbeRange.X10_PROBE_100V: 100.0,
	PicoConnectProbeRange.X10_PROBE_200V: 200.0,
	PicoConnectProbeRange.X10_PROBE_500V: 500.0,
	PicoConnectProbeRange.CONNECT_PROBE_OFF: 0.0,
	PicoConnectProbeRange.D9_BNC_10MV: 0.01,
	PicoConnectProbeRange.D9_BNC_20MV: 0.02,
	PicoConnectProbeRange.D9_BNC_50MV: 0.05,
	PicoConnectProbeRange.D9_BNC_100MV: 0.1,
	PicoConnectProbeRange.D9_BNC_200MV: 0.2,
	PicoConnectProbeRange.D9_BNC_500MV: 0.5,
	PicoConnectProbeRange.D9_BNC_1V: 1.0,
	PicoConnectProbeRange.D9_BNC_2V: 2.0,
	PicoConnectProbeRange.D9_BNC_5V: 5.0,
	PicoConnectProbeRange.D9_BNC_10V: 10.0,
	PicoConnectProbeRange.D9_BNC_20V: 20.0,
	PicoConnectProbeRange.D9_BNC_50V: 50.0,
	PicoConnectProbeRange.D9_BNC_100V: 100.0,
	PicoConnectProbeRange.D9_BNC_200V: 200.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_1A: 1.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_2A: 2.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_5A: 5.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_20A: 20.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_50A: 50.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_100A: 100.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_200A: 200.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_500A: 500.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_1000A: 1000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_200A_2kA_2000A: 2000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_100mA: 0.1,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_200mA: 0.2,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_500mA: 0.5,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_1A: 1.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_2A: 2.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_5A: 5.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_20A: 20.0,
	PicoConnectProbeRange.CURRENT_CLAMP_40A_40A: 40.0,
	PicoConnectProbeRange.KV_2_5V: 2.5,
	PicoConnectProbeRange.KV_5V: 5.0,
	PicoConnectProbeRange.KV_12_5V: 12.5,
	PicoConnectProbeRange.KV_25V: 25.0,
	PicoConnectProbeRange.KV_50V: 50.0,
	PicoConnectProbeRange.KV_125V: 125.0,
	PicoConnectProbeRange.KV_250V: 250.0,
	PicoConnectProbeRange.KV_500V: 500.0,
	PicoConnectProbeRange.KV_1000V: 1000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_20A: 20.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_50A: 50.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_100A: 100.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_200A: 200.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_500A: 500.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_1000A: 1000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_2000A: 2000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_2000ARMS_5000A: 5000.0,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_2_5A: 2.5,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_5A: 5.0,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_25A: 25.0,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_50A: 50.0,
	PicoConnectProbeRange.CURRENT_CLAMP_100A_100A: 100.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_2A: 2.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_5A: 5.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_20A: 20.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_50A: 50.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_60A: 60.0,
	PicoConnectProbeRange.OPTICAL_SENSOR_10V: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_0_5A: 0.5,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_1A: 1.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_2A: 2.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_5A: 5.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_10A: 10.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_20A: 20.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_50A: 50.0,
	PicoConnectProbeRange.CURRENT_CLAMP_60A_V2_60A: 60.0,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_100MV: 0.1,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_200MV: 0.2,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_500MV: 0.5,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_1V: 1.0,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_2V: 2.0,
	PicoConnectProbeRange.X10_ACTIVE_PROBE_5V: 5.0,
}


class PicoProbeUserAction(FlexIntEnum):
	"""Probe user action."""

	BUTTON_PRESS = 0


class PicoProbeButtonPressType(FlexIntEnum):
	"""The duration of the button press event."""

	SHORT_DURATION_PRESS = 0
	LONG_DURATION_PRESS = 1


DIGITAL_PORT_SERIAL_LENGTH = 10
DIGITAL_PORT_CALIBRATION_DATE_LENGTH = 8
MAX_DELAY_COUNT = 8388607  # Inferred, not defined in this model's headers.
