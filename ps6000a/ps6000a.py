"""Mid-level PicoScope 6000E driver interface."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: ps6000a.py
#
# Mid-level PicoScope 6000E driver interface.
#
# Encapsulates handle and exception management but does not automate top-level
# acquisition flows.
#
# Documentation Excerpts Copyright 2018-2019 Pico Technology Ltd.
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210818       Created.                                       jrowley
#   20240314       Added minimal API for block mode.              jrowley
#
###############################################################################

from collections import defaultdict
from ctypes import Array
import logging
from typing import Any, Optional, Sequence

from ps6000a.buffers import Buffer, BufferClass, BufferMaxMin
from ps6000a.callbacks import BlockReadyCallback, wrap_block_ready
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
from ps6000a.exceptions import PicoHandleError, PicoStatusError
import ps6000a.functions as ll
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

logger = logging.getLogger(__name__)


class PS6000A:
	"""
	Mid-level PicoScope 6000E driver interface.

	Encapsulates handle and exception management but does not automate top-level
	acquisition flows.

	:ivar raw_handle: The currently-held handle, if any, which may be invalid.
	:type raw_handle: Optional[PicoHandle]
	:ivar last_status: The status result of the last run method. Defaults
		to ``PicoStatus.NOT_YET_RUN`` at initialization.
	:type last_status: PicoStatus
	"""

	raw_handle: Optional[PicoHandle]
	last_status: PicoStatus
	buffers: dict[BufferClass, set[Buffer]]

	def __init__(self) -> None:
		"""
		Initialize PS6000A object.

		Note that this will NOT open any hardware. Call ``open_unit`` or use
		async opening flow before calling any non-static functions.
		"""
		self.raw_handle: Optional[PicoHandle] = None
		self.last_status: PicoStatus = PicoStatus.NOT_YET_RUN
		self.buffers: dict[BufferClass, set[Buffer]] = defaultdict(set)

	@property
	def handle(self) -> PicoHandle:
		"""
		Get handle to hardware device.

		:return: Valid handle.
		:rtype: PicoHandle
		:raise PicoHandleException: Will raise if no handle is held or the
			currently held handle is invalid.
		"""
		if self.raw_handle is not None and self.raw_handle.valid:
			return self.raw_handle
		else:
			raise PicoHandleError(self.raw_handle)

	def _verify_status(self, status: PicoStatus) -> None:
		"""
		Verify that supplied status is OK.

		If it's not, raise an exception.
		Will update ``last_status`` field.

		:param status: The status code to check.
		:type status: PicoStatus
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if ``status`` is not
			``PicoStatus.OK``.
		"""
		self.last_status = status
		if status != PicoStatus.OK:
			raise PicoStatusError(status)

	def open_unit(
		self, serial: Optional[str], resolution: PicoDeviceResolution
	) -> bool:
		"""
		Open a scope device (ps6000aOpenUnit).

		This function opens a PicoScope 6000E Series scope attached to the
		computer. The maximum number of units that can be opened depends on the
		operating system, the kernel driver and the computer.

		:param serial: A string containing the serial number of the scope to be
			opened. Optional. If None, then the function opens the first scope
			found; otherwise, it tries to open the scope that matches the
			string.
		:type serial: Optional[str]
		:param resolution: The required vertical resolution.
		:type resolution: PicoDeviceResolution
		:return: True if valid handle was returned, False otherwise. The handle
			will be stored with this object either way.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		if self.raw_handle is not None and self.raw_handle.valid:
			logger.warning("open_unit called while a unit is already open.")
			self.close_unit()
		status, handle = ll.open_unit(serial, resolution)
		self._verify_status(status)
		self.raw_handle = handle
		return handle.valid

	def open_unit_async(
		self, serial: Optional[str], resolution: PicoDeviceResolution
	) -> bool:
		"""
		Open unit without blocking (ps6000aOpenUnitAsync).

		This function opens a scope without blocking the calling thread. You
		can find out when it has finished by periodically calling
		``open_unit_progress`` until that function indicates the operation is
		complete.

		:param serial: A string containing the serial number of the scope to be
			opened. Optional. If None, then the function opens the first scope
			found; otherwise, it tries to open the scope that matches the
			string.
		:type serial: Optional[str]
		:param resolution: The required vertical resolution.
		:type resolution: PicoDeviceResolution
		:return: Opening status: False if the open operation was disallowed
			because another open operation is in progress or True if the open
			operation was successfully started.
		:rtype: bool
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		if self.raw_handle is not None and self.raw_handle.valid:
			logger.warning("open_unit_async called while a unit is already open.")
		status, status2 = ll.open_unit_async(serial, resolution)
		self._verify_status(status)
		return status2

	def open_unit_progress(self) -> bool:
		"""
		Get status of opening a unit (ps6000aOpenUnitProgress).

		This function checks on the progress of a request made to
		``open_unit_async`` to open a scope.

		:return: True if valid handle was returned, False otherwise (including
			if opening operation is not completed yet). The handle will be
			stored with this object if operation is complete, even if not valid.
		:rtype: bool
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		if self.raw_handle is not None and self.raw_handle.valid:
			logger.warning("open_unit_progress called while a unit is already open.")
			self.close_unit()
		status, handle, progress, complete = ll.open_unit_progress()
		self._verify_status(status)
		if complete:
			self.raw_handle = handle
		return complete and handle.valid

	@staticmethod
	def enumerate_units(parameters: str = "-v:-c:-h:-u:-f") -> tuple[int, str]:
		"""
		Get a list of unopened units (ps6000aEnumerateUnits).

		This function counts the number of PicoScope 6000 (A API) units
		connected to the computer, and returns a list of serial numbers and
		other optional information as a string. Note that this function can
		only detect devices that are not yet being controlled by an
		application. To query opened devices, use ``get_unit_info``.

		:param parameters: Can optionally contain the following parameter(s) to
			request information:

			- -v : model number
			- -c : calibration date
			- -h : hardware version
			- -u : USB version
			- -f : firmware version

			Example (any separator character can be used):

			``-v:-c:-h:-u:-f``

			Defaults to all parameters.
		:type parameters: str
		:return: Count, then serials.

			**Count:**
			On exit, the number of PicoScope 6000 (A API) units found.

			**Serials:**
			If ``parameters`` is an empty string, serials is populated on
			exit with a list of serial numbers separated by commas. Example:

			``AQ005/139,VDR61/356,ZOR14/107``

			If ``parameters`` contains parameters, more data will be appended.
			For example, if ``parameters`` is "-v:-c:-h:-u:-f", each serial
			number has the requested information appended in the following
			format:

			``AQ005/139[6425E,01Jan21,769,2.0,1.7.16.0]``
		:rtype: tuple[int, str]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		status, count, serials = ll.enumerate_units(parameters)
		if status != PicoStatus.OK:
			raise PicoStatusError(status)
		return count, serials

	def ping_unit(self) -> None:
		"""
		Check if device is still connected (ps6000aPingUnit).

		This function can be used to check that the already opened device is
		still connected to the USB port and communication is successful.

		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.ping_unit(handle)
		self._verify_status(status)

	def get_unit_info(self, info: PicoInfo) -> str:
		"""
		Get information about device (ps6000aGetUnitInfo).

		This function retrieves information about the specified oscilloscope.
		If the device fails to open, only the driver version and error code are
		available to explain why the last open unit call failed. To find out
		about unopened devices, call ``enumerate_units``.

		:param info: ``PicoInfo`` enum tag specifying what information is
			required.
		:type info: PicoInfo
		:return: Info string for selected info item.
		:rtype: str
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, info_string = ll.get_unit_info(handle, info)
		self._verify_status(status)
		return info_string

	def close_unit(self) -> None:
		"""
		Close a scope device (ps6000aCloseUnit).

		This function shuts down a PicoScope 6000E Series oscilloscope.

		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.close_unit(handle)
		self._verify_status(status)
		self.raw_handle = None

	def flash_led(self, start: int) -> None:
		"""
		Flash the front-panel LED (ps6000aFlashLed).

		This function flashes the status/trigger LED on the front of the scope
		without blocking the calling thread. Calls to ``run_streaming`` and
		``run_block`` cancel any flashing started by this function. It is not
		possible to set the LED to be constantly illuminated, as this state is
		used to indicate that the scope has not been initialized.

		:param start: The action required:
			- < 0 : flash the LED indefinitely.
			- 0 : stop the LED flashing.
			- > 0 : flash the LED start times.
			If the LED is already flashing on entry to this function, the flash
			count will be reset to start.
		:type start: int
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.flash_led(handle, start)
		self._verify_status(status)

	def memory_segments(self, n_segments: int) -> int:
		"""
		Set number of memory segments (ps6000aMemorySegments).

		This function sets the number of memory segments that the scope will
		use. See also ``memory_segments_by_samples``.

		When the scope is opened, the number of segments defaults to 1, meaning
		that each capture fills the scope's available memory. This function
		allows you to divide the memory into a number of segments so that the
		scope can store several waveforms sequentially.

		:param n_segments: The number of segments required. See datasheet for
			capacity of each model.
		:type n_segments: int
		:return: The number of samples available in each segment. This is the
			total number over all channels, so if more than one channel is in
			use then the number of samples available to each channel is this
			divided by the number of channels.
		:rtype: int
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, n_max_samples = ll.memory_segments(handle, n_segments)
		self._verify_status(status)
		return n_max_samples

	def memory_segments_by_samples(self, n_samples: int) -> int:
		"""
		Set size of memory segments (ps6000aMemorySegmentsBySamples).

		This function sets the number of samples per memory segment. Like
		``memory_segments`` it controls the segmentation of the capture memory,
		but in this case you specify the number of samples rather than the
		number of segments.

		:param n_samples: the number of samples required in each segment. See
			datasheet for capacity of each model. This is the total number over
			n channels, where n is the number of enabled channels or MSO ports
			rounded up to the next power of 2. For example, with 5 channels or
			ports enabled, n is 8. If n > 1, the number of segments available
			will be reduced accordingly.
		:type n_samples: int
		:return: The number of segments into which the capture memory has been
			divided.
		:rtype: int
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, n_max_segments = ll.memory_segments_by_samples(handle, n_samples)
		self._verify_status(status)
		return n_max_segments

	def get_maximum_available_memory(self, resolution: PicoDeviceResolution) -> int:
		"""
		Get maximium available memory (ps6000aGetMaximumAvailableMemory).

		This function returns the maximum number of samples that can be stored
		at a given hardware resolution.

		:param resolution: The vertical resolution.
		:type resolution: PicoDeviceResolution
		:return: The number of samples.
		:rtype: int
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, n_max_samples = ll.get_maximum_available_memory(handle, resolution)
		self._verify_status(status)
		return n_max_samples

	def query_max_segments_by_samples(
		self, n_samples: int, n_channels_enabled: int, resolution: PicoDeviceResolution
	) -> int:
		"""
		Get number of segments (ps6000aQueryMaxSegmentsBySamples).

		This function returns the maximum number of memory segments available
		given the number of samples per segment.

		:param n_samples: The number of samples per segment.
		:type n_samples: int
		:param n_channels_enabled: The number of channels enabled.
		:type n_channels_enabled: int
		:param resolution: The vertical resolution.
		:type resolution: PicoDeviceResolution
		:return: The maximum number of segments that can be requested.
		:rtype: int
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, n_max_segments = ll.query_max_segments_by_samples(
			handle, n_samples, n_channels_enabled, resolution
		)
		self._verify_status(status)
		return n_max_segments

	def set_channel_on(
		self,
		channel: PicoChannel,
		coupling: PicoCoupling,
		range_: PicoConnectProbeRange,
		analog_offset: float,
		bandwidth: PicoBandwidthLimiter,
	) -> None:
		"""
		Enable and set options for one channel (ps6000aSetChannelOn).

		This function switches an analog input channel on and specifies its
		input coupling type, voltage range, analog offset and bandwidth limit.
		Some of the arguments within this function have model-specific values.
		Consult the relevant section below according to the model you have. To
		switch off again, use ``set_channel_off``. For digital ports, see
		``set_digital_channel_on``.

		:param channel: The channel to be configured. Only analog channels (i.e.
			CHANNEL_A through CHANNEL_H) are permitted, and only channels that
			exist on the oscilloscope model in use.
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
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_channel_on(
			handle, channel, coupling, range_, analog_offset, bandwidth
		)
		self._verify_status(status)

	def set_channel_off(self, channel: PicoChannel) -> None:
		"""
		Disable one channel (ps6000aSetChannelOff).

		This function switches an analog input channel off. It has the opposite
		function to ``set_channel_on``.

		:param channel: The channel to disable. Only analog channels (i.e.
			CHANNEL_A through CHANNEL_H) are permitted, and only channels that
			exist on the oscilloscope model in use.
		:type channel: PicoChannel
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_channel_off(handle, channel)
		self._verify_status(status)

	def set_digital_port_on(
		self,
		port: PicoChannel,
		logic_threshold_level: Sequence[int],
		hysteresis: PicoDigitalPortHysteresis,
	) -> None:
		"""
		Set up and enable digital inputs (ps6000aSetDigitalPortOn).

		This function switches on one or more digital ports and sets the logic
		thresholds. Refer to the data sheet for the fastest sampling rates
		available with different combinations of analog and digital inputs. In
		most cases the fastest rates will be obtained by disabling all analog
		channels. When all analog channels are disabled you must also select
		8-bit resolution to allow the digital inputs to operate alone.

		:param port: The port to be configured. Only digital ports are permitted
			(i.e. ``PORT0`` and ``PORT1``).
		:type port: PicoChannel
		:param logic_threshold_level: A sequence of threshold voltages, one for
			each port pin, used to distinguish the 0 and 1 states. Range: –32767
			(–5 V) to 32767 (+5 V). This determines how many pins are enabled.
		:type logic_threshold_level: Sequence[int]
		:param hysteresis: The hysteresis to apply to all channels in the port.
		:type hysteresis: PicoDigitalPortHysteresis
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_digital_port_on(handle, port, logic_threshold_level, hysteresis)
		self._verify_status(status)

	def set_digital_port_off(self, port: PicoChannel) -> None:
		"""
		Switch off digital inputs (ps6000aSetDigitalPortOff).

		This function switches off one or more digital ports.

		:param port: The port to disable. Only digital ports are permitted (i.e.
			``PORT0`` and ``PORT1``).
		:type port: PicoChannel
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_digital_port_off(handle, port)
		self._verify_status(status)

	def get_timebase(
		self, timebase: int, no_samples: int, segment_index: int
	) -> tuple[float, int]:
		"""
		Get available timebases (ps6000aGetTimebase).

		This function calculates the sampling rate and maximum number of samples
		for a given timebase under the specified conditions. The result will
		depend on the number of channels enabled by the last call to
		``set_channel_on`` or ``set_channel_off``.

		The easiest way to find a suitable timebase is to call
		``nearest_sample_interval_stateless``. Alternatively, you can estimate
		the timebase number that you require using the information in the
		timebase guide, then call this function with that timebase and check
		the returned time interval (nanoseconds) value. Repeat until you obtain
		the time interval that you need.

		:param timebase: Timebase; see timebase guide in the manual.
		:type timebase: int
		:param no_samples: The number of samples required. This value is used to
			calculate the most suitable time interval.
		:type no_samples: int
		:param segment_index: The index of the memory segment to use.
		:type segment_index: int
		:return: Time interval, then max samples.

			**Time interval:**
			The time interval (in nanoseconds) between readings
			at the selected timebase.

			**Max samples:**
			The maximum number of samples available. The scope
			allocates a	certain amount of memory for internal overheads and this
			may vary depending on the number of segments, number of channels
			enabled, and the timebase chosen.
		:rtype: tuple[float, int]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, time_interval_ns, max_samples = ll.get_timebase(
			handle, timebase, no_samples, segment_index
		)
		self._verify_status(status)
		return time_interval_ns, max_samples

	def set_simple_trigger(
		self,
		enable: bool,
		source: PicoChannel,
		threshold: int,
		direction: PicoThresholdDirection,
		delay: int,
		auto_trigger_micro_seconds: int,
	) -> None:
		"""
		Set up triggering (ps6000aSetSimpleTrigger).

		:param enable: True to enable, or False to disable, the trigger.
		:type enable: int
		:param source: The channel on which to trigger. Only analog channels
			(i.e. CHANNEL_A through CHANNEL_H) are permitted, and only channels
			that exist on the oscilloscope model in use.
		:type source: PicoChannel
		:param threshold: The ADC count at which the trigger will fire.
		:type threshold: int
		:param direction: The direction in which the signal must move to cause
			a trigger. The following directions are supported: ABOVE, BELOW,
			RISING, FALLING and RISING_OR_FALLING.
		:type direction: PicoThresholdDirection
		:param delay: The time between the trigger occurring and the first
			sample being taken.
		:type delay: int
		:param auto_trigger_micro_seconds: The number of microseconds the device
			will wait if no trigger occurs.
		:type auto_trigger_micro_seconds: int
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_simple_trigger(
			handle,
			enable,
			source,
			threshold,
			direction,
			delay,
			auto_trigger_micro_seconds,
		)
		self._verify_status(status)

	def trigger_within_pre_trigger_samples(
		self, state: PicoTriggerWithinPreTrigger
	) -> None:
		"""
		Switch feature on or off (ps6000aTriggerWithinPreTriggerSamples).

		This function controls a special triggering feature.
		(Seriously, that's all the documentation says.)

		:param state: Whether to disable or enable the feature.
		:type state: PicoTriggerWithinPreTrigger
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.trigger_within_pre_trigger_samples(handle, state)
		self._verify_status(status)

	def set_trigger_channel_properties(
		self,
		channel_properties: Sequence[PicoTriggerChannelProperties],
		aux_output_enable: int,
		auto_trigger_micro_seconds: int,
	) -> None:
		"""
		Set up triggering (ps6000aSetTriggerChannelProperties).

		This function is used to enable or disable triggering and set its
		parameters.

		:param channel_properties: A sequence of
			``PicoTriggerChannelProperties`` describing the requested
			properties. The sequence can contain a single object describing the
			properties of one channel, or a number of objects describing several
			channels. If empty, triggering is switched off.
		:type channel_properties: Sequence[PicoTriggerChannelProperties]
		:param aux_output_enable: "Not used."
		:type aux_output_enable: int
		:param auto_trigger_micro_seconds: The time in microseconds for which
			the scope device will wait before collecting data if no trigger
			event occurs. If this is set to zero, the scope device will wait
			indefinitely for a trigger.
		:type auto_trigger_micro_seconds: int
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_trigger_channel_properties(
			handle, channel_properties, aux_output_enable, auto_trigger_micro_seconds
		)
		self._verify_status(status)

	def set_trigger_channel_conditions(
		self, conditions: Sequence[PicoCondition], action: PicoAction
	) -> None:
		"""
		Set triggering logic (ps6000aSetTriggerChannelConditions).

		This function sets up trigger conditions on the scope's inputs. The
		trigger is defined by one or more ``PicoCondition`` structures that are
		then ORed together. Each structure is itself the AND of the states of
		one or more of the inputs. This AND-OR logic allows you to create any
		possible Boolean function of the scope's inputs.

		If complex triggering is not required, use ``set_simple_trigger``.

		:param conditions: A sequence of ``PicoCondition`` structures
			specifying the conditions that should be applied to each channel.
			In the simplest case, the sequence consists of a single element.
			When there is more than one element, the overall trigger condition
			is the logical OR of all the elements. If the sequence is empty,
			triggering is switched off.
		:type conditions: Sequence[PicoCondition]
		:param action: Specifies how to apply the new conditions to any existing
			trigger conditions (i.e. append or replace).
		:type action: PicoAction
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_trigger_channel_conditions(handle, conditions, action)
		self._verify_status(status)

	def set_trigger_channel_directions(
		self, directions: Sequence[PicoDirection]
	) -> None:
		"""
		Set trigger directions (ps6000aSetTriggerChannelDirections).

		This function sets the direction of the trigger for one or more
		channels.

		:param directions: A sequence of ``PicoDirection`` objects, each
			specifying the trigger direction for a channel.
		:type directions: Sequence[PicoDirection]
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_trigger_channel_directions(handle, directions)
		self._verify_status(status)

	def set_trigger_delay(self, delay: int) -> None:
		"""
		Set post-trigger delay (ps6000aSetTriggerDelay).

		:param delay: The time between the trigger occurring and the first
			sample. For example, if delay=100, the scope would wait 100 sample
			periods before sampling. At a timebase of 5 GS/s, or 200 ps per
			sample (timebase=0), the total delay would then be 100 x 200 ps =
			20 ns. Range: 0 to MAX_DELAY_COUNT.
		:type delay: int
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_trigger_delay(handle, delay)
		self._verify_status(status)

	def get_data_buffer(
		self,
		channel: PicoChannel,
		n_samples: int,
		data_type: PicoDataType,
		segment: int,
		down_sample_ratio_mode: PicoRatioMode,
		clear_others: bool = False,
	) -> Buffer:
		"""
		Allocate and provide location of data buffer (ps6000aSetDataBuffers).

		Unlike the C API, this function will allocate the buffer and provide it
		to the driver. The buffer will be returned. This object will store
		a reference to the buffer to prevent garbage collection.

		This function tells the driver where to store the data, either
		unprocessed or downsampled, that will be returned after the next call
		to one of the ``get_values`` functions. The function allows you to
		specify only a single buffer, so for aggregation mode, which requires
		two buffers, you must call ``set_data_buffers`` instead.

		The buffer persists between captures until it is replaced with another
		buffer or buffer is set to NULL. The buffer can be replaced at any time
		between calls to ``get_values``.

		:param channel: The channel you want to use with the buffer.
		:type channel: PicoChannel
		:param n_samples: The length of the data buffer, in samples.
		:type n_samples: int
		:param data_type: The data type that you wish to use for the sample
			values.
		:type data_type: PicoDataType
		:param segment: The segment index. Must be zero for streaming.
		:type segment: int
		:param down_sample_ratio_mode: The downsampling mode. See
			``get_values`` for the available modes, but note that a single
			call to ``get_data_buffer`` can only associate one buffer with
			one downsampling mode. If you intend to call ``get_values`` with
			more than one downsampling mode activated, then you must call
			``get_data_buffer`` several times to associate a separate buffer
			with each downsampling mode.
		:type down_sample_ratio_mode: PicoRatioMode
		:param clear_others: True to clear any other associated buffers, False
			to keep them while adding a new one. Defaults to False.
			TODO: This may clear all other buffers, rather than just those
			associated with this channel/datatype/segment.
		:type clear_others: bool
		:return: Data buffer.
		:rtype: Buffer
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		buffer = Buffer(
			buffer=(data_type.ctype * n_samples)(),
			channel=channel,
			datatype=data_type,
			segment=segment,
			downsampling_mode=down_sample_ratio_mode,
			max_min=BufferMaxMin.MAX,
		)
		self.set_data_buffers(buffer, clear_others=clear_others)
		return buffer

	def get_data_buffers(
		self,
		channel: PicoChannel,
		n_samples: int,
		data_type: PicoDataType,
		segment: int,
		down_sample_ratio_mode: PicoRatioMode,
		clear_others: bool = False,
	) -> tuple[Buffer, Buffer]:
		"""
		Allocate and provide location of both data buffers (ps6000aSetDataBuffers).

		Unlike the C API, this function will allocate the buffers and provide
		them to the driver. The buffers will be returned. This object will
		store a reference to the buffers to prevent garbage collection.

		This function tells the driver the location of two buffers for
		receiving data. If you do not need two buffers, because you are not
		using aggregate mode, then you should use ``get_data_buffer`` instead.

		:param channel: The channel for which you want to set the buffers.
		:type channel: PicoChannel
		:param n_samples: The length of the data buffers, in samples.
		:type n_samples: int
		:param data_type: The data type that you wish to use for the sample
			values.
		:type data_type: PicoDataType
		:param segment: The segment index.
		:type segment: int
		:param down_sample_ratio_mode: The downsampling mode. See
			``get_values`` for the available modes, but note that a single
			call to ``get_data_buffer`` can only associate one pair of buffers
			with one downsampling mode. If you intend to call ``get_values``
			with more than one downsampling mode activated, then you must call
			``get_data_buffer`` several times to associate a separate buffer
			pair with each downsampling mode.
		:type down_sample_ratio_mode: PicoRatioMode
		:param clear_others: True to clear any other associated buffers, False
			to keep them while adding a new one. Defaults to False.
			TODO: This may clear all other buffers, rather than just those
			associated with this channel/datatype/segment.
		:type clear_others: bool
		:return: "Max" buffer, then "min" buffer.

			**Max buffer:**
			A buffer to receive the maximum data values in aggregation mode, or
			the non-aggregated values otherwise.

			**Min buffer:**
			A buffer to receive the minimum aggregated data values. Not used in
			other downsampling modes.
		:rtype: tuple[Buffer, Buffer]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		buffer_max = Buffer(
			buffer=(data_type.ctype * n_samples)(),
			channel=channel,
			datatype=data_type,
			segment=segment,
			downsampling_mode=down_sample_ratio_mode,
			max_min=BufferMaxMin.MAX,
		)
		buffer_min = Buffer(
			buffer=(data_type.ctype * n_samples)(),
			channel=channel,
			datatype=data_type,
			segment=segment,
			downsampling_mode=down_sample_ratio_mode,
			max_min=BufferMaxMin.MIN,
		)
		self.set_data_buffers(buffer_max, buffer_min, clear_others=clear_others)
		return buffer_max, buffer_min

	def set_data_buffers(
		self,
		buffer_max: Buffer,
		buffer_min: Optional[Buffer] = None,
		clear_others: bool = False,
	) -> None:
		"""
		Provide location of one or both data buffers (ps6000aSetDataBuffers).

		This function requires a Buffer object to already be created. The
		easiest way to do this is with ``get_data_buffer(s)``. This function
		is provided mostly as a more precise alternative to
		``reload_data_buffers``.

		This function tells the driver the location of two buffers for
		receiving data. If you do not need two buffers, simply set the "min"
		buffer to None (the default).

		:param buffer_max: A buffer to receive the maximum data values in
			aggregation mode, or the non-aggregated values otherwise.
		:type buffer_max: Buffer
		:param buffer_min: A buffer to receive the minimum aggregated data
			values. Not used in other downsampling modes. Optional, defaults
			to None, in which case only "max" buffer is set.
		:type buffer_min: Optional[Buffer]
		:param clear_others: True to clear any other associated buffers, False
			to keep them while adding a new one. Defaults to False.
		:type clear_others: bool
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		:raises ValueError: Will raise if ``buffer_min`` is not compatible with
			``buffer_max``.
		"""
		buffer_min_raw: Optional[Array] = None
		if buffer_min is not None:
			if buffer_min.buffer_class != buffer_max.buffer_class:
				raise ValueError(
					"Both min and max buffers must have same buffer class. "
					f"({buffer_min.buffer_class} != {buffer_max.buffer_class})"
				)
			if buffer_min.downsampling_mode != buffer_max.downsampling_mode:
				raise ValueError(
					"Both min and max buffers must have same downsampling "
					f"mode. ({buffer_min.downsampling_mode} != "
					f"{buffer_max.downsampling_mode})"
				)
			buffer_min_raw = buffer_min.buffer

		handle = self.handle
		action = PicoAction.ADD
		if clear_others:
			action |= PicoAction.CLEAR_ALL
		status = ll.set_data_buffers(
			handle,
			buffer_max.channel,
			buffer_max.buffer,
			buffer_min_raw,
			buffer_max.datatype,
			buffer_max.segment,
			buffer_max.downsampling_mode,
			action,
		)
		self._verify_status(status)

		buffer_class = buffer_max.buffer_class
		if clear_others:
			self.buffers[buffer_class].clear()
		self.buffers[buffer_class].add(buffer_max)
		if buffer_min is not None:
			self.buffers[buffer_class].add(buffer_min)

	def clear_data_buffers(
		self, channel: PicoChannel, data_type: PicoDataType, segment: int
	) -> None:
		"""
		Clear/unset data buffers (ps6000aSetDataBuffers).

		This function calls ps6000aSetDataBuffers with two null pointers.
		All the buffers associated with the specified channel, datatype, and
		segment will be unregisterd from the driver, and this object will no
		longer hold a reference to them.

		:param channel: The channel for which you want to clear the buffers.
		:type channel: PicoChannel
		:param data_type: The data type of the sample values.
		:type data_type: PicoDataType
		:param segment: The segment index.
		:type segment: int
		:return: None.
		:rtype: None
		"""
		handle = self.handle
		status = ll.set_data_buffers(
			handle,
			channel,
			None,
			None,
			data_type,
			segment,
			PicoRatioMode.RAW,
			PicoAction.CLEAR_ALL,
		)
		self._verify_status(status)

		buffer_class = BufferClass(channel=channel, datatype=data_type, segment=segment)
		self.buffers[buffer_class].clear()

	def get_existing_data_buffers(
		self, channel: PicoChannel, data_type: PicoDataType, segment: int
	) -> set[Buffer]:
		"""
		Retrieve previously created buffers.

		Get a set of previously created/registed buffers, which have not been
		subsequently cleared, for a given channel/datatype/segment. This can
		also be accomplished by accessing the ``buffers`` dict.

		:param channel: The channel of the buffers.
		:type channel: PicoChannel
		:param data_type: The data type of the buffer elements.
		:type data_type: PicoDataType
		:param segment: The segment index of the buffers.
		:type segment: int
		:return: A set of previously created buffers. May be empty.
		:rtype: set[Buffer]
		"""
		buffer_class = BufferClass(channel=channel, datatype=data_type, segment=segment)
		return self.buffers[buffer_class]

	def get_all_existing_data_buffers(
		self,
		channel: Optional[PicoChannel] = None,
		data_type: Optional[PicoDataType] = None,
		segment: Optional[int] = None,
	) -> set[Buffer]:
		"""
		Retrieve previously created buffers for multiple buffer classes.

		Get a set of previously created/registed buffers, which have not been
		subsequently cleared, matching zero or more of ``channel``,
		``data_type``, and ``segment`` as specified.

		:param channel: The channel of the buffers. Optional; if omitted, the
			returned buffers may have any channel.
		:type channel: PicoChannel
		:param data_type: The data type of the buffer elements. Optional; if
			omitted, the returned buffers may have any data type.
		:type data_type: PicoDataType
		:param segment: The segment index of the buffers. Optional; if omitted,
			the returned buffers may be for any segment.
		:type segment: int
		:return: A set of previously created buffers. May be empty.
		:rtype: set[Buffer]
		"""
		out: set[Buffer] = set()
		for bclass in self.buffers.values():
			for buffer in bclass:
				out.add(buffer)
				if channel is not None and buffer.channel != channel:
					out.remove(buffer)
				if data_type is not None and buffer.datatype != data_type:
					out.remove(buffer)
				if segment is not None and buffer.segment != segment:
					out.remove(buffer)
		return out

	def get_existing_data_buffer_pairs(
		self, channel: PicoChannel, data_type: PicoDataType, segment: int
	) -> set[tuple[Buffer, Optional[Buffer]]]:
		"""
		Retrieve previously created buffers in max/min pairs.

		Get a set of previously created/registed buffers, which have not been
		subsequently cleared, for a given channel/datatype/segment. This can
		also be accomplished by accessing the ``buffers`` dict.

		:param channel: The channel of the buffers.
		:type channel: PicoChannel
		:param data_type: The data type of the buffer elements.
		:type data_type: PicoDataType
		:param segment: The segment index of the buffers.
		:type segment: int
		:return: A set of previously created buffers, in max/min pairs according
			to buffer class as well as downsampling mode. May be empty. Within
			the tuple, max buffer is first, and min buffer (or None) is second.
		:rtype: set[tuple[Buffer, Optional[Buffer]]]
		"""
		pairs: dict[Any, list[Optional[Buffer]]] = defaultdict(lambda: [None, None])
		out: set[tuple[Buffer, Optional[Buffer]]] = set()
		for bclass in self.buffers.values():
			for buffer in bclass:
				key = (
					buffer.channel,
					buffer.datatype,
					buffer.segment,
					buffer.downsampling_mode,
				)
				if buffer.max_min == BufferMaxMin.MAX:
					pairs[key][0] = buffer
				elif buffer.max_min == BufferMaxMin.MIN:
					pairs[key][0] = buffer
				else:
					raise TypeError(f"Unknown buffer side: {buffer.max_min}")
		for pair in pairs.values():
			buffer_max = pair[0]
			buffer_min = pair[1]
			if buffer_max is None:
				logger.warning(f"No max buffer matching min buffer {buffer_min}")
				continue
			out.add((buffer_max, buffer_min))
		return out

	def reload_data_buffers(
		self, channel: PicoChannel, data_type: PicoDataType, segment: int
	) -> set[Buffer]:
		"""
		Re-register existing buffers with the driver.

		Get a set of previously created/registed buffers, which have not been
		subsequently cleared, for a given channel/datatype/segment. This can
		also be accomplished by accessing the ``buffers`` dict.

		:param channel: The channel of the buffers.
		:type channel: PicoChannel
		:param data_type: The data type of the buffer elements.
		:type data_type: PicoDataType
		:param segment: The segment index of the buffers.
		:type segment: int
		:return: Any buffers which were reloaded. May be empty.
		:rtype: set[Buffer]
		"""
		handle = self.handle
		pairs = self.get_existing_data_buffer_pairs(
			channel=channel, data_type=data_type, segment=segment
		)
		out: set[Buffer] = set()
		for pair in pairs:
			buffer_max = pair[0]
			buffer_min = pair[1]
			status = ll.set_data_buffers(
				handle,
				buffer_max.channel,
				buffer_max.buffer,
				buffer_min.buffer if buffer_min is not None else None,
				buffer_max.datatype,
				buffer_max.segment,
				buffer_max.downsampling_mode,
				PicoAction.ADD,
			)
			self._verify_status(status)
			out.add(buffer_max)
			if buffer_min is not None:
				out.add(buffer_min)
		return out

	@property
	def total_existing_data_buffers(self) -> int:
		"""
		Count the total number of created/registered buffers for this device.

		:getter: Count the total number of created buffers for this device.
		:setter: None, computed/read-only.
		:return: The total number of created/registered buffers for this device.
		:rtype: int
		"""
		count = 0
		for bufset in self.buffers.values():
			count += len(bufset)
		return count

	def run_streaming(
		self,
		sample_interval: float,
		max_pre_trigger_samples: int,
		max_post_trigger_samples: int,
		auto_stop: bool,
		down_sample_ratio: int,
		down_sample_ratio_mode: PicoRatioMode,
	) -> float:
		"""
		Start streaming mode capture (ps6000aRunStreaming).

		This function tells the oscilloscope to start collecting data in
		streaming mode. The device can return either raw or downsampled data to
		your application while streaming is in progress. Call
		``get_streaming_latest_values`` to retrieve the data. Consult the
		manual for more details.

		When a trigger is set, the total number of samples is the sum of
		``max_pre_trigger_samples`` and ``max_post_trigger_samples``. If
		``auto_stop`` is False then this will become the maximum number of
		samples without downsampling.

		When downsampled data is returned, the raw samples remain stored on the
		device. The maximum number of raw samples that can be retrieved after
		streaming has stopped is (scope's memory size) / (resolution data size
		* channels), where channels is the number of active channels rounded up
		to a power of 2.

		:param sample_interval: The requested time interval between samples,
			in seconds.
		:type sample_interval: float
		:param max_pre_trigger_samples: The maximum number of raw samples
			before a trigger event for each enabled channel. If no trigger
			condition is set this argument is ignored.
		:type max_pre_trigger_samples: int
		:param max_post_trigger_samples: The maximum number of raw samples
			after a trigger event for each enabled channel. If no trigger
			condition is set, this argument states the maximum number of
			samples to be stored.
		:type max_post_trigger_samples: int
		:param auto_stop: True if streaming should stop when the maximum number
			of samples have been captured, False otherwise.
		:type auto_stop: bool
		:param down_sample_ratio: The downsampling factor that will be applied
			to the raw data. Must be greater than zero.
		:type down_sample_ratio: int
		:param down_sample_ratio_mode: Which downsampling mode to use.
		:type down_sample_ratio_mode: PicoRatioMode
		:return: The actual sample interval (in seconds).
		:rtype: float
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		if self.total_existing_data_buffers <= 0:
			logger.warning("run_streaming called without any buffers created.")
		status, sample_interval = ll.run_streaming(
			handle,
			sample_interval,
			PicoTimeUnits.S,
			max_pre_trigger_samples,
			max_post_trigger_samples,
			auto_stop,
			down_sample_ratio,
			down_sample_ratio_mode,
		)
		self._verify_status(status)
		return sample_interval

	def get_streaming_latest_values(
		self, streaming_data_info: Optional[Sequence[PicoStreamingDataInfo]] = None
	) -> tuple[bool, Array[PicoStreamingDataInfo], Array[PicoStreamingDataTriggerInfo]]:
		"""
		Read streaming data (ps6000aGetStreamingLatestValues).

		This function populates the ``PicoStreamingDataInfo`` structures with a
		description of the samples available and the
		``PicoStreamingDataTriggerInfo`` structures to indicate that a trigger
		has occurred and at what location.

		:param streaming_data_info: Data structures to be populated with buffer
			information. Set the channel, downsampling ratio, and datatype
			before calling this function; the driver will set the rest.
			Optional. If None, the input structures will be generated
			automatically from all registed buffers.
		:type streaming_data_info: Optional[Sequence[PicoStreamingDataInfo]]
		:return: A flag which is True if the last buffer is full, then a list
			of structures containing buffer information, then a list of
			structures containing trigger information.
		:rtype: tuple[bool, Array[PicoStreamingDataInfo],
			Array[PicoStreamingDataTriggerInfo]]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK`` or
			``PicoStatus.WAITING_FOR_DATA_BUFFERS``.
		"""
		handle = self.handle
		if streaming_data_info is None:
			streaming_data_info = list()
			for buffer in self.get_all_existing_data_buffers(segment=0):
				streaming_data_info.append(buffer.empty_streaming_info)
		(
			status,
			streaming_info_array,
			streaming_trigger_array,
		) = ll.get_streaming_latest_values(handle, streaming_data_info)
		self.last_status = status
		if status != PicoStatus.OK and status != PicoStatus.WAITING_FOR_DATA_BUFFERS:
			raise PicoStatusError(status)
		full = status == PicoStatus.WAITING_FOR_DATA_BUFFERS
		return full, streaming_info_array, streaming_trigger_array

	def no_of_streaming_values(self) -> int:
		"""
		Get number of captured samples (ps6000aNoOfStreamingValues).

		This function returns the number of samples available after data
		collection in streaming mode. Call it after calling ``stop``.

		:return: The number of samples.
		:rtype: int
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, no_of_values = ll.no_of_streaming_values(handle)
		self._verify_status(status)
		return no_of_values

	def run_block(
		self,
		no_of_pre_trigger_samples: int,
		no_of_post_trigger_samples: int,
		timebase: int,
		segment_index: int,
		ready: Optional[BlockReadyCallback] = None,
	) -> float:
		"""
		Start collecting data in block mode (ps6000aRunBlock).

		For a step-by-step guide to this process, see `Using block mode`_.

		The number of samples is determined by ``no_of_pre_trigger_samples`` and
		``no_of_post_trigger_samples`` (see below for details). The total number
		of samples must not be more than the size of the segment referred to by
		``segment_index``.

		:param no_of_pre_trigger_samples: The number of samples to return before
			the trigger event. If no trigger has been set, then this argument is
			added to ``no_of_post_trigger_samples`` to give the maximum number
			of data points (samples) to collect.
		:type no_of_pre_trigger_samples: int
		:param no_of_post_trigger_samples: The number of samples to return after
			the trigger event. If no trigger event has been set, then this
			argument is added to ``no_of_pre_trigger_samples`` to give the
			maximum number of data points to collect. If a trigger condition
			has been set, this specifies the number of data points to collect
			after a trigger has fired, and the number of samples to be collected
			is: ``no_of_pre_trigger_samples + no_of_post_trigger_samples``
		:type no_of_post_trigger_samples: int
		:param timebase: A number in the range 0 to 0xFFFF_FFFF. See the guide
			to calculating timebase values.
		:type timebase: int
		:param segment_index: Zero-based, specifies which memory segment to use.
		:type segment_index: int
		:param ready: An optional callback function that the driver will call
			when the data has been collected. To use the ``is_ready`` polling
			method instead of a callback function, provide ``None``. Optional,
			defaults to None.
		:type ready: BlockReadyCallback
		:return: The time in milliseconds that the scope will spend collecting
			samples.
		:rtype: float
		"""
		handle = self.handle
		callback = wrap_block_ready(ready) if ready is not None else None

		status, time_indisposed_ms = ll.run_block(
			handle,
			no_of_pre_trigger_samples,
			no_of_post_trigger_samples,
			timebase,
			segment_index,
			callback,
			None,
		)
		self._verify_status(status)
		return time_indisposed_ms

	def is_ready(self) -> bool:
		"""
		Check if the device has finished collecting (ps6000aIsReady).

		This function may be used instead of a callback function to receive data
		from ``run_block``. To use this method, pass None as the ``ready``
		argument to ``run_block`` (no callback). You must then poll the driver
		to see if it has finished collecting the requested samples.

		:return: Indicates the state of collection. If zero, the device is still
			collecting. If non-zero, the device has finished collecting and
			``get_values`` can be used to retrieve the data.
		:rtype: bool
		"""
		handle = self.handle
		status, ready = ll.is_ready(handle)
		self._verify_status(status)
		return ready

	def get_values(
		self,
		start_index: int,
		no_of_samples: int,
		down_sample_ratio: int,
		down_sample_ratio_mode: PicoRatioMode,
		segment_index: int,
	) -> tuple[int, PicoChannelFlags]:
		"""
		Retrieve block-mode data (ps6000aGetValues).

		This function retrieves block-mode data, either with or without
		downsampling, starting at the specified sample number. It is used to get
		the stored data from the scope after data collection has stopped, and
		store it in a user buffer previously passed to ``set_data_buffer`` or
		``set_data_buffers``. It blocks the calling function while retrieving
		data.

		Note that the data is retrieved to the previously configured buffer,
		and is not returned from this function.

		:param start_index: A zero-based index that indicates the start point
			for data collection. It is measured in sample intervals from the
			start of the buffer.
		:type start_index: int
		:param no_of_samples: The number of raw samples to be processed. The
			number of samples retrieved will not be more than the number
			requested, and the data retrieved always starts with the first
			sample captured.
		:type no_of_samples: int
		:param down_sample_ratio: The downsampling factor that will be applied
			to the raw data. Must be greater than zero.
		:type down_sample_ratio: int
		:param down_sample_ratio_mode: Which downsampling mode to use.
		:type down_sample_ratio_mode: PicoRatioMode
		:param segment_index: The zero-based number of the memory segment where
			the data is stored.
		:type segment_index: int
		:return: Tuple of:

			- The actual number of raw samples retrieved.
			- A set of flags that indicate whether an overvoltage has occurred
			on any of the channels.

		:rtype: Tuple[int, PicoChannelFlags]
		"""
		handle = self.handle
		status, no_of_samples, overflow = ll.get_values(
			handle,
			start_index,
			no_of_samples,
			down_sample_ratio,
			down_sample_ratio_mode,
			segment_index,
		)
		self._verify_status(status)
		return no_of_samples, overflow

	def stop(self) -> None:
		"""
		Stop sampling (ps6000aStop).

		This function stops the scope device from sampling data.

		When running the device in streaming mode, always call this function
		after the end of a capture to ensure that the scope is ready for the
		next capture.

		When running the device in block mode or rapid block mode, you can call
		this function to interrupt data capture.

		If this function is called before a trigger event occurs, the
		oscilloscope may not contain valid data.

		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.stop(handle)
		self._verify_status(status)

	def get_trigger_info(
		self, first_segment_index: int, segment_count: int
	) -> Array[PicoTriggerInfo]:
		"""
		Get trigger timing information (ps6000aGetTriggerInfo).

		This function gets trigger timing information from one or more buffer
		segments.

		Call this function after data has been captured or when data has been
		retrieved from a previous capture.

		:param first_segment_index: The index of the first segment of interest.
		:type first_segment_index: int
		:param segment_count: The number of segments of interest.
		:type segment_count: int
		:return: A sequence of ``PicoTriggerInfo`` structures, one for each
			buffer segment, containing trigger information. Length will be
			equal to ``segment_count``.
		:rtype: Array[PicoTriggerInfo]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, trigger_info = ll.get_trigger_info(
			handle, first_segment_index, segment_count
		)
		self._verify_status(status)
		return trigger_info

	def get_analog_offset_limits(
		self, range_: PicoConnectProbeRange, coupling: PicoCoupling
	) -> tuple[float, float]:
		"""
		Get analog offset information (ps6000aGetAnalogueOffsetLimits).

		This function is used to get the maximum and minimum allowable analog
		offset for a specific voltage range.

		:param range_: The voltage range for which minimum and maximum voltages
			are required.
		:type range_: PicoConnectProbeRange
		:param coupling: The type of AC/DC/50 Ω coupling used.
		:type coupling: PicoCoupling
		:return: Minimum offset voltage, then maximum offset voltage.
		:rtype: tuple[float, float]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, minimum_voltage, maximum_voltage = ll.get_analog_offset_limits(
			handle, range_, coupling
		)
		self._verify_status(status)
		return minimum_voltage, maximum_voltage

	def get_minimum_timebase_stateless(
		self, enabled_channel_flags: PicoChannelFlags, resolution: PicoDeviceResolution
	) -> tuple[int, float]:
		"""
		Find fastest available timebase (ps6000aGetMinimumTimebaseStateless).

		This function returns the shortest timebase that could be selected with
		a proposed configuration of the oscilloscope. It does not set the
		oscilloscope to the proposed configuration.

		:param enabled_channel_flags: A bit field indicating which channels are
			enabled in the proposed configuration. Channel A is bit 0 and so on.
		:type enabled_channel_flags: PicoChannelFlags
		:param resolution: The vertical resolution in the proposed
			configuration.
		:type resolution: PicoDeviceResolution
		:return: Timebase, then time interval.

			**Timebase:**
			The number of the shortest timebase possible with the proposed
			configuration.

			**Time interval:**
			The sample period in seconds corresponding to the timebase.
		:rtype: tuple[int, float]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, timebase, time_interval = ll.get_minimum_timebase_stateless(
			handle, enabled_channel_flags, resolution
		)
		self._verify_status(status)
		return timebase, time_interval

	def nearest_sample_interval_stateless(
		self,
		enabled_channel_flags: PicoChannelFlags,
		time_interval_requested: float,
		resolution: PicoDeviceResolution,
	) -> tuple[int, float]:
		"""
		Get nearest sampling interval (ps6000aNearestSampleIntervalStateless).

		This function returns the nearest possible sample interval to the
		requested sample interval. It does not change the configuration of the
		oscilloscope.

		:param enabled_channel_flags: A bit field indicating which channels are
			enabled in the proposed configuration. Channel A is bit 0 and so on.
		:type enabled_channel_flags: PicoChannelFlags
		:param time_interval_requested: The time interval, in seconds, that you
			would like to obtain.
		:type time_interval_requested: double
		:param resolution: The vertical resolution for which the oscilloscope
			will be configured.
		:type resolution: PicoDeviceResolution
		:return: Timebase, then time interval available.

			**Timebase:**
			The number of the nearest available timebase.

			**Time interval availble:**
			The nearest available time interval, in seconds.
		:rtype: tuple[int, float]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		(
			status,
			timebase,
			time_interval_available,
		) = ll.nearest_sample_interval_stateless(
			handle, enabled_channel_flags, time_interval_requested, resolution
		)
		self._verify_status(status)
		return timebase, time_interval_available

	def set_device_resolution(self, resolution: PicoDeviceResolution) -> None:
		"""
		Set the hardware resolution (ps6000aSetDeviceResolution).

		This function sets the sampling resolution of the device. At 10-bit and
		higher resolutions, the maximum capture buffer length is half that of
		8-bit mode. When using 12-bit resolution only 2 channels can be enabled
		to capture data.

		When you change the device resolution, the driver discards all
		previously captured data.

		After changing the resolution and before calling ``run_block`` or
		``run_streaming``, call ``set_channel_on`` to set up the input channels.

		:param resolution: Determines the resolution of the device when opened.
		:type resolution: PicoDeviceResolution
		:return: None.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.set_device_resolution(handle, resolution)
		self._verify_status(status)

	def get_device_resolution(self) -> PicoDeviceResolution:
		"""
		Retrieve the device resolution (ps6000aGetDeviceResolution).

		This function retrieves the vertical resolution of the oscilloscope.

		:return: The resolution of the device.
		:rtype: PicoDeviceResolution
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, resolution = ll.get_device_resolution(handle)
		self._verify_status(status)
		return resolution

	def get_scaling_values(
		self, scaling_values: Sequence[PicoScalingFactorsValues]
	) -> None:
		"""
		Call ps6000aGetScalingValues (no documentation available).

		:param scaling_values: Sequence of ``PicoScalingFactorsValues``
			structures to be updated with scaling factor information. Probably
			the ``channel`` member needs to be set beforehand, then the rest
			are set by the driver.
		:type scaling_values: Sequence[PicoScalingFactorsValues]
		:return: None, ``scaling_values`` is updated by the driver.
		:rtype: None
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status = ll.get_scaling_values(handle, scaling_values)
		self._verify_status(status)

	def get_adc_limits(self, resolution: PicoDeviceResolution) -> tuple[int, int]:
		"""
		Get min and max sample values (ps6000aGetAdcLimits).

		This function gets the maximum and minimum sample values that the ADC
		can produce at a given resolution.

		:param resolution: The vertical resolution about which you require
			information.
		:type resolution: PicoDeviceResolution
		:return: The minimum sample value, then maximum sample value.
		:rtype: tuple[int, int]
		:raises PicoStatusException: Will raise if driver returns a status code
			other than ``PicoStatus.OK``.
		"""
		handle = self.handle
		status, min_value, max_value = ll.get_adc_limits(handle, resolution)
		self._verify_status(status)
		return min_value, max_value
