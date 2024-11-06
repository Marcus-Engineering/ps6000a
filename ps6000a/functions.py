"""PicoScope 6000E main API."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: types.py
#
# PicoScope 6000E main API.
# Loads the DLL and provides typed Python wrappers for all functions.
#
# Functions are converted to not require any pointers outside of this module,
# and where enums are returned the actual enum object is constructed.
# Documentation is taken from the manual.
#
# Some functions are not fully Pythonized or documented because they are not
# expected to be used in the scope of this project.
#
# APPLICABLE DLL VERSION: 1.0.67.2674
#
# Portions Copyright 2018-2019 Pico Technology Ltd. (ISC Licensed)
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Generated.                                     jrowley
#   20240314       Added minimal API for block mode.              jrowley
#
###############################################################################

from ctypes import (
	Array,
	addressof,
	byref,
	c_char_p,
	c_double,
	c_int16,
	c_int32,
	c_uint8,
	c_uint16,
	c_uint32,
	c_uint64,
	c_void_p,
)
from ctypes import cast as c_cast
from ctypes import create_string_buffer, sizeof, windll
from ctypes.util import find_library
from typing import Optional, Sequence, Union

from ps6000a.callbacks import (
	BlockReadyCType,
	DataReadyCType,
	DigitalPortInteractionsCType,
	PicoAWGOverrangeInteractionsCType,
	PicoDataReadyUsingReadsCType,
	PicoExternalReferenceInteractionsCType,
	PicoProbeInteractionsCType,
	PicoProbeUserActionCType,
	PicoTemperatureSensorInteractionsCType,
	PicoUpdateFirmwareProgressCType,
)
from ps6000a.constants import (
	PicoAction,
	PicoBandwidthLimiter,
	PicoChannel,
	PicoChannelFlags,
	PicoConnectProbeRange,
	PicoCoupling,
	PicoDataType,
	PicoDeviceResolution,
	PicoDigitalPortHysteresis,
	PicoInfo,
	PicoRatioMode,
	PicoStatus,
	PicoThresholdDirection,
	PicoTimeUnits,
	PicoTriggerWithinPreTrigger,
)
from ps6000a.types import (
	PicoCondition,
	PicoDirection,
	PicoHandle,
	PicoScalingFactorsValues,
	PicoStreamingDataInfo,
	PicoStreamingDataTriggerInfo,
	PicoTriggerChannelProperties,
	PicoTriggerInfo,
)

lib_path = find_library("ps6000a")
if lib_path is None:
	raise ImportError("Could not load ps6000a driver (not installed?).")
_dll = windll.LoadLibrary(lib_path)

_open_unit = _dll.ps6000aOpenUnit
_open_unit.restype = c_uint32
_open_unit.argtypes = [c_void_p, c_char_p, c_int32]


def open_unit(
	serial: Optional[str], resolution: PicoDeviceResolution
) -> tuple[PicoStatus, PicoHandle]:
	"""
	Open a scope device (ps6000aOpenUnit).

	This function opens a PicoScope 6000E Series scope attached to the computer.
	The maximum number of units that can be opened depends on the operating
	system, the kernel driver and the computer.

	:param serial: A string containing the serial number of the scope to be
		opened. Optional. If None, then the function opens the first scope
		found; otherwise, it tries to open the scope that matches the string.
	:type serial: Optional[str]
	:param resolution: The required vertical resolution.
	:type resolution: PicoDeviceResolution
	:return: Status and resulting handle.

		**Handle:**
		The result of the attempt to open a scope:

		- –1 : if the scope fails to open
		- 0 : if no scope is found
		- > 0 : a number that uniquely identifies the scope

		If a valid handle is returned, it must be used in all subsequent calls
		to API functions to identify this scope. This handle is valid only if
		the function returns ``PicoStatus.OK``.
	:rtype: tuple[PicoStatus, PicoHandle]
	"""
	handle = c_int16()
	ser_char_p: Optional[c_char_p] = None
	if serial is not None:
		ser_chars = create_string_buffer(serial.encode("ASCII"))
		ser_char_p = c_cast(addressof(ser_chars), c_char_p)
	status = PicoStatus(_open_unit(byref(handle), ser_char_p, resolution))
	return status, PicoHandle(handle.value)


_open_unit_async = _dll.ps6000aOpenUnitAsync
_open_unit_async.restype = c_uint32
_open_unit_async.argtypes = [c_void_p, c_char_p, c_int32]


def open_unit_async(
	serial: Optional[str], resolution: PicoDeviceResolution
) -> tuple[PicoStatus, bool]:
	"""
	Open unit without blocking (ps6000aOpenUnitAsync).

	This function opens a scope without blocking the calling thread. You can
	find out when it has finished by periodically calling ``open_unit_progress``
	until that function indicates the operation is complete.

	:param serial: A string containing the serial number of the scope to be
		opened. Optional. If None, then the function opens the first scope
		found; otherwise, it tries to open the scope that matches the string.
	:type serial: Optional[str]
	:param resolution: The required vertical resolution.
	:type resolution: PicoDeviceResolution
	:return: Main status and opening status.

		**Opening status:**
		False if the open operation was disallowed because
		another open operation is in progress or True if the open operation was
		successfully started.
	:rtype: tuple[PicoStatus, bool]
	"""
	status2 = c_int16()
	ser_char_p: Optional[c_char_p] = None
	if serial is not None:
		ser_chars = create_string_buffer(serial.encode("ASCII"))
		ser_char_p = c_cast(addressof(ser_chars), c_char_p)
	status = PicoStatus(_open_unit_async(byref(status2), ser_char_p, resolution))
	return status, bool(status2.value)


_open_unit_progress = _dll.ps6000aOpenUnitProgress
_open_unit_progress.restype = c_uint32
_open_unit_progress.argtypes = [c_void_p, c_void_p, c_void_p]


def open_unit_progress() -> tuple[PicoStatus, PicoHandle, int, bool]:
	"""
	Get status of opening a unit (ps6000aOpenUnitProgress).

	This function checks on the progress of a request made to
	``open_unit_async`` to open a scope.

	:return: Status, then resulting handle, then progress percent, then
		compeletion flag.

		The handle is the result of the attempt to open a scope:
		- –1 : if the scope fails to open
		- 0 : if no scope is found
		- > 0 : a number that uniquely identifies the scope
		If a valid handle is returned, it must be used in all subsequent calls
		to API functions to identify this scope. This handle is valid only if
		the function returns ``PicoStatus.OK``.

		Progress percent is 0 while the operation is in progress or 100 when the
		operation is complete.

		Complete is True when open operation has finished, False otherwise.
	:rtype: tuple[PicoStatus, PicoHandle, int, bool]
	"""
	handle = c_int16()
	progress = c_int16()
	complete = c_int16()
	status = PicoStatus(
		_open_unit_progress(byref(handle), byref(progress), byref(complete))
	)
	return status, PicoHandle(handle.value), progress.value, bool(complete.value)


_get_unit_info = _dll.ps6000aGetUnitInfo
_get_unit_info.restype = c_uint32
_get_unit_info.argtypes = [c_int16, c_char_p, c_int16, c_void_p, c_int32]


def get_unit_info(handle: PicoHandle, info: PicoInfo) -> tuple[PicoStatus, str]:
	"""
	Get information about device (ps6000aGetUnitInfo).

	This function retrieves information about the specified oscilloscope. If the
	device fails to open, only the driver version and error code are available
	to explain why the last open unit call failed. To find out about unopened
	devices, call ``enumerate_units``.

	:param handle: Identifies the device from which information is required. If
		an invalid handle is passed, the error code from the last unit that
		failed to open is returned.
	:type handle: PicoHandle
	:param info: ``PicoInfo`` enum tag specifying what information is required.
	:type info: PicoInfo
	:return: Status, and info string for selected info item.
	:rtype: tuple[PicoStatus, str]
	"""
	info_length = c_int16(256)
	info_chars = create_string_buffer(info_length.value)
	info_char_p = c_cast(addressof(info_chars), c_char_p)
	status = PicoStatus(
		_get_unit_info(handle, info_char_p, info_length, byref(info_length), info)
	)
	info_string = info_chars.value.decode("ASCII")
	return status, info_string


_close_unit = _dll.ps6000aCloseUnit
_close_unit.restype = c_uint32
_close_unit.argtypes = [c_int16]


def close_unit(handle: PicoHandle) -> PicoStatus:
	"""
	Close a scope device (ps6000aCloseUnit).

	This function shuts down a PicoScope 6000E Series oscilloscope.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_close_unit(handle))


_flash_led = _dll.ps6000aFlashLed
_flash_led.restype = c_uint32
_flash_led.argtypes = [c_int16, c_int16]


def flash_led(handle: PicoHandle, start: int) -> PicoStatus:
	"""
	Flash the front-panel LED (ps6000aFlashLed).

	This function flashes the status/trigger LED on the front of the scope
	without blocking the calling thread. Calls to ``run_streaming`` and
	``run_block`` cancel any flashing started by this function. It is not
	possible to set the LED to be constantly illuminated, as this state is used
	to indicate that the scope has not been initialized.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param start: The action required:
		- < 0 : flash the LED indefinitely.
		- 0 : stop the LED flashing.
		- > 0 : flash the LED start times.
		If the LED is already flashing on entry to this function, the flash
		count will be reset to start.
	:type start: int
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_flash_led(handle, start))


_memory_segments = _dll.ps6000aMemorySegments
_memory_segments.restype = c_uint32
_memory_segments.argtypes = [c_int16, c_uint64, c_void_p]


def memory_segments(handle: PicoHandle, n_segments: int) -> tuple[PicoStatus, int]:
	"""
	Set number of memory segments (ps6000aMemorySegments).

	This function sets the number of memory segments that the scope will use.
	See also ``memory_segments_by_samples``.

	When the scope is opened, the number of segments defaults to 1, meaning that
	each capture fills the scope's available memory. This function allows you to
	divide the memory into a number of segments so that the scope can store
	several waveforms sequentially.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param n_segments: The number of segments required. See datasheet for
		capacity of each model.
	:type n_segments: int
	:return: Status, and the number of samples available in each segment. This
		is the total number over all channels, so if more than one channel is in
		use then the number of samples available to each channel is this divided
		by the number of channels.
	:rtype: tuple[PicoStatus, int]
	"""
	n_max_samples = c_uint64()
	status = PicoStatus(_memory_segments(handle, n_segments, byref(n_max_samples)))
	return status, n_max_samples.value


_memory_segments_by_samples = _dll.ps6000aMemorySegmentsBySamples
_memory_segments_by_samples.restype = c_uint32
_memory_segments_by_samples.argtypes = [c_int16, c_uint64, c_void_p]


def memory_segments_by_samples(
	handle: PicoHandle, n_samples: int
) -> tuple[PicoStatus, int]:
	"""
	Set size of memory segments (ps6000aMemorySegmentsBySamples).

	This function sets the number of samples per memory segment. Like
	``memory_segments`` it controls the segmentation of the capture memory, but
	in this case you specify the number of samples rather than the number of
	segments.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param n_samples: the number of samples required in each segment. See
		datasheet for capacity of each model. This is the total number over n
		channels, where n is the number of enabled channels or MSO ports rounded
		up to the next power of 2. For example, with 5 channels or ports
		enabled, n is 8. If n > 1, the number of segments available will be
		reduced accordingly.
	:type n_samples: int
	:return: Status, and the number of segments into which the capture memory
		has been divided.
	:rtype: tuple[PicoStatus, int]
	"""
	n_max_segments = c_uint64()
	status = PicoStatus(
		_memory_segments_by_samples(handle, n_samples, byref(n_max_segments))
	)
	return status, n_max_segments.value


_get_maximum_available_memory = _dll.ps6000aGetMaximumAvailableMemory
_get_maximum_available_memory.restype = c_uint32
_get_maximum_available_memory.argtypes = [c_int16, c_void_p, c_uint32]


def get_maximum_available_memory(
	handle: PicoHandle, resolution: PicoDeviceResolution
) -> tuple[PicoStatus, int]:
	"""
	Get maximium available memory (ps6000aGetMaximumAvailableMemory).

	This function returns the maximum number of samples that can be stored at a
	given hardware resolution.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param resolution: The vertical resolution.
	:type resolution: PicoDeviceResolution
	:return: Status, and the number of samples.
	:rtype: tuple[PicoStatus, int]
	"""
	n_max_samples = c_uint64()
	status = PicoStatus(
		_get_maximum_available_memory(handle, byref(n_max_samples), resolution)
	)
	return status, n_max_samples.value


_query_max_segments_by_samples = _dll.ps6000aQueryMaxSegmentsBySamples
_query_max_segments_by_samples.restype = c_uint32
_query_max_segments_by_samples.argtypes = [
	c_int16,
	c_uint64,
	c_int32,
	c_void_p,
	c_uint32,
]


def query_max_segments_by_samples(
	handle: PicoHandle,
	n_samples: int,
	n_channels_enabled: int,
	resolution: PicoDeviceResolution,
) -> tuple[PicoStatus, int]:
	"""
	Get number of segments (ps6000aQueryMaxSegmentsBySamples).

	This function returns the maximum number of memory segments available given
	the number of samples per segment.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param n_samples: The number of samples per segment.
	:type n_samples: int
	:param n_channels_enabled: The number of channels enabled.
	:type n_channels_enabled: int
	:param resolution: The vertical resolution.
	:type resolution: PicoDeviceResolution
	:return: Status, and the maximum number of segments that can be requested.
	:rtype: tuple[PicoStatus, int]
	"""
	n_max_segments = c_uint64()
	status = PicoStatus(
		_query_max_segments_by_samples(
			handle, n_samples, n_channels_enabled, byref(n_max_segments), resolution
		)
	)
	return status, n_max_segments.value


_set_channel_on = _dll.ps6000aSetChannelOn
_set_channel_on.restype = c_uint32
_set_channel_on.argtypes = [c_int16, c_uint32, c_uint32, c_uint32, c_double, c_uint32]


def set_channel_on(
	handle: PicoHandle,
	channel: PicoChannel,
	coupling: PicoCoupling,
	range_: PicoConnectProbeRange,
	analog_offset: float,
	bandwidth: PicoBandwidthLimiter,
) -> PicoStatus:
	"""
	Enable and set options for one channel (ps6000aSetChannelOn).

	This function switches an analog input channel on and specifies its input
	coupling type, voltage range, analog offset and bandwidth limit. Some of the
	arguments within this function have model-specific values. Consult the
	relevant section below according to the model you have. To switch off again,
	use ``set_channel_off``. For digital ports, see ``set_digital_channel_on``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param channel: The channel to be configured. Only analog channels (i.e.
		CHANNEL_A through CHANNEL_H) are permitted, and only channels that exist
		on the oscilloscope model in use.
	:type channel: PicoChannel
	:param coupling: The impedance and coupling type.
	:type coupling: PicoCoupling
	:param range_: The input voltage range and probe type.
	:type range_: PicoConnectProbeRange
	:param analog_offset: A voltage to add to the input channel before
		digitization.
	:type analog_offset: double
	:param bandwidth: The bandwidth limiter setting. Valid options are
		``BW_FULL``, ``BW_20MHZ``, and ``BW_200MHZ``.
	:type bandwidth: PicoBandwidthLimiter
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_channel_on(handle, channel, coupling, range_, analog_offset, bandwidth)
	)


_set_channel_off = _dll.ps6000aSetChannelOff
_set_channel_off.restype = c_uint32
_set_channel_off.argtypes = [c_int16, c_uint32]


def set_channel_off(handle: PicoHandle, channel: PicoChannel) -> PicoStatus:
	"""
	Disable one channel (ps6000aSetChannelOff).

	This function switches an analog input channel off. It has the opposite
	function to ``set_channel_on``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param channel: The channel to disable. Only analog channels (i.e. CHANNEL_A
		through CHANNEL_H) are permitted, and only channels that exist on the
		oscilloscope model in use.
	:type channel: PicoChannel
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_channel_off(handle, channel))


_set_digital_port_on = _dll.ps6000aSetDigitalPortOn
_set_digital_port_on.restype = c_uint32
_set_digital_port_on.argtypes = [c_int16, c_uint32, c_void_p, c_int16, c_uint32]


def set_digital_port_on(
	handle: PicoHandle,
	port: PicoChannel,
	logic_threshold_level: Sequence[int],
	hysteresis: PicoDigitalPortHysteresis,
) -> PicoStatus:
	"""
	Set up and enable digital inputs (ps6000aSetDigitalPortOn).

	This function switches on one or more digital ports and sets the logic
	thresholds. Refer to the data sheet for the fastest sampling rates available
	with different combinations of analog and digital inputs. In most cases the
	fastest rates will be obtained by disabling all analog channels. When all
	analog channels are disabled you must also select 8-bit resolution to allow
	the digital inputs to operate alone.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param port: The port to be configured. Only digital ports are permitted
		(i.e. ``PORT0`` and ``PORT1``).
	:type port: PicoChannel
	:param logic_threshold_level: A sequence of threshold voltages, one for each
		port pin, used to distinguish the 0 and 1 states. Range: –32767 (–5 V)
		to 32767 (+5 V). This determines how many pins are enabled.
	:type logic_threshold_level: Sequence[int]
	:param hysteresis: The hysteresis to apply to all channels in the port.
	:type hysteresis: PicoDigitalPortHysteresis
	:return: Status.
	:rtype: PicoStatus
	"""
	ltl_count = len(logic_threshold_level)
	ltl_array = (c_int16 * ltl_count)(*logic_threshold_level)
	ltl_ptr = c_cast(addressof(ltl_array), c_void_p)
	return PicoStatus(
		_set_digital_port_on(handle, port, ltl_ptr, ltl_count, hysteresis)
	)


_set_digital_port_off = _dll.ps6000aSetDigitalPortOff
_set_digital_port_off.restype = c_uint32
_set_digital_port_off.argtypes = [c_int16, c_uint32]


def set_digital_port_off(handle: PicoHandle, port: PicoChannel) -> PicoStatus:
	"""
	Switch off digital inputs (ps6000aSetDigitalPortOff).

	This function switches off one or more digital ports.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param port: The port to disable. Only digital ports are permitted (i.e.
		``PORT0`` and ``PORT1``).
	:type port: PicoChannel
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_digital_port_off(handle, port))


_get_timebase = _dll.ps6000aGetTimebase
_get_timebase.restype = c_uint32
_get_timebase.argtypes = [c_int16, c_uint32, c_uint64, c_void_p, c_void_p, c_uint64]


def get_timebase(
	handle: PicoHandle, timebase: int, no_samples: int, segment_index: int
) -> tuple[PicoStatus, float, int]:
	"""
	Get available timebases (ps6000aGetTimebase).

	This function calculates the sampling rate and maximum number of samples for
	a given timebase under the specified conditions. The result will depend on
	the number of channels enabled by the last call to ``set_channel_on`` or
	``set_channel_off``.

	The easiest way to find a suitable timebase is to call
	``nearest_sample_interval_stateless``. Alternatively, you can estimate the
	timebase number that you require using the information in the timebase
	guide, then call this function with that timebase and check the returned
	time interval (nanoseconds) value. Repeat until you obtain the time interval
	that you need.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param timebase: Timebase; see timebase guide in the manual.
	:type timebase: int
	:param no_samples: The number of samples required. This value is used to
		calculate the most suitable time interval.
	:type no_samples: int
	:param segment_index: The index of the memory segment to use.
	:type segment_index: int
	:return: Status, then time interval, then max samples.

		**Time interval:**
		The time interval (in nanoseconds) between readings
		at the selected timebase.

		**Max samples:**
		The maximum number of samples available. The scope
		allocates a	certain amount of memory for internal overheads and this may
		vary depending on the number of segments, number of channels enabled,
		and the timebase chosen.
	:rtype: tuple[PicoStatus, float, int]
	"""
	time_interval_ns = c_double()
	max_samples = c_uint64()
	status = PicoStatus(
		_get_timebase(
			handle,
			timebase,
			no_samples,
			byref(time_interval_ns),
			byref(max_samples),
			segment_index,
		)
	)
	return status, time_interval_ns.value, max_samples.value


_set_simple_trigger = _dll.ps6000aSetSimpleTrigger
_set_simple_trigger.restype = c_uint32
_set_simple_trigger.argtypes = [
	c_int16,
	c_int16,
	c_uint32,
	c_int16,
	c_uint32,
	c_uint64,
	c_uint32,
]


def set_simple_trigger(
	handle: PicoHandle,
	enable: bool,
	source: PicoChannel,
	threshold: int,
	direction: PicoThresholdDirection,
	delay: int,
	auto_trigger_micro_seconds: int,
) -> PicoStatus:
	"""
	Set up triggering (ps6000aSetSimpleTrigger).

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param enable: True to enable, or False to disable, the trigger.
	:type enable: int
	:param source: The channel on which to trigger. Only analog channels (i.e.
		CHANNEL_A through CHANNEL_H) are permitted, and only channels that
		exist on the oscilloscope model in use.
	:type source: PicoChannel
	:param threshold: The ADC count at which the trigger will fire.
	:type threshold: int
	:param direction: The direction in which the signal must move to cause a
		trigger. The following directions are supported: ABOVE, BELOW, RISING,
		FALLING and RISING_OR_FALLING.
	:type direction: PicoThresholdDirection
	:param delay: The time between the trigger occurring and the first sample
		being taken.
	:type delay: int
	:param auto_trigger_micro_seconds: The number of microseconds the device
		will wait if no trigger occurs.
	:type auto_trigger_micro_seconds: int
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_simple_trigger(
			handle,
			int(enable),
			source,
			threshold,
			direction,
			delay,
			auto_trigger_micro_seconds,
		)
	)


_trigger_within_pre_trigger_samples = _dll.ps6000aTriggerWithinPreTriggerSamples
_trigger_within_pre_trigger_samples.restype = c_uint32
_trigger_within_pre_trigger_samples.argtypes = [c_int16, c_uint32]


def trigger_within_pre_trigger_samples(
	handle: PicoHandle, state: PicoTriggerWithinPreTrigger
) -> PicoStatus:
	"""
	Switch feature on or off (ps6000aTriggerWithinPreTriggerSamples).

	This function controls a special triggering feature.
	(Seriously, that's all the documentation says.)

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param state: Whether to disable or enable the feature.
	:type state: PicoTriggerWithinPreTrigger
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_trigger_within_pre_trigger_samples(handle, state))


_set_trigger_channel_properties = _dll.ps6000aSetTriggerChannelProperties
_set_trigger_channel_properties.restype = c_uint32
_set_trigger_channel_properties.argtypes = [
	c_int16,
	c_void_p,
	c_int16,
	c_int16,
	c_uint32,
]


def set_trigger_channel_properties(
	handle: PicoHandle,
	channel_properties: Sequence[PicoTriggerChannelProperties],
	aux_output_enable: int,
	auto_trigger_micro_seconds: int,
) -> PicoStatus:
	"""
	Set up triggering (ps6000aSetTriggerChannelProperties).

	This function is used to enable or disable triggering and set its
	parameters.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param channel_properties: A sequence of ``PicoTriggerChannelProperties``
		describing the requested properties. The sequence can contain a single
		object describing the properties of one channel, or a number of objects
		describing several channels. If empty, triggering is switched off.
	:type channel_properties: Sequence[PicoTriggerChannelProperties]
	:param aux_output_enable: "Not used."
	:type aux_output_enable: int
	:param auto_trigger_micro_seconds: The time in microseconds for which the
		scope device will wait before collecting data if no trigger event
		occurs. If this is set to zero, the scope device will wait indefinitely
		for a trigger.
	:type auto_trigger_micro_seconds: int
	:return: Status.
	:rtype: PicoStatus
	"""
	cprop_count = len(channel_properties)
	cprop_array = (PicoTriggerChannelProperties * cprop_count)(*channel_properties)
	cprop_ptr = c_cast(addressof(cprop_array), c_void_p)
	return PicoStatus(
		_set_trigger_channel_properties(
			handle,
			cprop_ptr,
			cprop_count,
			aux_output_enable,
			auto_trigger_micro_seconds,
		)
	)


_set_trigger_channel_conditions = _dll.ps6000aSetTriggerChannelConditions
_set_trigger_channel_conditions.restype = c_uint32
_set_trigger_channel_conditions.argtypes = [c_int16, c_void_p, c_int16, c_uint32]


def set_trigger_channel_conditions(
	handle: PicoHandle, conditions: Sequence[PicoCondition], action: PicoAction
) -> PicoStatus:
	"""
	Set triggering logic (ps6000aSetTriggerChannelConditions).

	This function sets up trigger conditions on the scope's inputs. The trigger
	is defined by one or more ``PicoCondition`` structures that are then ORed
	together. Each structure is itself the AND of the states of one or more of
	the inputs. This AND-OR logic allows you to create any possible Boolean
	function of the scope's inputs.

	If complex triggering is not required, use ``set_simple_trigger``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param conditions: A sequence of ``PicoCondition`` structures specifying the
		conditions that should be applied to each channel. In the simplest case,
		the sequence consists of a single element. When there is more than one
		element, the overall trigger condition is the logical OR of all the
		elements. If the sequence is empty, triggering is switched off.
	:type conditions: Sequence[PicoCondition]
	:param action: Specifies how to apply the new conditions to any existing
		trigger conditions (i.e. append or replace).
	:type action: PicoAction
	:return: Status.
	:rtype: PicoStatus
	"""
	cond_count = len(conditions)
	cond_array = (PicoCondition * cond_count)(*conditions)
	cond_ptr = c_cast(addressof(cond_array), c_void_p)
	return PicoStatus(
		_set_trigger_channel_conditions(handle, cond_ptr, cond_count, action)
	)


_set_trigger_channel_directions = _dll.ps6000aSetTriggerChannelDirections
_set_trigger_channel_directions.restype = c_uint32
_set_trigger_channel_directions.argtypes = [c_int16, c_void_p, c_int16]


def set_trigger_channel_directions(
	handle: PicoHandle, directions: Sequence[PicoDirection]
) -> PicoStatus:
	"""
	Set trigger directions (ps6000aSetTriggerChannelDirections).

	This function sets the direction of the trigger for one or more channels.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param directions: A sequence of ``PicoDirection`` objects, each specifying
		the trigger direction for a channel.
	:type directions: Sequence[PicoDirection]
	:return: Status.
	:rtype: PicoStatus
	"""
	dir_count = len(directions)
	dir_array = (PicoDirection * dir_count)(*directions)
	dir_ptr = c_cast(addressof(dir_array), c_void_p)
	return PicoStatus(_set_trigger_channel_directions(handle, dir_ptr, dir_count))


_set_trigger_delay = _dll.ps6000aSetTriggerDelay
_set_trigger_delay.restype = c_uint32
_set_trigger_delay.argtypes = [c_int16, c_uint64]


def set_trigger_delay(handle: PicoHandle, delay: int) -> PicoStatus:
	"""
	Set post-trigger delay (ps6000aSetTriggerDelay).

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param delay: The time between the trigger occurring and the first sample.
		For example, if delay=100, the scope would wait 100 sample periods
		before sampling. At a timebase of 5 GS/s, or 200 ps per sample
		(timebase=0), the total delay would then be 100 x 200 ps = 20 ns.
		Range: 0 to MAX_DELAY_COUNT.
	:type delay: int
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_trigger_delay(handle, delay))


_set_data_buffer = _dll.ps6000aSetDataBuffer
_set_data_buffer.restype = c_uint32
_set_data_buffer.argtypes = [
	c_int16,
	c_uint32,
	c_void_p,
	c_int32,
	c_uint32,
	c_uint64,
	c_uint32,
	c_uint32,
]


def set_data_buffer(
	handle: PicoHandle,
	channel: PicoChannel,
	buffer: Optional[Array],
	data_type: PicoDataType,
	waveform: int,
	down_sample_ratio_mode: PicoRatioMode,
	action: PicoAction,
) -> PicoStatus:
	"""
	Allocate and provide location of data buffer (ps6000aSetDataBuffer).

	This function will not allocate memory. The ctypes array must be created
	beforehand. Also note that in streaming mode, the same buffer may need to
	be registered multiple times even if the user never clears it.

	This function tells the driver where to store the data, either unprocessed
	or downsampled, that will be returned after the next call to one of the
	``get_values`` functions. The function allows you to specify only a single
	buffer, so for aggregation mode, which requires two buffers, you must call
	``set_data_buffers`` instead.

	The buffer persists between captures until it is replaced with another
	buffer or buffer is set to NULL. The buffer can be replaced at any time
	between calls to ``get_values``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param channel: The channel you want to use with the buffer.
	:type channel: PicoChannel
	:param buffer: The data buffer to use. Sample count will be determined
		from buffer length. Data type must match ``data_type``. May be set to
		``None``, which in combination with ``action`` can clear buffers.
	:type buffer: Optional[Array]
	:param data_type: The data type that you wish to use for the sample values.
	:type data_type: PicoDataType
	:param waveform: The segment index.
	:type waveform: int
	:param down_sample_ratio_mode: The downsampling mode. See ``get_values`` for
		the available modes, but note that a single call to ``get_data_buffer``
		can only associate one buffer with one downsampling mode. If you intend
		to call ``get_values`` with more than one downsampling mode activated,
		then you must call ``get_data_buffer`` several times to associate a
		separate buffer with each downsampling mode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param action: The method to use when creating the buffer. The buffer is
		added to a unique list for the channel, data type and segment. Therefore
		you must use ``PicoAction.CLEAR_ALL`` to remove all buffers already
		written. ``PicoAction`` values can be ORed together to allow clearing
		and adding in one call.
	:type action: PicoAction
	:return: Status.
	:rtype: PicoStatus
	"""
	buffer_ptr: Optional[c_void_p]
	if buffer is None:
		buffer_ptr = None
		n_samples = 0
	else:
		n_samples = len(buffer)
		if sizeof(buffer) != (n_samples * sizeof(data_type.ctype)):
			raise TypeError("Buffer size mismatch, is data type wrong?")
		buffer_ptr = c_cast(addressof(buffer), c_void_p)
	status = PicoStatus(
		_set_data_buffer(
			handle,
			channel,
			buffer_ptr,
			n_samples,
			data_type,
			waveform,
			down_sample_ratio_mode,
			action,
		)
	)
	return status


_set_data_buffers = _dll.ps6000aSetDataBuffers
_set_data_buffers.restype = c_uint32
_set_data_buffers.argtypes = [
	c_int16,
	c_uint32,
	c_void_p,
	c_void_p,
	c_int32,
	c_uint32,
	c_uint64,
	c_uint32,
	c_uint32,
]


def set_data_buffers(
	handle: PicoHandle,
	channel: PicoChannel,
	buffer_max: Optional[Array],
	buffer_min: Optional[Array],
	data_type: PicoDataType,
	waveform: int,
	down_sample_ratio_mode: PicoRatioMode,
	action: PicoAction,
) -> PicoStatus:
	"""
	Allocate and provide location of both data buffers (ps6000aSetDataBuffers).

	This function will not allocate memory. The ctypes array must be created
	beforehand. Also note that in streaming mode, the same buffers may need to
	be registered multiple times even if the user never clears them.

	This function tells the driver the location of two buffers for receiving
	data. If you do not need two buffers, because you are not using aggregate
	mode, then you should use ``get_data_buffer`` instead.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param channel: The channel for which you want to set the buffers.
	:type channel: PicoChannel
	:param buffer_max: The "max" data buffer to use. Sample count will be
		determined from buffer length. Data type must match ``data_type``.
		This will receive the maximum data values in aggregation mode, or the
		non-aggregated values otherwise. Set to ``None`` to not set a buffer,
		which in combination with ``action`` can clear buffers. May not be
		``None`` if ``buffer_min`` is not ``None``.
	:type buffer_max: Array
	:param buffer_min: The "min" data buffer to use. Sample count will be
		determined from buffer length. Data type must match ``data_type``.
		This will receive the minimum aggregated data values. Not used in
		other downsampling modes. Set to ``None`` to not set a buffer, which
		in combination with ``action`` can clear buffers.
	:type buffer_min: Array
	:param data_type: The data type that you wish to use for the sample values.
	:type data_type: PicoDataType
	:param waveform: The segment index.
	:type waveform: int
	:param down_sample_ratio_mode: The downsampling mode. See ``get_values`` for
		the available modes, but note that a single call to ``get_data_buffers``
		can only associate one buffer pair with one downsampling mode. If you
		intend to call ``get_values`` with more than one downsampling mode
		activated, then you must call ``get_data_buffers`` several times to
		associate a separate buffer pair with each downsampling mode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param action: The method to use when creating the buffers. The buffers are
		added to a unique list for the channel, data type and segment. Therefore
		you must use ``PicoAction.CLEAR_ALL`` to remove all buffers already
		written. ``PicoAction`` values can be ORed together to allow clearing
		and adding in one call.
	:type action: PicoAction
	:return: Status.
	:rtype: PicoStatus
	"""
	if buffer_min is not None and buffer_max is None:
		raise TypeError("Cannot set min buffer without max buffer.")
	buffer_max_ptr: Optional[c_void_p]
	buffer_min_ptr: Optional[c_void_p]
	if buffer_max is None:
		buffer_max_ptr = None
		buffer_min_ptr = None
		n_samples = 0
	else:
		n_samples = len(buffer_max)
		if sizeof(buffer_max) != (n_samples * sizeof(data_type.ctype)):
			raise TypeError("Buffer (max) size mismatch, is data type wrong?")
		buffer_max_ptr = c_cast(addressof(buffer_max), c_void_p)
		if buffer_min is None:
			buffer_min_ptr = None
		else:
			if len(buffer_max) != len(buffer_min):
				raise TypeError("Buffer min vs. max size mismatch.")
			if sizeof(buffer_min) != (n_samples * sizeof(data_type.ctype)):
				raise TypeError("Buffer (min) size mismatch, is data type wrong?")
			buffer_min_ptr = c_cast(addressof(buffer_min), c_void_p)
	status = PicoStatus(
		_set_data_buffers(
			handle,
			channel,
			buffer_max_ptr,
			buffer_min_ptr,
			n_samples,
			data_type,
			waveform,
			down_sample_ratio_mode,
			action,
		)
	)
	return status


_run_streaming = _dll.ps6000aRunStreaming
_run_streaming.restype = c_uint32
_run_streaming.argtypes = [
	c_int16,
	c_void_p,
	c_uint32,
	c_uint64,
	c_uint64,
	c_int16,
	c_uint64,
	c_uint32,
]


def run_streaming(
	handle: PicoHandle,
	sample_interval: float,
	sample_interval_time_units: PicoTimeUnits,
	max_pre_trigger_samples: int,
	max_post_trigger_samples: int,
	auto_stop: bool,
	down_sample_ratio: int,
	down_sample_ratio_mode: PicoRatioMode,
) -> tuple[PicoStatus, float]:
	"""
	Start streaming mode capture (ps6000aRunStreaming).

	This function tells the oscilloscope to start collecting data in streaming
	mode. The device can return either raw or downsampled data to your
	application while streaming is in progress. Call
	``get_streaming_latest_values`` to retrieve the data. Consult the manual
	for more details.

	When a trigger is set, the total number of samples is the sum of
	``max_pre_trigger_samples`` and ``max_post_trigger_samples``. If
	``auto_stop`` is False then this will become the maximum number of samples
	without downsampling.

	When downsampled data is returned, the raw samples remain stored on the
	device. The maximum number of raw samples that can be retrieved after
	streaming has stopped is (scope's memory size) / (resolution data size *
	channels), where channels is the number of active channels rounded up to a
	power of 2.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param sample_interval: The requested time interval between samples.
	:type sample_interval: float
	:param sample_interval_time_units: The unit of time used for
		``sample_interval``.
	:type sample_interval_time_units: PicoTimeUnits
	:param max_pre_trigger_samples: The maximum number of raw samples before a
		trigger event for each enabled channel. If no trigger condition is set
		this argument is ignored.
	:type max_pre_trigger_samples: int
	:param max_post_trigger_samples: The maximum number of raw samples after a
		trigger event for each enabled channel. If no trigger condition is set,
		this argument states the maximum number of samples to be stored.
	:type max_post_trigger_samples: int
	:param auto_stop: True if streaming should stop when the maximum number of
		samples have been captured, False otherwise.
	:type auto_stop: bool
	:param down_sample_ratio: The downsampling factor that will be applied to
		the raw data. Must be greater than zero.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: Which downsampling mode to use.
	:type down_sample_ratio_mode: PicoRatioMode
	:return: Status, and the actual sample interval (in units specified by
		``sample_interval_time_units``).
	:rtype: tuple[PicoStatus, float]
	"""
	sample_interval_out = c_double(sample_interval)
	status = PicoStatus(
		_run_streaming(
			handle,
			byref(sample_interval_out),
			sample_interval_time_units,
			max_pre_trigger_samples,
			max_post_trigger_samples,
			int(auto_stop),
			down_sample_ratio,
			down_sample_ratio_mode,
		)
	)
	return status, sample_interval_out.value


_get_streaming_latest_values = _dll.ps6000aGetStreamingLatestValues
_get_streaming_latest_values.restype = c_uint32
_get_streaming_latest_values.argtypes = [c_int16, c_void_p, c_uint64, c_void_p]


def get_streaming_latest_values(
	handle: PicoHandle, streaming_data_info: Sequence[PicoStreamingDataInfo]
) -> tuple[
	PicoStatus, Array[PicoStreamingDataInfo], Array[PicoStreamingDataTriggerInfo]
]:
	"""
	Read streaming data (ps6000aGetStreamingLatestValues).

	This function populates the ``PicoStreamingDataInfo`` structures with a
	description of the samples available and the
	``PicoStreamingDataTriggerInfo`` structures to indicate that a trigger has
	occurred and at what location.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param streaming_data_info: Data structures to be populated with buffer
		information. Set the channel, downsampling ratio, and datatype before
		calling this function; the driver will set the rest.
	:type streaming_data_info: Sequence[PicoStreamingDataInfo]
	:return: Status, then a list of structures containing buffer information,
		then a list of structures containing trigger information.
	:rtype: tuple[PicoStatus, Array[PicoStreamingDataInfo],
		Array[PicoStreamingDataTriggerInfo]]
	"""
	streaming_info_count = len(streaming_data_info)
	streaming_info_array = (PicoStreamingDataInfo * streaming_info_count)(
		*streaming_data_info
	)
	streaming_info_ptr = c_cast(addressof(streaming_info_array), c_void_p)
	streaming_trigger_array = (PicoStreamingDataTriggerInfo * streaming_info_count)()
	streaming_trigger_ptr = c_cast(addressof(streaming_trigger_array), c_void_p)
	status = PicoStatus(
		_get_streaming_latest_values(
			handle, streaming_info_ptr, streaming_info_count, streaming_trigger_ptr
		)
	)
	return status, streaming_info_array, streaming_trigger_array


_no_of_streaming_values = _dll.ps6000aNoOfStreamingValues
_no_of_streaming_values.restype = c_uint32
_no_of_streaming_values.argtypes = [c_int16, c_void_p]


def no_of_streaming_values(handle: PicoHandle) -> tuple[PicoStatus, int]:
	"""
	Get number of captured samples (ps6000aNoOfStreamingValues).

	This function returns the number of samples available after data collection
	in streaming mode. Call it after calling ``stop``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Status, and the number of samples.
	:rtype: tuple[PicoStatus, int]
	"""
	no_of_values = c_uint64()
	status = PicoStatus(_no_of_streaming_values(handle, byref(no_of_values)))
	return status, no_of_values.value


_stop = _dll.ps6000aStop
_stop.restype = c_uint32
_stop.argtypes = [c_int16]


def stop(handle: PicoHandle) -> PicoStatus:
	"""
	Stop sampling (ps6000aStop).

	This function stops the scope device from sampling data.

	When running the device in streaming mode, always call this function after
	the end of a capture to ensure that the scope is ready for the next capture.

	When running the device in block mode or rapid block mode, you can call this
	function to interrupt data capture.

	If this function is called before a trigger event occurs, the oscilloscope
	may not contain valid data.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_stop(handle))


_get_trigger_info = _dll.ps6000aGetTriggerInfo
_get_trigger_info.restype = c_uint32
_get_trigger_info.argtypes = [c_int16, c_void_p, c_uint64, c_uint64]


def get_trigger_info(
	handle: PicoHandle, first_segment_index: int, segment_count: int
) -> tuple[PicoStatus, Array[PicoTriggerInfo]]:
	"""
	Get trigger timing information (ps6000aGetTriggerInfo).

	This function gets trigger timing information from one or more buffer
	segments.

	Call this function after data has been captured or when data has been
	retrieved from a previous capture.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param first_segment_index: The index of the first segment of interest.
	:type first_segment_index: int
	:param segment_count: The number of segments of interest.
	:type segment_count: int
	:return: Status, and trigger info.

		**Trigger info:**
		A sequence of ``PicoTriggerInfo`` structures, one for each buffer
		segment, containing trigger information. Length will be equal to
		``segment_count``.
	:rtype: tuple[PicoStatus, Array[PicoTriggerInfo]]
	"""
	trigger_info = (PicoTriggerInfo * segment_count)()
	trigger_info_p = c_cast(addressof(trigger_info), c_void_p)
	status = PicoStatus(
		_get_trigger_info(handle, trigger_info_p, first_segment_index, segment_count)
	)
	return status, trigger_info


_enumerate_units = _dll.ps6000aEnumerateUnits
_enumerate_units.restype = c_uint32
_enumerate_units.argtypes = [c_void_p, c_char_p, c_void_p]


def enumerate_units(parameters: str = "") -> tuple[PicoStatus, int, str]:
	"""
	Get a list of unopened units (ps6000aEnumerateUnits).

	This function counts the number of PicoScope 6000 (A API) units connected
	to the computer, and returns a list of serial numbers and other optional
	information as a string. Note that this function can only detect devices
	that are not yet being controlled by an application. To query opened
	devices, use ``get_unit_info``.

	:param parameters: Can optionally contain the following parameter(s) to
		request information:

		- -v : model number
		- -c : calibration date
		- -h : hardware version
		- -u : USB version
		- -f : firmware version

		Example (any separator character can be used):

		``-v:-c:-h:-u:-f``

		Defaults to empty string.
	:type parameters: str
	:return: Status, then count, then serials.

		**Count:**
		On exit, the number of PicoScope 6000 (A API) units found.

		**Serials:**
		If ``parameters`` is an empty string, serials is populated on
		exit with a list of serial numbers separated by commas. Example:

		``AQ005/139,VDR61/356,ZOR14/107``

		If ``parameters`` contains parameters, more data will be appended. For
		example, if ``parameters`` is "-v:-c:-h:-u:-f", each serial number has
		the requested information appended in the following format:

		``AQ005/139[6425E,01Jan21,769,2.0,1.7.16.0]``
	:rtype: tuple[PicoStatus, int, str]
	"""
	count = c_int16()
	serials_length = c_int16(1024)
	serials_chars = create_string_buffer(
		parameters.encode("ASCII"), serials_length.value
	)
	serials_char_p = c_cast(addressof(serials_chars), c_char_p)
	status = PicoStatus(
		_enumerate_units(byref(count), serials_char_p, byref(serials_length))
	)
	serials_string = serials_chars.value.decode("ASCII")
	return status, count.value, serials_string


_ping_unit = _dll.ps6000aPingUnit
_ping_unit.restype = c_uint32
_ping_unit.argtypes = [c_int16]


def ping_unit(handle: PicoHandle) -> PicoStatus:
	"""
	Check if device is still connected (ps6000aPingUnit).

	This function can be used to check that the already opened device is still
	connected to the USB port and communication is successful.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_ping_unit(handle))


_get_analogue_offset_limits = _dll.ps6000aGetAnalogueOffsetLimits
_get_analogue_offset_limits.restype = c_uint32
_get_analogue_offset_limits.argtypes = [c_int16, c_uint32, c_uint32, c_void_p, c_void_p]


def get_analog_offset_limits(
	handle: PicoHandle, range_: PicoConnectProbeRange, coupling: PicoCoupling
) -> tuple[PicoStatus, float, float]:
	"""
	Get analog offset information (ps6000aGetAnalogueOffsetLimits).

	This function is used to get the maximum and minimum allowable analog offset
	for a specific voltage range.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param range_: The voltage range for which minimum and maximum voltages are
		required.
	:type range_: PicoConnectProbeRange
	:param coupling: The type of AC/DC/50 Ω coupling used.
	:type coupling: PicoCoupling
	:return: Status, then minimum offset voltage, then maximum offset voltage.
		Note that this order is the opposite of the C API argument order.
	:rtype: tuple[PicoStatus, float, float]
	"""
	maximum_voltage = c_double()
	minimum_voltage = c_double()
	status = PicoStatus(
		_get_analogue_offset_limits(
			handle, range_, coupling, byref(maximum_voltage), byref(minimum_voltage)
		)
	)
	return status, minimum_voltage.value, maximum_voltage.value


_get_minimum_timebase_stateless = _dll.ps6000aGetMinimumTimebaseStateless
_get_minimum_timebase_stateless.restype = c_uint32
_get_minimum_timebase_stateless.argtypes = [
	c_int16,
	c_uint32,
	c_void_p,
	c_void_p,
	c_uint32,
]


def get_minimum_timebase_stateless(
	handle: PicoHandle,
	enabled_channel_flags: PicoChannelFlags,
	resolution: PicoDeviceResolution,
) -> tuple[PicoStatus, int, float]:
	"""
	Find fastest available timebase (ps6000aGetMinimumTimebaseStateless).

	This function returns the shortest timebase that could be selected with a
	proposed configuration of the oscilloscope. It does not set the oscilloscope
	to the proposed configuration.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param enabled_channel_flags: A bit field indicating which channels are
		enabled in the proposed configuration. Channel A is bit 0 and so on.
	:type enabled_channel_flags: PicoChannelFlags
	:param resolution: The vertical resolution in the proposed configuration.
	:type resolution: PicoDeviceResolution
	:return: Status, then timebase, then time interval.

		**Timebase:**
		The number of the shortest timebase possible with the proposed
		configuration.

		**Time interval:**
		The sample period in seconds corresponding to the timebase.
	:rtype: tuple[PicoStatus, int, float]
	"""
	timebase = c_uint32()
	time_interval = c_double()
	status = PicoStatus(
		_get_minimum_timebase_stateless(
			handle,
			enabled_channel_flags,
			byref(timebase),
			byref(time_interval),
			resolution,
		)
	)
	return status, timebase.value, time_interval.value


_nearest_sample_interval_stateless = _dll.ps6000aNearestSampleIntervalStateless
_nearest_sample_interval_stateless.restype = c_uint32
_nearest_sample_interval_stateless.argtypes = [
	c_int16,
	c_uint32,
	c_double,
	c_uint32,
	c_void_p,
	c_void_p,
]


def nearest_sample_interval_stateless(
	handle: PicoHandle,
	enabled_channel_flags: PicoChannelFlags,
	time_interval_requested: float,
	resolution: PicoDeviceResolution,
) -> tuple[PicoStatus, int, float]:
	"""
	Get nearest sampling interval (ps6000aNearestSampleIntervalStateless).

	This function returns the nearest possible sample interval to the requested
	sample interval. It does not change the configuration of the oscilloscope.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param enabled_channel_flags: A bit field indicating which channels are
		enabled in the proposed configuration. Channel A is bit 0 and so on.
	:type enabled_channel_flags: PicoChannelFlags
	:param time_interval_requested: The time interval, in seconds, that you
		would like to obtain.
	:type time_interval_requested: double
	:param resolution: The vertical resolution for which the oscilloscope will
		be configured.
	:type resolution: PicoDeviceResolution
	:return: Status, then timebase, then time interval available.

		**Timebase:**
		The number of the nearest available timebase.

		**Time interval availble:**
		The nearest available time interval, in seconds.
	:rtype: tuple[PicoStatus, int, float]
	"""
	timebase = c_uint32()
	time_interval_available = c_double()
	status = PicoStatus(
		_nearest_sample_interval_stateless(
			handle,
			enabled_channel_flags,
			time_interval_requested,
			resolution,
			byref(timebase),
			byref(time_interval_available),
		)
	)
	return status, timebase.value, time_interval_available.value


_set_device_resolution = _dll.ps6000aSetDeviceResolution
_set_device_resolution.restype = c_uint32
_set_device_resolution.argtypes = [c_int16, c_uint32]


def set_device_resolution(
	handle: PicoHandle, resolution: PicoDeviceResolution
) -> PicoStatus:
	"""
	Set the hardware resolution (ps6000aSetDeviceResolution).

	This function sets the sampling resolution of the device. At 10-bit and
	higher resolutions, the maximum capture buffer length is half that of 8-bit
	mode. When using 12-bit resolution only 2 channels can be enabled to capture
	data.

	When you change the device resolution, the driver discards all previously
	captured data.

	After changing the resolution and before calling ``run_block`` or
	``run_streaming``, call ``set_channel_on`` to set up the input channels.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param resolution: Determines the resolution of the device when opened.
	:type resolution: PicoDeviceResolution
	:return: Status.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_device_resolution(handle, resolution))


_get_device_resolution = _dll.ps6000aGetDeviceResolution
_get_device_resolution.restype = c_uint32
_get_device_resolution.argtypes = [c_int16, c_void_p]


def get_device_resolution(
	handle: PicoHandle,
) -> tuple[PicoStatus, PicoDeviceResolution]:
	"""
	Retrieve the device resolution (ps6000aGetDeviceResolution).

	This function retrieves the vertical resolution of the oscilloscope.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Status, and the resolution of the device.
	:rtype: tuple[PicoStatus, PicoDeviceResolution]
	"""
	resolution = c_uint32()
	status = PicoStatus(_get_device_resolution(handle, byref(resolution)))
	return status, PicoDeviceResolution(resolution.value)


_get_scaling_values = _dll.ps6000aGetScalingValues
_get_scaling_values.restype = c_uint32
_get_scaling_values.argtypes = [c_int16, c_void_p, c_int16]


def get_scaling_values(
	handle: PicoHandle, scaling_values: Sequence[PicoScalingFactorsValues]
) -> PicoStatus:
	"""
	Call ps6000aGetScalingValues (no documentation available).

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param scaling_values: Sequence of ``PicoScalingFactorsValues`` structures
		to be updated with scaling factor information. Probably the ``channel``
		member needs to be set beforehand, then the rest are set by the driver.
	:type scaling_values: Sequence[PicoScalingFactorsValues]
	:return: Status. ``scaling_values`` is updated by the driver.
	:rtype: PicoStatus
	"""
	scaling_values_count = len(scaling_values)
	scaling_values_array = (PicoScalingFactorsValues * scaling_values_count)(
		*scaling_values
	)
	scaling_values_ptr = c_cast(addressof(scaling_values_array), c_void_p)
	return PicoStatus(
		_get_scaling_values(handle, scaling_values_ptr, scaling_values_count)
	)


_get_adc_limits = _dll.ps6000aGetAdcLimits
_get_adc_limits.restype = c_uint32
_get_adc_limits.argtypes = [c_int16, c_uint32, c_void_p, c_void_p]


def get_adc_limits(
	handle: PicoHandle, resolution: PicoDeviceResolution
) -> tuple[PicoStatus, int, int]:
	"""
	Get min and max sample values (ps6000aGetAdcLimits).

	This function gets the maximum and minimum sample values that the ADC can
	produce at a given resolution.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param resolution: The vertical resolution about which you require
		information.
	:type resolution: PicoDeviceResolution
	:return: Status, then minimum sample value, then maximum sample value.
	:rtype: tuple[PicoStatus, int, int]
	"""
	min_value = c_int16()
	max_value = c_int16()
	status = PicoStatus(
		_get_adc_limits(handle, resolution, byref(min_value), byref(max_value))
	)
	return status, min_value.value, max_value.value


def run_block(
	handle: PicoHandle,
	no_of_pre_trigger_samples: int,
	no_of_post_trigger_samples: int,
	timebase: int,
	segment_index: int,
	cb_ready: Optional[BlockReadyCType] = None,
	cb_parameter: Optional[c_void_p] = None,
) -> tuple[PicoStatus, float]:
	"""
	Start collecting data in block mode.

	For a step-by-step guide to this process, see `Using block mode`_.

	The number of samples is determined by ``noOfPreTriggerSamples`` and
	``noOfPostTriggerSamples`` (see below for details). The total number of
	samples must not be more than the size of the segment referred to by
	``segmentIndex``.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param no_of_pre_trigger_samples: The number of samples to return before the
		trigger event. If no trigger has been set, then this argument is added
		to ``noOfPostTriggerSamples`` to give the maximum number of data points
		(samples) to collect.
	:type no_of_pre_trigger_samples: int
	:param no_of_post_trigger_samples: The number of samples to return after the
		trigger event. If no trigger event has been set, then this argument is
		added to ``noOfPreTriggerSamples`` to give the maximum number of data
		points to collect. If a trigger condition has been set, this specifies
		the number of data points to collect after a trigger has fired, and the
		number of samples to be collected is:
		``noOfPreTriggerSamples + noOfPostTriggerSamples``
	:type no_of_post_trigger_samples: int
	:param timebase: A number in the range 0 to 0xFFFF_FFFF. See the guide to
		calculating timebase values.
	:type timebase: int (uint32_t)
	:param segment_index: Zero-based, specifies which memory segment to use.
	:type segment_index: int
	:param cb_ready: A pointer to the ``ps6000aBlockReady()`` callback function
		that the driver will call when the data has been collected. To use the
		``ps6000aIsReady()`` polling method instead of a callback function, set
		this pointer to NULL.
	:type cb_ready: BlockReadyCType
	:param cb_parameter: A void pointer that is passed to the
		``ps6000aBlockReady()`` callback function. The callback can
		use this pointer to return arbitrary data to the application.
	:type cb_parameter: void*
	:return: Tuple of:

		- Status.
		- The time in milliseconds that the scope will spend collecting samples.

	:rtype: Tuple[PicoStatus, float]
	"""
	time_indisposed_ms = c_double()
	status = PicoStatus(
		_run_block(
			handle,
			no_of_pre_trigger_samples,
			no_of_post_trigger_samples,
			timebase,
			byref(time_indisposed_ms),
			segment_index,
			cb_ready,
			cb_parameter,
		)
	)
	return status, time_indisposed_ms.value


_is_ready = _dll.ps6000aIsReady
_is_ready.restype = c_uint32
_is_ready.argtypes = [c_int16, c_void_p]


def is_ready(handle: PicoHandle) -> tuple[PicoStatus, bool]:
	"""
	Check if the device has finished collecting the requested samples.

	This function may be used instead of a callback function to receive data
	from ``ps6000aRunBlock()``. To use this method, pass a NULL pointer as the
	lpReady argument to ``ps6000aRunBlock()``. You must then poll the driver to
	see if it has finished collecting the requested samples.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:return: Tuple of:

		- Status.
		- Indicates the state of collection. If zero, the device is still
		collecting. If non-zero, the device has finished collecting and
		``ps6000aGetValues()`` can be used to retrieve the data.

	:rtype: Tuple[PicoStatus, bool]
	"""
	ready = c_int16()
	status = PicoStatus(_is_ready(handle, byref(ready)))
	return status, bool(ready.value)


_get_values = _dll.ps6000aGetValues
_get_values.restype = c_uint32
_get_values.argtypes = [
	c_int16,
	c_uint64,
	c_void_p,
	c_uint64,
	c_uint32,
	c_uint64,
	c_void_p,
]


def get_values(
	handle: PicoHandle,
	start_index: int,
	no_of_samples: int,
	down_sample_ratio: int,
	down_sample_ratio_mode: PicoRatioMode,
	segment_index: int,
) -> tuple[PicoStatus, int, PicoChannelFlags]:
	"""
	Retrieve block-mode data.

	This function retrieves block-mode data, either with or without
	downsampling, starting at the specified sample number. It is used to get
	the stored data from the scope after data collection has stopped, and
	store it in a user buffer previously passed to ``ps6000aSetDataBuffer()``
	or ``ps6000aSetDataBuffers()``. It blocks the calling function while
	retrieving data.

	:param handle: The device identifier returned by ``open_unit``.
	:type handle: PicoHandle
	:param start_index: A zero-based index that indicates the start point for
		data collection. It is measured in sample intervals from the start of
		the buffer.
	:type start_index: int
	:param no_of_samples: The number of raw samples to be processed. The number
		of samples retrieved will not be more than the number requested, and the
		data retrieved always starts with the first sample captured.
	:type no_of_samples: int
	:param down_sample_ratio: The downsampling factor that will be applied to
		the raw data. Must be greater than zero.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: Which downsampling mode to use.
	:type down_sample_ratio_mode: PicoRatioMode
	:param segment_index: The zero-based number of the memory segment where the
		data is stored.
	:type segment_index: int
	:return: Tuple of:

		- Status.
		- The actual number of raw samples retrieved.
		- A set of flags that indicate whether an overvoltage has occurred on
		any of the channels.

	:rtype: Tuple[PicoStatus, int, PicoChannelFlags]
	"""
	c_no_of_samples = c_uint64(no_of_samples)
	overflow = c_int16()
	status = PicoStatus(
		_get_values(
			handle,
			start_index,
			byref(c_no_of_samples),
			down_sample_ratio,
			down_sample_ratio_mode,
			segment_index,
			byref(overflow),
		)
	)
	return status, c_no_of_samples.value, PicoChannelFlags(overflow.value)


# Functions below this line are not planned to be "Pythonized".
# Actually, I'd like to do the rest of the block mode stuff at some point.
# But don't hold your breath for the signal generator.

_get_accessory_info = _dll.ps6000aGetAccessoryInfo
_get_accessory_info.restype = c_uint32
_get_accessory_info.argtypes = [
	c_int16,
	c_uint32,
	c_char_p,
	c_int16,
	c_void_p,
	c_uint16,
]


def get_accessory_info(
	handle: PicoHandle,
	channel: int,
	string: c_char_p,
	string_length: int,
	required_size: c_void_p,
	info: int,
) -> PicoStatus:
	"""
	Call ps6000aGetAccessoryInfo (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param channel: (PICO_CHANNEL)channel.
	:type channel: int
	:param string: (int8_t*)string.
	:type string: c_char_p
	:param string_length: (int16_t)stringLength.
	:type string_length: int
	:param required_size: (int16_t*)requiredSize.
	:type required_size: c_void_p
	:param info: (PICO_INFO)info.
	:type required_size: int
	:return: (ps6000aGetAccessoryInfo) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_accessory_info(handle, channel, string, string_length, required_size, info)
	)


_sig_gen_waveform = _dll.ps6000aSigGenWaveform
_sig_gen_waveform.restype = c_uint32
_sig_gen_waveform.argtypes = [c_int16, c_uint32, c_void_p, c_uint16]


def sig_gen_waveform(
	handle: PicoHandle, wavetype: int, buffer: c_void_p, buffer_length: int
) -> PicoStatus:
	"""
	Call ps6000aSigGenWaveform (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param wavetype: (PICO_WAVE_TYPE)wavetype.
	:type wavetype: PicoWaveType
	:param buffer: (int16_t*)buffer.
	:type buffer: int
	:param buffer_length: (uint16)bufferLength.
	:type buffer_length: int
	:return: (ps6000aSigGenWaveform) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_waveform(handle, wavetype, buffer, buffer_length))


_sig_gen_range = _dll.ps6000aSigGenRange
_sig_gen_range.restype = c_uint32
_sig_gen_range.argtypes = [c_int16, c_double, c_double]


def sig_gen_range(
	handle: PicoHandle, peak_to_peak_volts: float, offset_volts: float
) -> PicoStatus:
	"""
	Call ps6000aSignGenRange (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param peak_to_peak_volts: (double)peakToPeakVolts.
	:type peak_to_peak_volts: double
	:param offset_volts: (double)offsetVolts.
	:type offset_volts: double
	:return: (ps6000aSignGenRange) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_range(handle, peak_to_peak_volts, offset_volts))


_sig_gen_waveform_duty_cycle = _dll.ps6000aSigGenWaveformDutyCycle
_sig_gen_waveform_duty_cycle.restype = c_uint32
_sig_gen_waveform_duty_cycle.argtypes = [c_int16, c_double]


def sig_gen_waveform_duty_cycle(
	handle: PicoHandle, duty_cycle_percent: float
) -> PicoStatus:
	"""
	Call ps6000aSigGenWaveformDutyCycle (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param duty_cycle_percent: (double)dutyCyclePercent.
	:type duty_cycle_percent: double
	:return: (ps6000aSigGenWaveformDutyCycle) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_waveform_duty_cycle(handle, duty_cycle_percent))


_sig_gen_trigger = _dll.ps6000aSigGenTrigger
_sig_gen_trigger.restype = c_uint32
_sig_gen_trigger.argtypes = [c_int16, c_uint32, c_uint32, c_uint64, c_uint64]


def sig_gen_trigger(
	handle: PicoHandle,
	trigger_type: int,
	trigger_source: int,
	cycles: int,
	auto_trigger_pico_seconds: int,
) -> PicoStatus:
	"""
	Call ps6000aSigGenTrigger (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param trigger_type: (PICO_SIGGEN_TRIG_TYPE)triggerType.
	:type trigger_type: PicoSiggenTrigType
	:param trigger_source: (PICO_SIGGEN_TRIG_SOURCE)triggerSource.
	:type trigger_source: PicoSiggenTrigSource
	:param cycles: (uint64_t)cycles.
	:type cycles: int
	:param auto_trigger_pico_seconds: (uint64_t)autoTriggerPicoSeconds.
	:type auto_trigger_pico_seconds: int
	:return: (ps6000aSigGenTrigger) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_trigger(
			handle, trigger_type, trigger_source, cycles, auto_trigger_pico_seconds
		)
	)


_sig_gen_filter = _dll.ps6000aSigGenFilter
_sig_gen_filter.restype = c_uint32
_sig_gen_filter.argtypes = [c_int16, c_uint32]


def sig_gen_filter(handle: PicoHandle, filter_state: int) -> PicoStatus:
	"""
	Call ps6000aSigGenFilter (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param filter_state: (PICO_SIGGEN_FILTER_STATE)filterState.
	:type filter_state: PicoSiggenFilterState
	:return: (ps6000aSigGenFilter) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_filter(handle, filter_state))


_sig_gen_frequency = _dll.ps6000aSigGenFrequency
_sig_gen_frequency.restype = c_uint32
_sig_gen_frequency.argtypes = [c_int16, c_double]


def sig_gen_frequency(handle: PicoHandle, frequency_hz: float) -> PicoStatus:
	"""
	Call ps6000aSigGenFrequency (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param frequency_hz: (double)frequencyHz.
	:type frequency_hz: double
	:return: (ps6000aSigGenFrequency) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_frequency(handle, frequency_hz))


_sig_gen_frequency_sweep = _dll.ps6000aSigGenFrequencySweep
_sig_gen_frequency_sweep.restype = c_uint32
_sig_gen_frequency_sweep.argtypes = [c_int16, c_double, c_double, c_double, c_uint32]


def sig_gen_frequency_sweep(
	handle: PicoHandle,
	stop_frequency_hz: float,
	frequency_increment: float,
	dwell_time_seconds: float,
	sweep_type: int,
) -> PicoStatus:
	"""
	Call ps6000aSigGenFrequencySweep (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param stop_frequency_hz: (double)stopFrequencyHz.
	:type stop_frequency_hz: double
	:param frequency_increment: (double)frequencyIncrement.
	:type frequency_increment: double
	:param dwell_time_seconds: (double)dwellTimeSeconds.
	:type dwell_time_seconds: double
	:param sweep_type: (PICO_SWEEP_TYPE)sweepType.
	:type sweep_type: PicoSweepType
	:return: (ps6000aSigGenFrequencySweep) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_frequency_sweep(
			handle,
			stop_frequency_hz,
			frequency_increment,
			dwell_time_seconds,
			sweep_type,
		)
	)


_sig_gen_phase = _dll.ps6000aSigGenPhase
_sig_gen_phase.restype = c_uint32
_sig_gen_phase.argtypes = [c_int16, c_uint64]


def sig_gen_phase(handle: PicoHandle, delta_phase: int) -> PicoStatus:
	"""
	Call ps6000aSigGenPhase (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param delta_phase: (uint64_t)deltaPhase.
	:type delta_phase: int
	:return: (ps6000aSigGenPhase) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_phase(handle, delta_phase))


_sig_gen_phase_sweep = _dll.ps6000aSigGenPhaseSweep
_sig_gen_phase_sweep.restype = c_uint32
_sig_gen_phase_sweep.argtypes = [c_int16, c_uint64, c_uint64, c_uint64, c_uint32]


def sig_gen_phase_sweep(
	handle: PicoHandle,
	stop_delta_phase: int,
	delta_phase_increment: int,
	dwell_count: int,
	sweep_type: int,
) -> PicoStatus:
	"""
	Call ps6000aSigGenPhaseSweep (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param stop_delta_phase: (uint64_t)stopDeltaPhase.
	:type stop_delta_phase: int
	:param delta_phase_increment: (uint64_t)deltaPhaseIncrement.
	:type delta_phase_increment: int
	:param dwell_count: (uint64_t)dwellCount.
	:type dwell_count: int
	:param sweep_type: (PICO_SWEEP_TYPE)sweepType.
	:type sweep_type: PicoSweepType
	:return: (ps6000aSigGenPhaseSweep) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_phase_sweep(
			handle, stop_delta_phase, delta_phase_increment, dwell_count, sweep_type
		)
	)


_sig_gen_clock_manual = _dll.ps6000aSigGenClockManual
_sig_gen_clock_manual.restype = c_uint32
_sig_gen_clock_manual.argtypes = [c_int16, c_double, c_uint64]


def sig_gen_clock_manual(
	handle: PicoHandle, dac_clock_frequency: float, prescale_ratio: int
) -> PicoStatus:
	"""
	Call ps6000aSigGenClockManual (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param dac_clock_frequency: (double)dacClockFrequency.
	:type dac_clock_frequency: double
	:param prescale_ratio: (uint64_t)prescaleRatio.
	:type prescale_ratio: int
	:return: (ps6000aSigGenClockManual) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_clock_manual(handle, dac_clock_frequency, prescale_ratio)
	)


_sig_gen_software_trigger_control = _dll.ps6000aSigGenSoftwareTriggerControl
_sig_gen_software_trigger_control.restype = c_uint32
_sig_gen_software_trigger_control.argtypes = [c_int16, c_uint32]


def sig_gen_software_trigger_control(
	handle: PicoHandle, trigger_state: int
) -> PicoStatus:
	"""
	Call ps6000aSigGenSoftwareTriggerControl (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param trigger_state: (PICO_SIGGEN_TRIG_TYPE)triggerState.
	:type trigger_state: PicoSiggenTrigType
	:return: (ps6000aSigGenSoftwareTriggerControl) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_software_trigger_control(handle, trigger_state))


_sig_gen_apply = _dll.ps6000aSigGenApply
_sig_gen_apply.restype = c_uint32
_sig_gen_apply.argtypes = [
	c_int16,
	c_int16,
	c_int16,
	c_int16,
	c_int16,
	c_int16,
	c_void_p,
	c_void_p,
	c_void_p,
	c_void_p,
]


def sig_gen_apply(
	handle: PicoHandle,
	sig_gen_enabled: int,
	sweep_enabled: int,
	trigger_enabled: int,
	automatic_clock_optimisation_enabled: int,
	override_automatic_clock_and_prescale: int,
	frequency: c_void_p,
	stop_frequency: c_void_p,
	frequency_increment: c_void_p,
	dwell_time: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aSigGenApply (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param sig_gen_enabled: (int16_t)sigGenEnabled.
	:type sig_gen_enabled: int
	:param sweep_enabled: (int16_t)sweepEnabled.
	:type sweep_enabled: int
	:param trigger_enabled: (int16_t)triggerEnabled.
	:type trigger_enabled: int
	:param automatic_clock_optimisation_enabled: (int16_t)automaticClockOptimisationEnabled.
	:type automatic_clock_optimisation_enabled: int
	:param override_automatic_clock_and_prescale: (int16_t)overrideAutomaticClockAndPrescale.
	:type override_automatic_clock_and_prescale: int
	:param frequency: (double*)frequency.
	:type frequency: double*
	:param stop_frequency: (double*)stopFrequency.
	:type stop_frequency: double*
	:param frequency_increment: (double*)frequencyIncrement.
	:type frequency_increment: double*
	:param dwell_time: (double*)dwellTime.
	:type dwell_time: double*
	:return: (ps6000aSigGenApply) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_apply(
			handle,
			sig_gen_enabled,
			sweep_enabled,
			trigger_enabled,
			automatic_clock_optimisation_enabled,
			override_automatic_clock_and_prescale,
			frequency,
			stop_frequency,
			frequency_increment,
			dwell_time,
		)
	)


_sig_gen_limits = _dll.ps6000aSigGenLimits
_sig_gen_limits.restype = c_uint32
_sig_gen_limits.argtypes = [c_int16, c_uint32, c_double, c_double, c_double]


def sig_gen_limits(
	handle: PicoHandle,
	parameter: int,
	minimum_permissible_value: float,
	maximum_permissible_value: float,
	step: float,
) -> PicoStatus:
	"""
	Call ps6000aSigGenLimits (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param parameter: (PICO_SIGGEN_PARAMETER)parameter.
	:type parameter: PicoSiggenParameter
	:param minimum_permissible_value: (double*)minimumPermissibleValue.
	:type minimum_permissible_value: double*
	:param maximum_permissible_value: (double*)maximumPermissibleValue.
	:type maximum_permissible_value: double*
	:param step: (double*)step.
	:type step: double*
	:return: (ps6000aSigGenLimits) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_limits(
			handle,
			parameter,
			minimum_permissible_value,
			maximum_permissible_value,
			step,
		)
	)


_sig_gen_frequency_limits = _dll.ps6000aSigGenFrequencyLimits
_sig_gen_frequency_limits.restype = c_uint32
_sig_gen_frequency_limits.argtypes = [
	c_int16,
	c_uint32,
	c_void_p,
	c_void_p,
	c_int16,
	c_void_p,
	c_void_p,
	c_void_p,
	c_void_p,
	c_void_p,
	c_void_p,
	c_void_p,
]


def sig_gen_frequency_limits(
	handle: PicoHandle,
	wave_type: int,
	num_samples: c_void_p,
	start_frequency: c_void_p,
	sweep_enabled: int,
	manual_dac_clock_frequency: c_void_p,
	manual_prescale_ratio: c_void_p,
	max_stop_frequency_out: c_void_p,
	min_frequency_step_out: c_void_p,
	max_frequency_step_out: c_void_p,
	min_dwell_time_out: c_void_p,
	max_dwell_time_out: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aSigGenFrequencyLimits (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param wave_type: (PICO_WAVE_TYPE)waveType.
	:type wave_type: PicoWaveType
	:param num_samples: (uint64_t*)numSamples.
	:type num_samples: int
	:param start_frequency: (double*)startFrequency.
	:type start_frequency: double*
	:param sweep_enabled: (int16_t)sweepEnabled.
	:type sweep_enabled: int
	:param manual_dac_clock_frequency: (double*)manualDacClockFrequency.
	:type manual_dac_clock_frequency: double*
	:param manual_prescale_ratio: (uint64_t*)manualPrescaleRatio.
	:type manual_prescale_ratio: int
	:param max_stop_frequency_out: (double*)maxStopFrequencyOut.
	:type max_stop_frequency_out: double*
	:param min_frequency_step_out: (double*)minFrequencyStepOut.
	:type min_frequency_step_out: double*
	:param max_frequency_step_out: (double*)maxFrequencyStepOut.
	:type max_frequency_step_out: double*
	:param min_dwell_time_out: (double*)minDwellTimeOut.
	:type min_dwell_time_out: double*
	:param max_dwell_time_out: (double*)maxDwellTimeOut.
	:type max_dwell_time_out: double*
	:return: (ps6000aSigGenFrequencyLimits) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_sig_gen_frequency_limits(
			handle,
			wave_type,
			num_samples,
			start_frequency,
			sweep_enabled,
			manual_dac_clock_frequency,
			manual_prescale_ratio,
			max_stop_frequency_out,
			min_frequency_step_out,
			max_frequency_step_out,
			min_dwell_time_out,
			max_dwell_time_out,
		)
	)


_sig_gen_pause = _dll.ps6000aSigGenPause
_sig_gen_pause.restype = c_uint32
_sig_gen_pause.argtypes = [c_int16]


def sig_gen_pause(handle: PicoHandle) -> PicoStatus:
	"""
	Call ps6000aSigGenPause (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:return: (ps6000aSigGenPause) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_pause(handle))


_sig_gen_restart = _dll.ps6000aSigGenRestart
_sig_gen_restart.restype = c_uint32
_sig_gen_restart.argtypes = [c_int16]


def sig_gen_restart(handle: PicoHandle) -> PicoStatus:
	"""
	Call ps6000aSigGenRestart (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:return: (ps6000aSigGenRestart) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_sig_gen_restart(handle))


_set_pulse_width_qualifier_properties = _dll.ps6000aSetPulseWidthQualifierProperties
_set_pulse_width_qualifier_properties.restype = c_uint32
_set_pulse_width_qualifier_properties.argtypes = [c_int16, c_uint32, c_uint32, c_uint32]


def set_pulse_width_qualifier_properties(
	handle: PicoHandle, lower: int, upper: int, type_: int
) -> PicoStatus:
	"""
	Call ps6000aSetPulseWidthQualifierProperties (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param lower: (uint32_t)lower.
	:type lower: int
	:param upper: (uint32_t)upper.
	:type upper: int
	:param type_: (PICO_PULSE_WIDTH_TYPE)type.
	:type type_: PicoPulseWidthType
	:return: (ps6000aSetPulseWidthQualifierProperties) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_pulse_width_qualifier_properties(handle, lower, upper, type_)
	)


_set_pulse_width_qualifier_conditions = _dll.ps6000aSetPulseWidthQualifierConditions
_set_pulse_width_qualifier_conditions.restype = c_uint32
_set_pulse_width_qualifier_conditions.argtypes = [c_int16, c_void_p, c_int16, c_uint32]


def set_pulse_width_qualifier_conditions(
	handle: PicoHandle, conditions: c_void_p, n_conditions: int, action: int
) -> PicoStatus:
	"""
	Call ps6000aSetPulseWidthQualifierConditions (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param conditions: (PICO_CONDITION*)conditions.
	:type conditions: PicoCondition*
	:param n_conditions: (int16_t)nConditions.
	:type n_conditions: int
	:param action: (PICO_ACTION)action.
	:type action: PicoAction
	:return: (ps6000aSetPulseWidthQualifierConditions) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_pulse_width_qualifier_conditions(handle, conditions, n_conditions, action)
	)


_set_pulse_width_qualifier_directions = _dll.ps6000aSetPulseWidthQualifierDirections
_set_pulse_width_qualifier_directions.restype = c_uint32
_set_pulse_width_qualifier_directions.argtypes = [c_int16, c_void_p, c_int16]


def set_pulse_width_qualifier_directions(
	handle: PicoHandle, directions: c_void_p, n_directions: int
) -> PicoStatus:
	"""
	Call ps6000aSetPulseWidthQualifierDirections (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param directions: (PICO_DIRECTION*)directions.
	:type directions: PicoDirection*
	:param n_directions: (int16_t)nDirections.
	:type n_directions: int
	:return: (ps6000aSetPulseWidthQualifierDirections) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_pulse_width_qualifier_directions(handle, directions, n_directions)
	)


_set_trigger_digital_port_properties = _dll.ps6000aSetTriggerDigitalPortProperties
_set_trigger_digital_port_properties.restype = c_uint32
_set_trigger_digital_port_properties.argtypes = [c_int16, c_uint32, c_void_p, c_int16]


def set_trigger_digital_port_properties(
	handle: PicoHandle, port: int, directions: c_void_p, n_directions: int
) -> PicoStatus:
	"""
	Call ps6000aSetTriggerDigitalPortProperties (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param port: (PICO_CHANNEL)port.
	:type port: PicoChannel
	:param directions: (PICO_DIGITAL_CHANNEL_DIRECTIONS*)directions.
	:type directions: PicoDigitalChannelDirections*
	:param n_directions: (int16_t)nDirections.
	:type n_directions: int
	:return: (ps6000aSetTriggerDigitalPortProperties) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_trigger_digital_port_properties(handle, port, directions, n_directions)
	)


_set_pulse_width_digital_port_properties = (
	_dll.ps6000aSetPulseWidthDigitalPortProperties
)
_set_pulse_width_digital_port_properties.restype = c_uint32
_set_pulse_width_digital_port_properties.argtypes = [
	c_int16,
	c_uint32,
	c_void_p,
	c_int16,
]


def set_pulse_width_digital_port_properties(
	handle: PicoHandle, port: int, directions: c_void_p, n_directions: int
) -> PicoStatus:
	"""
	Call ps6000aSetPulseWidthDigitalPortProperties (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param port: (PICO_CHANNEL)port.
	:type port: PicoChannel
	:param directions: (PICO_DIGITAL_CHANNEL_DIRECTIONS*)directions.
	:type directions: PicoDigitalChannelDirections*
	:param n_directions: (int16_t)nDirections.
	:type n_directions: int
	:return: (ps6000aSetPulseWidthDigitalPortProperties) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_set_pulse_width_digital_port_properties(handle, port, directions, n_directions)
	)


_get_trigger_time_offset = _dll.ps6000aGetTriggerTimeOffset
_get_trigger_time_offset.restype = c_uint32
_get_trigger_time_offset.argtypes = [c_int16, c_void_p, c_void_p, c_uint64]


def get_trigger_time_offset(
	handle: PicoHandle, time: c_void_p, time_units: c_void_p, segment_index: int
) -> PicoStatus:
	"""
	Call ps6000aGetTriggerTimeOffset (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param time: (int64_t*)time.
	:type time: int
	:param time_units: (PICO_TIME_UNITS*)timeUnits.
	:type time_units: PicoTimeUnits*
	:param segment_index: (uint64_t)segmentIndex.
	:type segment_index: int
	:return: (ps6000aGetTriggerTimeOffset) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_get_trigger_time_offset(handle, time, time_units, segment_index))


_get_values_trigger_time_offset_bulk = _dll.ps6000aGetValuesTriggerTimeOffsetBulk
_get_values_trigger_time_offset_bulk.restype = c_uint32
_get_values_trigger_time_offset_bulk.argtypes = [
	c_int16,
	c_void_p,
	c_void_p,
	c_uint64,
	c_uint64,
]


def get_values_trigger_time_offset_bulk(
	handle: PicoHandle,
	time: c_void_p,
	time_units: c_void_p,
	from_segement_index: int,
	to_segment_index: int,
) -> PicoStatus:
	"""
	Call ps6000aGetValuesTriggerTimeOffsetBulk (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param time: (int64_t*)time.
	:type time: int
	:param time_units: (PICO_TIME_UNITS*)timeUnits.
	:type time_units: PicoTimeUnits*
	:param from_segement_index: (uint64_t)fromSegementIndex.
	:type from_segement_index: int
	:param to_segment_index: (uint64_t)toSegmentIndex.
	:type to_segment_index: int
	:return: (ps6000aGetValuesTriggerTimeOffsetBulk) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_values_trigger_time_offset_bulk(
			handle, time, time_units, from_segement_index, to_segment_index
		)
	)


_run_block = _dll.ps6000aRunBlock
_run_block.restype = c_uint32
_run_block.argtypes = [
	c_int16,
	c_uint64,
	c_uint64,
	c_uint32,
	c_void_p,
	c_uint64,
	c_void_p,
	c_void_p,
]


_get_values_bulk = _dll.ps6000aGetValuesBulk
_get_values_bulk.restype = c_uint32
_get_values_bulk.argtypes = [
	c_int16,
	c_uint64,
	c_void_p,
	c_uint64,
	c_uint64,
	c_uint64,
	c_uint32,
	c_void_p,
]


def get_values_bulk(
	handle: PicoHandle,
	start_index: int,
	no_of_samples: c_void_p,
	from_segment_index: int,
	to_segment_index: int,
	down_sample_ratio: int,
	down_sample_ratio_mode: int,
	overflow: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aGetValuesBulk (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param start_index: (uint64_t)startIndex.
	:type start_index: int
	:param no_of_samples: (uint64_t*)noOfSamples.
	:type no_of_samples: int
	:param from_segment_index: (uint64_t)fromSegmentIndex.
	:type from_segment_index: int
	:param to_segment_index: (uint64_t)toSegmentIndex.
	:type to_segment_index: int
	:param down_sample_ratio: (uint64_t)downSampleRatio.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: (PICO_RATIO_MODE)downSampleRatioMode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param overflow: (int16_t*)overflow.
	:type overflow: int
	:return: (ps6000aGetValuesBulk) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_values_bulk(
			handle,
			start_index,
			no_of_samples,
			from_segment_index,
			to_segment_index,
			down_sample_ratio,
			down_sample_ratio_mode,
			overflow,
		)
	)


_get_values_async = _dll.ps6000aGetValuesAsync
_get_values_async.restype = c_uint32
_get_values_async.argtypes = [
	c_int16,
	c_uint64,
	c_uint64,
	c_uint64,
	c_uint32,
	c_uint64,
	c_void_p,
	c_void_p,
]


def get_values_async(
	handle: PicoHandle,
	start_index: int,
	no_of_samples: int,
	down_sample_ratio: int,
	down_sample_ratio_mode: int,
	segment_index: int,
	lp_data_ready: Union[DataReadyCType, PicoDataReadyUsingReadsCType],
	p_parameter: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aGetValuesAsync (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param start_index: (uint64_t)startIndex.
	:type start_index: int
	:param no_of_samples: (uint64_t)noOfSamples.
	:type no_of_samples: int
	:param down_sample_ratio: (uint64_t)downSampleRatio.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: (PICO_RATIO_MODE)downSampleRatioMode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param segment_index: (uint64_t)segmentIndex.
	:type segment_index: int
	:param lp_data_ready: (PICO_POINTER)lpDataReady.
	:type lp_data_ready: Union[DataReadyCType, PicoDataReadyUsingReadsCType]
	:param p_parameter: (PICO_POINTER)pParameter.
	:type p_parameter: PicoPointer
	:return: (ps6000aGetValuesAsync) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_values_async(
			handle,
			start_index,
			no_of_samples,
			down_sample_ratio,
			down_sample_ratio_mode,
			segment_index,
			lp_data_ready,
			p_parameter,
		)
	)


_get_values_bulk_async = _dll.ps6000aGetValuesBulkAsync
_get_values_bulk_async.restype = c_uint32
_get_values_bulk_async.argtypes = [
	c_int16,
	c_uint64,
	c_uint64,
	c_uint64,
	c_uint64,
	c_uint64,
	c_uint32,
	c_void_p,
	c_void_p,
]


def get_values_bulk_async(
	handle: PicoHandle,
	start_index: int,
	no_of_samples: int,
	from_segment_index: int,
	to_segment_index: int,
	down_sample_ratio: int,
	down_sample_ratio_mode: int,
	lp_data_ready: c_void_p,
	p_parameter: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aGetValuesBulkAsync (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param start_index: (uint64_t)startIndex.
	:type start_index: int
	:param no_of_samples: (uint64_t)noOfSamples.
	:type no_of_samples: int
	:param from_segment_index: (uint64_t)fromSegmentIndex.
	:type from_segment_index: int
	:param to_segment_index: (uint64_t)toSegmentIndex.
	:type to_segment_index: int
	:param down_sample_ratio: (uint64_t)downSampleRatio.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: (PICO_RATIO_MODE)downSampleRatioMode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param lp_data_ready: (PICO_POINTER)lpDataReady.
	:type lp_data_ready: PicoPointer
	:param p_parameter: (PICO_POINTER)pParameter.
	:type p_parameter: PicoPointer
	:return: (ps6000aGetValuesBulkAsync) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_values_bulk_async(
			handle,
			start_index,
			no_of_samples,
			from_segment_index,
			to_segment_index,
			down_sample_ratio,
			down_sample_ratio_mode,
			lp_data_ready,
			p_parameter,
		)
	)


_get_values_overlapped = _dll.ps6000aGetValuesOverlapped
_get_values_overlapped.restype = c_uint32
_get_values_overlapped.argtypes = [
	c_int16,
	c_uint64,
	c_void_p,
	c_uint64,
	c_uint32,
	c_uint64,
	c_uint64,
	c_void_p,
]


def get_values_overlapped(
	handle: PicoHandle,
	start_index: int,
	no_of_samples: c_void_p,
	down_sample_ratio: int,
	down_sample_ratio_mode: int,
	from_segement_index: int,
	to_segment_index: int,
	overflow: c_void_p,
) -> PicoStatus:
	"""
	Call ps6000aGetValuesOverlapped (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param start_index: (uint64_t)startIndex.
	:type start_index: int
	:param no_of_samples: (uint64_t*)noOfSamples.
	:type no_of_samples: int
	:param down_sample_ratio: (uint64_t)downSampleRatio.
	:type down_sample_ratio: int
	:param down_sample_ratio_mode: (PICO_RATIO_MODE)downSampleRatioMode.
	:type down_sample_ratio_mode: PicoRatioMode
	:param from_segement_index: (uint64_t)fromSegementIndex.
	:type from_segement_index: int
	:param to_segment_index: (uint64_t)toSegmentIndex.
	:type to_segment_index: int
	:param overflow: (int16_t*)overflow.
	:type overflow: int
	:return: (ps6000aGetValuesOverlapped) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_get_values_overlapped(
			handle,
			start_index,
			no_of_samples,
			down_sample_ratio,
			down_sample_ratio_mode,
			from_segement_index,
			to_segment_index,
			overflow,
		)
	)


_stop_using_get_values_overlapped = _dll.ps6000aStopUsingGetValuesOverlapped
_stop_using_get_values_overlapped.restype = c_uint32
_stop_using_get_values_overlapped.argtypes = [c_int16]


def stop_using_get_values_overlapped(handle: PicoHandle) -> PicoStatus:
	"""
	Call ps6000aStopUsingGetValuesOverlapped (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:return: (ps6000aStopUsingGetValuesOverlapped) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_stop_using_get_values_overlapped(handle))


_get_no_of_captures = _dll.ps6000aGetNoOfCaptures
_get_no_of_captures.restype = c_uint32
_get_no_of_captures.argtypes = [c_int16, c_void_p]


def get_no_of_captures(handle: PicoHandle, n_captures: c_void_p) -> PicoStatus:
	"""
	Call ps6000aGetNoOfCaptures (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param n_captures: (uint64_t*)nCaptures.
	:type n_captures: int
	:return: (ps6000aGetNoOfCaptures) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_get_no_of_captures(handle, n_captures))


_get_no_of_processed_captures = _dll.ps6000aGetNoOfProcessedCaptures
_get_no_of_processed_captures.restype = c_uint32
_get_no_of_processed_captures.argtypes = [c_int16, c_void_p]


def get_no_of_processed_captures(
	handle: PicoHandle, n_processed_captures: c_void_p
) -> PicoStatus:
	"""
	Call ps6000aGetNoOfProcessedCaptures (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param n_processed_captures: (uint64_t*)nProcessedCaptures.
	:type n_processed_captures: int
	:return: (ps6000aGetNoOfProcessedCaptures) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_get_no_of_processed_captures(handle, n_processed_captures))


_set_no_of_captures = _dll.ps6000aSetNoOfCaptures
_set_no_of_captures.restype = c_uint32
_set_no_of_captures.argtypes = [c_int16, c_uint64]


def set_no_of_captures(handle: PicoHandle, n_captures: int) -> PicoStatus:
	"""
	Call ps6000aSetNoOfCaptures (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param n_captures: (uint64_t)nCaptures.
	:type n_captures: int
	:return: (ps6000aSetNoOfCaptures) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_no_of_captures(handle, n_captures))


_query_output_edge_detect = _dll.ps6000aQueryOutputEdgeDetect
_query_output_edge_detect.restype = c_uint32
_query_output_edge_detect.argtypes = [c_int16, c_void_p]


def query_output_edge_detect(handle: PicoHandle, state: c_void_p) -> PicoStatus:
	"""
	Call ps6000aQueryOutputEdgeDetect (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param state: (int16_t*)state.
	:type state: int
	:return: (ps6000aQueryOutputEdgeDetect) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_query_output_edge_detect(handle, state))


_set_output_edge_detect = _dll.ps6000aSetOutputEdgeDetect
_set_output_edge_detect.restype = c_uint32
_set_output_edge_detect.argtypes = [c_int16, c_int16]


def set_output_edge_detect(handle: PicoHandle, state: int) -> PicoStatus:
	"""
	Call ps6000aSetOutputEdgeDetect (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param state: (int16_t)state.
	:type state: int
	:return: (ps6000aSetOutputEdgeDetect) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_output_edge_detect(handle, state))


_check_for_update = _dll.ps6000aCheckForUpdate
_check_for_update.restype = c_uint32
_check_for_update.argtypes = [c_int16, c_void_p, c_void_p, c_void_p]


def check_for_update(
	handle: PicoHandle, current: c_void_p, update: c_void_p, update_required: c_void_p
) -> PicoStatus:
	"""
	Call ps6000aCheckForUpdate (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param current: (PICO_VERSION*)current.
	:type current: PicoVersion*
	:param update: (PICO_VERSION*)update.
	:type update: PicoVersion*
	:param update_required: (uint16_t*)updateRequired.
	:type update_required: int
	:return: (ps6000aCheckForUpdate) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_check_for_update(handle, current, update, update_required))


_start_firmware_update = _dll.ps6000aStartFirmwareUpdate
_start_firmware_update.restype = c_uint32
_start_firmware_update.argtypes = [c_int16, c_void_p]


def start_firmware_update(
	handle: PicoHandle, progress: PicoUpdateFirmwareProgressCType
) -> PicoStatus:
	"""
	Call ps6000aStartFirmwareUpdate (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param progress: (PicoUpdateFirmwareProgress)progress.
	:type progress: PicoUpdateFirmwareProgressCType
	:return: (ps6000aStartFirmwareUpdate) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_start_firmware_update(handle, progress))


_reset_channels_and_report_all_channels_overvoltage_trip_status = (
	_dll.ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus
)
_reset_channels_and_report_all_channels_overvoltage_trip_status.restype = c_uint32
_reset_channels_and_report_all_channels_overvoltage_trip_status.argtypes = [
	c_int16,
	c_void_p,
	c_uint8,
]


def reset_channels_and_report_all_channels_overvoltage_trip_status(
	handle: PicoHandle,
	all_channels_tripped_status: c_void_p,
	n_channel_tripped_status: int,
) -> PicoStatus:
	"""
	Call ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param all_channels_tripped_status: (PICO_CHANNEL_OVERVOLTAGE_TRIPPED*)allChannelsTrippedStatus.
	:type all_channels_tripped_status: PicoChannelOvervoltageTripped
	:param n_channel_tripped_status: (uint8_t)nChannelTrippedStatus.
	:type n_channel_tripped_status: int
	:return: (ps6000aSetProbeInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_reset_channels_and_report_all_channels_overvoltage_trip_status(
			handle, all_channels_tripped_status, n_channel_tripped_status
		)
	)


_report_all_channels_overvoltage_trip_status = (
	_dll.ps6000aReportAllChannelsOvervoltageTripStatus
)
_report_all_channels_overvoltage_trip_status.restype = c_uint32
_report_all_channels_overvoltage_trip_status.argtypes = [c_int16, c_void_p, c_uint8]


def report_all_channels_overvoltage_trip_status(
	handle: PicoHandle,
	all_channels_tripped_status: c_void_p,
	n_channel_tripped_status: int,
) -> PicoStatus:
	"""
	Call ps6000aReportAllChannelsOvervoltageTripStatus (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param all_channels_tripped_status: (PICO_CHANNEL_OVERVOLTAGE_TRIPPED*)allChannelsTrippedStatus.
	:type all_channels_tripped_status: PicoChannelOvervoltageTripped
	:param n_channel_tripped_status: (uint8_t)nChannelTrippedStatus.
	:type n_channel_tripped_status: int
	:return: (ps6000aSetProbeInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_report_all_channels_overvoltage_trip_status(
			handle, all_channels_tripped_status, n_channel_tripped_status
		)
	)


_set_probe_interaction_callback = _dll.ps6000aSetDigitalPortInteractionCallback
_set_probe_interaction_callback.restype = c_uint32
_set_probe_interaction_callback.argtypes = [c_int16, c_void_p]


def set_digital_port_interaction_callback(
	handle: PicoHandle, callback: DigitalPortInteractionsCType
) -> PicoStatus:
	"""
	Call ps6000aSetDigitalPortInteractionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoDigitalPortInteractions)callback.
	:type callback: DigitalPortInteractionsCType
	:return: (ps6000aSetProbeInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_probe_interaction_callback(handle, callback))


_set_probe_interaction_callback = _dll.ps6000aSetProbeInteractionCallback
_set_probe_interaction_callback.restype = c_uint32
_set_probe_interaction_callback.argtypes = [c_int16, c_void_p]


def set_probe_interaction_callback(
	handle: PicoHandle, callback: PicoProbeInteractionsCType
) -> PicoStatus:
	"""
	Call ps6000aSetProbeInteractionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoProbeInteractions)callback.
	:type callback: PicoProbeInteractionsCType
	:return: (ps6000aSetProbeInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_probe_interaction_callback(handle, callback))


_set_external_reference_interaction_callback = (
	_dll.ps6000aSetExternalReferenceInteractionCallback
)
_set_external_reference_interaction_callback.restype = c_uint32
_set_external_reference_interaction_callback.argtypes = [c_int16, c_void_p]


def set_external_reference_interaction_callback(
	handle: PicoHandle, callback: PicoExternalReferenceInteractionsCType
) -> PicoStatus:
	"""
	Call ps6000aSetExternalReferenceInteractionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoExternalReferenceInteractions)callback.
	:type callback: PicoExternalReferenceInteractionsCType
	:return: (ps6000aSetExternalReferenceInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_external_reference_interaction_callback(handle, callback))


_set_awg_overrange_interaction_callback = _dll.ps6000aSetAWGOverrangeInteractionCallback
_set_awg_overrange_interaction_callback.restype = c_uint32
_set_awg_overrange_interaction_callback.argtypes = [c_int16, c_void_p]


def set_awg_overrange_interaction_callback(
	handle: PicoHandle, callback: PicoAWGOverrangeInteractionsCType
) -> PicoStatus:
	"""
	Call ps6000aSetAWGOverrangeInteractionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoAWGOverrangeInteractions)callback.
	:type callback: PicoAWGOverrangeInteractionsCType
	:return: (ps6000aSetAWGOverrangeInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_awg_overrange_interaction_callback(handle, callback))


_set_temperature_sensor_interaction_callback = (
	_dll.ps6000aSetTemperatureSensorInteractionCallback
)
_set_temperature_sensor_interaction_callback.restype = c_uint32
_set_temperature_sensor_interaction_callback.argtypes = [c_int16, c_void_p]


def set_temperature_sensor_interaction_callback(
	handle: PicoHandle, callback: PicoTemperatureSensorInteractionsCType
) -> PicoStatus:
	"""
	Call ps6000aSetTemperatureSensorInteractionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoTemperatureSensorInteractions)callback.
	:type callback: PicoTemperatureSensorInteractionsCType
	:return: (ps6000aSetTemperatureSensorInteractionCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_temperature_sensor_interaction_callback(handle, callback))


_set_probe_user_action_callback = _dll.ps6000aSetProbeUserActionCallback
_set_probe_user_action_callback.restype = c_uint32
_set_probe_user_action_callback.argtypes = [c_int16, c_void_p, c_void_p]


def set_probe_user_action_callback(
	handle: PicoHandle, callback: PicoProbeUserActionCType, p_parameter: c_void_p
) -> PicoStatus:
	"""
	Call ps6000aSetProbeUserActionCallback (no documentation available).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param callback: (PicoTemperatureSensorInteractions)callback.
	:type callback: PicoProbeUserActionCType
	:param p_parameter: (PICO_POINTER)pParameter.
	:type p_parameter: PicoPointer
	:return: (ps6000aSetTemperatureSensorInteractioNCallback) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(_set_probe_user_action_callback(handle, callback, p_parameter))


_channel_combinations_stateless = _dll.ps6000aChannelCombinationsStateless
_channel_combinations_stateless.restype = c_uint32
_channel_combinations_stateless.argtypes = [
	c_int16,
	c_void_p,
	c_void_p,
	c_uint32,
	c_uint32,
]


def channel_combinations_stateless(
	handle: PicoHandle,
	channel_flags_combinations: c_void_p,
	n_channel_combinations: c_void_p,
	resolution: int,
	timebase: int,
) -> PicoStatus:
	"""
	Call ps6000aChannelCombinationsStateless (autogenerated documentation).

	:param handle: (int16_t)handle.
	:type handle: PicoHandle
	:param channel_flags_combinations: (PICO_CHANNEL_FLAGS*)channelFlagsCombinations.
	:type channel_flags_combinations: PicoChannelFlags*
	:param n_channel_combinations: (uint32_t*)nChannelCombinations.
	:type n_channel_combinations: int
	:param resolution: (PICO_DEVICE_RESOLUTION)resolution.
	:type resolution: PicoDeviceResolution
	:param timebase: (uint32_t)timebase.
	:type timebase: int
	:return: (ps6000aChannelCombinationsStateless) result.
	:rtype: PicoStatus
	"""
	return PicoStatus(
		_channel_combinations_stateless(
			handle,
			channel_flags_combinations,
			n_channel_combinations,
			resolution,
			timebase,
		)
	)
