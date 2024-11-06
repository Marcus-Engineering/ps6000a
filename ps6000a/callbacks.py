"""PicoScope API callback function types."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: callbacks.py
#
# PicoScope API callback function types.
#
# Portions Copyright 2018-2019 Pico Technology Ltd. (ISC Licensed)
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Created.                                       jrowley
#   20240314       Fixed callback objects going out of scope.     jrowley
#
###############################################################################

from ctypes import POINTER, WINFUNCTYPE, c_int16, c_uint16, c_uint32, c_uint64, c_void_p
from ctypes import cast as c_cast
from typing import TYPE_CHECKING, Callable, Protocol, Sequence, Union

from ps6000a.constants import (
	PicoChannel,
	PicoClockReference,
	PicoConnectProbe,
	PicoProbeUserAction,
	PicoReadSelection,
	PicoStatus,
	PicoTemperatureReference,
)
from ps6000a.types import (
	PicoDigitalPortInteractions,
	PicoHandle,
	PicoProbeButtonPressParameter,
	PicoUserProbeInteractions,
)

if TYPE_CHECKING:
	# noinspection PyProtectedMember
	# noinspection PyUnresolvedReferences
	# We need _CData for typing to work right. API stability unknown.
	from ctypes import _CData

# Many real prototypes have a final argument (void *)pParameter. We do not pass
# this to the Python function, because its use is user-defined and it's safest
# to say we just don't use it at all.


# ps6000aBlockReady


class BlockReadyCallback(Protocol):
	"""Pythonized version of ps6000aBlockReady C function type."""

	def __call__(self, handle: PicoHandle, status: PicoStatus) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class BlockReadyCType(_CData):
		"""ps6000aBlockReady C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	BlockReadyCType = WINFUNCTYPE(None, c_int16, c_uint32, c_void_p)


def wrap_block_ready(callback: BlockReadyCallback) -> BlockReadyCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: BlockReadyCallback
	:return: C function pointer according to "ps6000aBlockReady" typedef.
	:rtype: BlockReadyCType
	"""
	holder = "__ps6000a_BlockReadyCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		parameter: c_void_p,
	) -> None:
		callback(PicoHandle(handle), PicoStatus(status))

	out = BlockReadyCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# ps6000aDataReady


class DataReadyCallback(Protocol):
	"""Pythonized version of ps6000aDataReady C function type."""

	def __call__(
		self, handle: PicoHandle, status: PicoStatus, num_samples: int, overflow: int
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class DataReadyCType(_CData):
		"""ps6000aDataReady C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	DataReadyCType = WINFUNCTYPE(None, c_int16, c_uint32, c_uint64, c_int16, c_void_p)


def wrap_data_ready(callback: DataReadyCallback) -> DataReadyCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: DataReadyCallback
	:return: C function pointer according to "ps6000aDataReady" typedef.
	:rtype: DataReadyCType
	"""
	holder = "__ps6000a_DataReadyCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		num_samples: int,
		overflow: int,
		parameter: c_void_p,
	) -> None:
		callback(PicoHandle(handle), PicoStatus(status), num_samples, overflow)

	out = DataReadyCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# ps6000aDigitalPortInteractions


class DigitalPortInteractionsCallback(Protocol):
	"""Pythonized version of ps6000aDigitalPortInteractions C function type."""

	def __call__(
		self,
		handle: PicoHandle,
		status: PicoStatus,
		ports: Sequence[PicoDigitalPortInteractions],
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class DigitalPortInteractionsCType(_CData):
		"""ps6000aDigitalPortInteractions C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	DigitalPortInteractionsCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_void_p, c_uint32
	)


def wrap_digital_port_interactions(
	callback: DigitalPortInteractionsCallback,
) -> DigitalPortInteractionsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: DigitalPortInteractionsCallback
	:return: C function pointer according to "ps6000aDigitalPortInteractions"
		typedef.
	:rtype: DigitalPortInteractionsCType
	"""
	holder = "__ps6000a_DigitalPortInteractionsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		ports: c_void_p,  # Points to array of PicoDigitalPortInteractions.
		num_ports: int,  # Length of ports array.
	) -> None:
		c_struct_p = POINTER(PicoDigitalPortInteractions * num_ports)
		ports_live = c_cast(ports, c_struct_p)
		callback(PicoHandle(handle), PicoStatus(status), tuple(ports_live.contents))

	out = DigitalPortInteractionsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoUpdateFirmwareProgress


class PicoUpdateFirmwareProgressCallback(Protocol):
	"""Pythonized version of PicoUpdateFirmwareProgress C function type."""

	def __call__(self, handle: PicoHandle, progress: int) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoUpdateFirmwareProgressCType(_CData):
		"""PicoUpdateFirmwareProgress C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoUpdateFirmwareProgressCType = WINFUNCTYPE(None, c_int16, c_uint16)


def wrap_pico_update_firmware_progress(
	callback: PicoUpdateFirmwareProgressCallback,
) -> PicoUpdateFirmwareProgressCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoUpdateFirmwareProgressCallback
	:return: C function pointer according to "PicoUpdateFirmwareProgress"
		typedef.
	:rtype: PicoUpdateFirmwareProgressCType
	"""
	holder = "__ps6000a_PicoUpdateFirmwareProgressCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(handle: int, progress: int) -> None:
		callback(PicoHandle(handle), progress)

	out = PicoUpdateFirmwareProgressCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoProbeInteractions


class PicoProbeInteractionsCallback(Protocol):
	"""Pythonized version of PicoProbeInteractions C function type."""

	def __call__(
		self,
		handle: PicoHandle,
		status: PicoStatus,
		probes: Sequence[PicoUserProbeInteractions],
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoProbeInteractionsCType(_CData):
		"""PicoProbeInteractions C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoProbeInteractionsCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_void_p, c_uint32
	)


def wrap_pico_probe_interactions(
	callback: PicoProbeInteractionsCallback,
) -> PicoProbeInteractionsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoProbeInteractionsCallback
	:return: C function pointer according to "PicoProbeInteractions" typedef.
	:rtype: PicoProbeInteractionsCType
	"""
	holder = "__ps6000a_PicoProbeInteractionsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		probes: c_void_p,  # Points to array of PicoUserProbeInteractions.
		num_probes: int,  # Length of probes array.
	) -> None:
		c_struct_p = POINTER(PicoUserProbeInteractions * num_probes)
		probes_live = c_cast(probes, c_struct_p)
		callback(PicoHandle(handle), PicoStatus(status), tuple(probes_live.contents))

	out = PicoProbeInteractionsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoDataReadyUsingReads


class PicoDataReadyUsingReadsCallback(Protocol):
	"""Pythonized version of PicoDataReadyUsingReads C function type."""

	def __call__(
		self,
		handle: PicoHandle,
		read: PicoReadSelection,
		status: PicoStatus,
		from_segment_index: int,
		to_segment_index: int,
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoDataReadyUsingReadsCType(_CData):
		"""PicoDataReadyUsingReads C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoDataReadyUsingReadsCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_uint32, c_uint64, c_uint64, c_void_p
	)


def wrap_pico_data_ready_using_reads(
	callback: PicoDataReadyUsingReadsCallback,
) -> PicoDataReadyUsingReadsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoDataReadyUsingReadsCallback
	:return: C function pointer according to "PicoDataReadyUsingReads"
		typedef.
	:rtype: PicoDataReadyUsingReadsCType
	"""
	holder = "__ps6000a_PicoDataReadyUsingReadsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		read: int,  # Value should be in PicoReadSelection enum.
		status: int,  # Value should be in PicoStatus enum.
		from_segment_index: int,
		to_segment_index: int,
		parameter: c_void_p,
	) -> None:
		callback(
			PicoHandle(handle),
			PicoReadSelection(read),
			PicoStatus(status),
			from_segment_index,
			to_segment_index,
		)

	out = PicoDataReadyUsingReadsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoExternalReferenceInteractions


class PicoExternalReferenceInteractionsCallback(Protocol):
	"""Pythonized version of PicoExternalReferenceInteractions C function type."""

	def __call__(
		self, handle: PicoHandle, status: PicoStatus, reference: PicoClockReference
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoExternalReferenceInteractionsCType(_CData):
		"""PicoExternalReferenceInteractions C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoExternalReferenceInteractionsCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_uint32
	)


def wrap_pico_external_reference_interactions(
	callback: PicoExternalReferenceInteractionsCallback,
) -> PicoExternalReferenceInteractionsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoExternalReferenceInteractionsCallback
	:return: C function pointer according to "PicoExternalReferenceInteractions"
		typedef.
	:rtype: PicoExternalReferenceInteractionsCType
	"""
	holder = "__ps6000a_PicoExternalReferenceInteractionsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		reference: int,  # Value should be in PicoClockReference enum.
	) -> None:
		callback(PicoHandle(handle), PicoStatus(status), PicoClockReference(reference))

	out = PicoExternalReferenceInteractionsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoAWGOverrangeInteractions


class PicoAWGOverrangeInteractionsCallback(Protocol):
	"""Pythonized version of PicoAWGOverrangeInteractions C function type."""

	def __call__(self, handle: PicoHandle, status: PicoStatus) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoAWGOverrangeInteractionsCType(_CData):
		"""PicoAWGOverrangeInteractions C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoAWGOverrangeInteractionsCType = WINFUNCTYPE(None, c_int16, c_uint32)


def wrap_pico_awg_overrange_interactions(
	callback: PicoAWGOverrangeInteractionsCallback,
) -> PicoAWGOverrangeInteractionsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoAWGOverrangeInteractionsCallback
	:return: C function pointer according to "PicoAWGOverrangeInteractions"
		typedef.
	:rtype: PicoAWGOverrangeInteractionsCType
	"""
	holder = "__ps6000a_PicoAWGOverrangeInteractionsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int, status: int  # Value should be in PicoStatus enum.
	) -> None:
		callback(PicoHandle(handle), PicoStatus(status))

	out = PicoAWGOverrangeInteractionsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoTemperatureSensorInteractions


class PicoTemperatureSensorInteractionsCallback(Protocol):
	"""Pythonized version of PicoTemperatureSensorInteractions C function type."""

	def __call__(
		self, handle: PicoHandle, temperature_status: PicoTemperatureReference
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoTemperatureSensorInteractionsCType(_CData):
		"""PicoTemperatureSensorInteractions C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoTemperatureSensorInteractionsCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_uint32
	)


def wrap_pico_temperature_sensor_interactions(
	callback: PicoTemperatureSensorInteractionsCallback,
) -> PicoTemperatureSensorInteractionsCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoTemperatureSensorInteractionsCallback
	:return: C function pointer according to "PicoTemperatureSensorInteractions"
		typedef.
	:rtype: PicoTemperatureSensorInteractionsCType
	"""
	holder = "__ps6000a_PicoTemperatureSensorInteractionsCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		temperature_status: int,  # Value should be in PicoTemperatureReference enum.
	) -> None:
		callback(PicoHandle(handle), PicoTemperatureReference(temperature_status))

	out = PicoTemperatureSensorInteractionsCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out


# PicoProbeUserAction


class PicoProbeUserActionCallback(Protocol):
	"""Pythonized version of PicoProbeUserAction C function type."""

	def __call__(
		self,
		handle: PicoHandle,
		status: PicoStatus,
		channel: PicoChannel,
		probe: PicoConnectProbe,
		action: PicoProbeUserAction,
		action_parameter: Union[PicoProbeButtonPressParameter],
	) -> None:
		"""Handle callback call."""
		...


if TYPE_CHECKING:

	class PicoProbeUserActionCType(_CData):
		"""PicoProbeUserAction C function type."""

		# noinspection PyMissingConstructor
		def __init__(self, arg: Callable):
			"""Create C function pointer from Python function."""
			pass

else:
	PicoProbeUserActionCType = WINFUNCTYPE(
		None, c_int16, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p, c_void_p
	)


def wrap_pico_probe_user_action(
	callback: PicoProbeUserActionCallback,
) -> PicoProbeUserActionCType:
	"""
	Create C function pointer from compatible Python function.

	:param callback: The Python function to make a pointer to.
	:type callback: PicoProbeUserActionCallback
	:return: C function pointer according to "PicoProbeUserAction" typedef.
	:rtype: PicoProbeUserActionCType
	"""
	holder = "__ps6000a_PicoProbeUserActionCType"
	if hasattr(callback, holder):
		return getattr(callback, holder)[1]  # type: ignore

	def _callback(
		handle: int,
		status: int,  # Value should be in PicoStatus enum.
		channel: int,  # Value should be in PicoChannel enum.
		probe: int,  # Value should be in PicoConnectProbe enum.
		action: int,  # Value should be in PicoProbeUserAction enum.
		action_parameter: c_void_p,
		parameter: c_void_p,
	) -> None:
		pico_probe_button_press_parameter_p_t = POINTER(PicoProbeButtonPressParameter)
		py_action = PicoProbeUserAction(action)
		if py_action is PicoProbeUserAction.BUTTON_PRESS:
			py_action_parameter = c_cast(
				action_parameter, pico_probe_button_press_parameter_p_t
			).contents
		else:
			raise RuntimeError(f"Cannot handle action {action}.")
		callback(
			PicoHandle(handle),
			PicoStatus(status),
			PicoChannel(channel),
			PicoConnectProbe(probe),
			py_action,
			py_action_parameter,
		)

	out = PicoProbeUserActionCType(_callback)
	setattr(callback, holder, (_callback, out))
	return out
