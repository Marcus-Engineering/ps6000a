"""PicoScope API structure and other type definitions."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: types.py
#
# PicoScope API structure and other type definitions.
#
# Portions Copyright 2018-2019 Pico Technology Ltd. (ISC Licensed)
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Created from PicoDeviceStructs.py.             jrowley
#
###############################################################################

from ctypes import (
	Structure,
	c_double,
	c_int8,
	c_int16,
	c_int32,
	c_uint8,
	c_uint16,
	c_uint32,
	c_uint64,
)

from ps6000a.constants import (
	DIGITAL_PORT_CALIBRATION_DATE_LENGTH,
	DIGITAL_PORT_SERIAL_LENGTH,
	PicoChannel,
	PicoConnectProbeRange,
	PicoDataType,
	PicoDigitalDirection,
	PicoProbeButtonPressType,
	PicoRatioMode,
	PicoStatus,
	PicoThresholdDirection,
	PicoThresholdMode,
	PicoTimeUnits,
	PicoTriggerState,
)


class PicoTriggerInfo(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Contains trigger information for a single buffer segment.

	:ivar status: Indicates success or failure.
	:type status: PicoStatus
	:ivar segment_index: The number of the segment.
	:type segment_index: int
	:ivar trigger_index: The index of the sample at which the trigger occurred.
	:type trigger_index: int
	:ivar trigger_time: The time at which the trigger occurred.
	:type trigger_time: float
	:ivar time_units: The units for ``trigger_time``.
	:type time_units: PicoTimeUnits
	:ivar missed_triggers: The number of trigger events, if any, detected since
		the start of previous segment.
	:type missed_triggers: int
	:ivar time_stamp_counter: The time in samples from the first capture to the
		current capture. The status ``PicoStatus.DEVICE_TIME_STAMP_RESET``
		indicates that the trigger time has started over.
	:type time_stamp_counter: int
	"""

	_status: int
	segment_index: int
	trigger_index: int
	trigger_time: float
	_time_units: int
	missed_triggers: int
	time_stamp_counter: int

	_pack_ = 1
	_fields_ = [
		("_status", c_uint32),
		("segment_index", c_uint64),
		("trigger_index", c_uint64),
		("trigger_time", c_double),
		("_time_units", c_uint32),
		("missed_triggers", c_uint64),
		("time_stamp_counter", c_uint64),
	]

	@property
	def status(self) -> PicoStatus:
		"""
		Turn ``_status`` integer into PicoStatus enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoStatus enum type.
		"""
		return PicoStatus(self._status)

	@status.setter
	def status(self, status: PicoStatus) -> None:
		"""Update ``_status`` from PicoStatus enum."""
		self._status = status.value

	@property
	def time_units(self) -> PicoTimeUnits:
		"""
		Turn ``_time_units`` integer into PicoTimeUnits enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoTimeUnits enum type.
		"""
		return PicoTimeUnits(self._time_units)

	@time_units.setter
	def time_units(self, time_units: PicoTimeUnits) -> None:
		"""Update ``_time_units`` from PicoTimeUnits enum."""
		self._time_units = time_units.value


class PicoTriggerChannelProperties(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Specifies the trigger mechanism.

	There are two trigger thresholds called Upper and Lower. Each trigger type
	uses one or other of these thresholds, or both, as specified in
	``set_trigger_channel_directions``. Each trigger threshold has its own
	hysteresis setting.

	:ivar upper_threshold: The upper threshold at which the trigger fires. It is
		scaled in 16-bit ADC counts at the currently selected range for that
		channel. Use when "Upper" or "Both" is specified in
		``set_trigger_channel_directions``.
	:type upper_threshold: int
	:ivar upper_hysteresis: The distance by which the signal must fall below the
		upper threshold (for rising edge triggers) or rise above the upper
		threshold (for falling edge triggers) in order to rearm the trigger for
		the next event. It is scaled in 16-bit counts.
	:type upper_hysteresis: int
	:ivar lower_threshold: Lower threshold (see ``upper_threshold``). Use when
		"Lower" or "Both" is specified in ``set_trigger_channel_directions``.
	:type lower_threshold: int
	:ivar lower_hysteresis: Lower threshold hysteresis (see
		``upper_hysteresis``).
	:type lower_hysteresis: int
	:ivar channel: The channel to which the properties apply. Only analog
		channels (i.e. CHANNEL_A through CHANNEL_H) are permitted, and only
		channels that exist on the oscilloscope model in use.
	:type channel: PicoChannel
	"""

	upper_threshold: int
	upper_hysteresis: int
	lower_threshold: int
	lower_hysteresis: int
	_channel: int

	_pack_ = 1
	_fields_ = [
		("upper_threshold", c_int16),
		("upper_hysteresis", c_uint16),
		("lower_threshold", c_int16),
		("lower_hysteresis", c_uint16),
		("_channel", c_uint32),
	]

	@property
	def channel(self) -> PicoChannel:
		"""
		Turn ``_channel`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._channel)

	@channel.setter
	def channel(self, channel: PicoChannel) -> None:
		"""Update ``_channel`` from PicoChannel enum."""
		self._channel = channel.value


class PicoCondition(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Specifies trigger condition.

	:ivar source: The signal that forms an input to the trigger condition.
	:type source: PicoChannel
	:ivar condition: The type of condition that should be applied.
	:type condition: PicoTriggerState
	"""

	_source: int
	_condition: int

	_pack_ = 1
	_fields_ = [("_source", c_uint32), ("_condition", c_uint32)]

	@property
	def source(self) -> PicoChannel:
		"""
		Turn ``_source`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._source)

	@source.setter
	def source(self, source: PicoChannel) -> None:
		"""Update ``_source`` from PicoChannel enum."""
		self._source = source.value

	@property
	def condition(self) -> PicoTriggerState:
		"""
		Turn ``_condition`` integer into PicoTriggerState enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoTriggerState(self._condition)

	@condition.setter
	def condition(self, condition: PicoTriggerState) -> None:
		"""Update ``_condition`` from PicoTriggerState enum."""
		self._condition = condition.value


class PicoDirection(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Specifies trigger direction.

	:ivar channel: The channel whose direction you want to set.
	:type channel: PicoChannel
	:ivar direction: The direction required for the channel.
	:type direction: PicoThresholdDirection
	:ivar threshold_mode: The type of threshold to use.
	:type threshold_mode: PicoThresholdMode
	"""

	_channel: int
	_direction: int
	_threshold_mode: int

	_pack_ = 1
	_fields_ = [
		("_channel", c_uint32),
		("_direction", c_uint32),
		("_threshold_mode", c_uint32),
	]

	@property
	def channel(self) -> PicoChannel:
		"""
		Turn ``_channel`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._channel)

	@channel.setter
	def channel(self, channel: PicoChannel) -> None:
		"""Update ``_channel`` from PicoChannel enum."""
		self._channel = channel.value

	@property
	def direction(self) -> PicoThresholdDirection:
		"""
		Turn ``_direction`` integer into PicoThresholdDirection enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoThresholdDirection enum type.
		"""
		return PicoThresholdDirection(self._direction)

	@direction.setter
	def direction(self, direction: PicoThresholdDirection) -> None:
		"""Update ``_direction`` from PicoThresholdDirection enum."""
		self._direction = direction.value

	@property
	def threshold_mode(self) -> PicoThresholdMode:
		"""
		Turn ``_threshold_mode`` integer into PicoThresholdMode enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoThresholdMode enum type.
		"""
		return PicoThresholdMode(self._threshold_mode)

	@threshold_mode.setter
	def threshold_mode(self, threshold_mode: PicoThresholdMode) -> None:
		"""Update ``_threshold_mode`` from PicoThresholdMode enum."""
		self._threshold_mode = threshold_mode.value


class PicoStreamingDataInfo(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Specifies parameters for streaming mode data capture.

	:ivar channel: The oscilloscope channel that the parameters apply to.
	:type channel: PicoChannel
	:ivar mode: The downsampling mode to use.
	:type mode: PicoRatioMode
	:ivar type: The data type to use for the sample data.
	:type type: PicoDataType
	:ivar no_of_samples: The number of samples made available by the driver.
	:type no_of_samples: int
	:ivar buffer_index: An index to the starting sample with the specified
		waveform buffer.
	:type buffer_index: int
	:ivar start_index: An index to the waveform buffer within the capture
		buffer.
	:type start_index: int
	:ivar overflow: True if any sample value overflowed, False otherwise.
	:type overflow: int
	"""

	_channel: int
	_mode: int
	_type: int
	no_of_samples: int
	buffer_index: int
	start_index: int
	_overflow: int

	_pack_ = 1
	_fields_ = [
		("_channel", c_uint32),
		("_mode", c_uint32),
		("_type", c_uint32),
		("no_of_samples", c_int32),
		("buffer_index", c_uint64),
		("start_index", c_int32),
		("_overflow", c_int16),
	]

	@property
	def channel(self) -> PicoChannel:
		"""
		Turn ``_channel`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._channel)

	@channel.setter
	def channel(self, channel: PicoChannel) -> None:
		"""Update ``_channel`` from PicoChannel enum."""
		self._channel = channel.value

	@property
	def mode(self) -> PicoRatioMode:
		"""
		Turn ``_mode`` integer into PicoRatioMode enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoRatioMode enum type.
		"""
		return PicoRatioMode(self._mode)

	@mode.setter
	def mode(self, mode: PicoRatioMode) -> None:
		"""Update ``_mode`` from PicoRatioMode enum."""
		self._mode = mode.value

	@property
	def type(self) -> PicoDataType:
		"""
		Turn ``_type`` integer into PicoDataType enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoDataType enum type.
		"""
		return PicoDataType(self._type)

	@type.setter
	def type(self, type_: PicoDataType) -> None:
		"""Update ``_type`` from PicoDataType enum."""
		self._type = type_.value

	@property
	def overflow(self) -> bool:
		"""Turn ``_overflow`` integer into boolean value."""
		return bool(self._overflow)

	@overflow.setter
	def overflow(self, overflow: bool) -> None:
		"""Update ``_overflow`` from boolean value."""
		self._overflow = bool(overflow)


class PicoStreamingDataTriggerInfo(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Contains information about trigger events.

	:ivar trigger_at: An index to the sample on which the trigger occurred.
	:type trigger_at: int
	:ivar triggered: True if a trigger occurred, False otherwise.
	:type triggered: bool
	:ivar auto_stop: True if the oscilloscope was in auto-stop mode, False
		otherwise.
	:type auto_stop: bool
	"""

	trigger_at: int
	_triggered: int
	_auto_stop: int

	_pack_ = 1
	_fields_ = [
		("trigger_at", c_uint64),
		("_triggered", c_int16),
		("_auto_stop", c_int16),
	]

	@property
	def triggered(self) -> bool:
		"""Turn ``_triggered`` integer into boolean value."""
		return bool(self._triggered)

	@triggered.setter
	def triggered(self, triggered: bool) -> None:
		"""Update ``_triggered`` from boolean value."""
		self._triggered = bool(triggered)

	@property
	def auto_stop(self) -> bool:
		"""Turn ``_auto_stop`` integer into boolean value."""
		return bool(self._auto_stop)

	@auto_stop.setter
	def auto_stop(self, auto_stop: bool) -> None:
		"""Update ``_auto_stop`` from boolean value."""
		self._auto_stop = bool(auto_stop)


class PicoScalingFactorsValues(Structure):
	# noinspection PyUnresolvedReferences
	"""
	No documentation available.

	Used as input and output to ``get_scaling_values``.

	SPECULATION:

	:ivar channel: The applicable channel.
	:type channel: PicoChannel
	:ivar range: The current channel range and scaling.
	:type range: PicoConnectProbeRange
	:ivar offset: The offset, in ADC counts.
	:type offset: int
	:ivar scaling_factor: The scaling factor from ADC counts to target units.
	:type scaling_factor: c_double
	"""

	_channel: int
	_range: int
	offset: int
	scaling_factor: float

	_pack_ = 1
	_fields_ = [
		("_channel", c_uint32),
		("_range", c_uint32),
		("offset", c_int16),
		("scaling_factor", c_double),
	]

	@property
	def channel(self) -> PicoChannel:
		"""
		Turn ``_channel`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._channel)

	@channel.setter
	def channel(self, channel: PicoChannel) -> None:
		"""Update ``_channel`` from PicoChannel enum."""
		self._channel = channel.value

	@property
	def range(self) -> PicoConnectProbeRange:
		"""
		Turn ``_range`` integer into PicoConnectProbeRange enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoConnectProbeRange enum type.
		"""
		return PicoConnectProbeRange(self._range)

	@range.setter
	def range(self, range_: PicoConnectProbeRange) -> None:
		"""Update ``_range`` from PicoConnectProbeRange enum."""
		self._range = range_.value


class PicoDigitalChannelDirections(Structure):
	# noinspection PyUnresolvedReferences
	"""
	Specifies the digital channel trigger direction for a single pin.

	:ivar channel: The digital channel.
	:type channel: PicoChannel
	:ivar direction: The trigger direction.
	:type direction: PicoDigitalDirection
	"""

	_channel: int
	_direction: int

	_pack_ = 1
	_fields_ = [("_channel", c_uint32), ("direction", c_uint32)]

	@property
	def channel(self) -> PicoChannel:
		"""
		Turn ``_channel`` integer into PicoChannel enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoChannel enum type.
		"""
		return PicoChannel(self._channel)

	@channel.setter
	def channel(self, channel: PicoChannel) -> None:
		"""Update ``_channel`` from PicoChannel enum."""
		self._channel = channel.value

	@property
	def direction(self) -> PicoDigitalDirection:
		"""
		Turn ``_direction`` integer into PicoDigitalDirection enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoDigitalDirection enum type.
		"""
		return PicoDigitalDirection(self._direction)

	@direction.setter
	def direction(self, direction: PicoDigitalDirection) -> None:
		"""Update ``_direction`` from PicoDigitalDirection enum."""
		self._direction = direction.value


class PicoDigitalPortInteractions(Structure):
	"""
	No documentation available.

	Passed to ``PicoDigitalPortInteractionsCallback`` callback.
	"""

	_pack_ = 1
	_fields_ = [
		("connected", c_uint16),
		("channel", c_uint32),
		("digital_port_name", c_uint32),
		("status", c_uint32),
		("serial", c_int8 * DIGITAL_PORT_SERIAL_LENGTH),
		("calibration_date", c_int8 * DIGITAL_PORT_CALIBRATION_DATE_LENGTH),
	]


class PicoChannelOvervoltageTripped(Structure):
	"""
	No documentation available.

	Returned by ``report_all_channels_overvoltage_trip_status`` and similar.
	"""

	_pack_ = 1
	_fields_ = [
		("channel", c_uint32),
		("tripped", c_uint8),
	]


class PicoProbeButtonPressParameter(Structure):
	# noinspection PyUnresolvedReferences
	"""
	The parameter struct for a button press event.

	:ivar button_index: Which button was pressed (in case future probes have
		multiple buttons).
	:type button_index: int
	:ivar button_press_type: The type/duration of press.
	:type button_press_type: PicoProbeButtonPressType
	"""

	button_index: int
	_button_press_type: int

	_pack_ = 1
	_fields_ = [
		("button_index", c_uint8),
		("_button_press_type", c_uint32),
	]

	@property
	def button_press_type(self) -> PicoProbeButtonPressType:
		"""
		Turn ``_button_press_type`` integer into PicoProbeButtonPressType enum.

		:raises ValueError: Will raise if stored value is not a member of the
			PicoProbeButtonPressType enum type.
		"""
		return PicoProbeButtonPressType(self._button_press_type)

	@button_press_type.setter
	def button_press_type(self, button_press_type: PicoProbeButtonPressType) -> None:
		"""Update ``_button_press_type`` from PicoProbeButtonPressType enum."""
		self._button_press_type = button_press_type.value


class PicoUserProbeInteractions(Structure):
	"""
	Contains data for notification of intelligent probe change.

	Not planned for Pythonization.
	"""

	_pack_ = 1
	_fields_ = [
		("connected", c_uint16),
		("channel", c_uint32),
		("enabled", c_uint16),
		("probe_name", c_uint32),
		("requires_power", c_uint8),
		("is_powered", c_uint8),
		("status", c_uint32),
		("probe_off", c_uint32),
		("range_first", c_uint32),
		("range_last", c_uint32),
		("range_current", c_uint32),
		("coupling_first", c_uint32),
		("coupling_last", c_uint32),
		("coupling_current", c_uint32),
		("filter_flags", c_uint32),
		("filter_current", c_uint32),
		("default_filter", c_uint32),
	]


class PicoHandle(int):
	"""The handle to the PicoScope hardware."""

	@property
	def valid(self) -> bool:
		"""
		Check if this handle is valid.

		:getter: Check if this handle is valid.
		:setter: None, computed/read-only.
		:return: True if this handle is valid, False otherwise.
		:rtype: bool
		"""
		return self > 0
