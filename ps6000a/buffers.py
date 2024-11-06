"""Encapsulation for data buffers registed with the driver."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: buffers.py
#
# Encapsulation for data buffers registed with the driver.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210818       Created.                                       jrowley
#
###############################################################################

from ctypes import Array
from dataclasses import dataclass, field
from enum import Enum, auto

from ps6000a.constants import PicoChannel, PicoDataType, PicoRatioMode
from ps6000a.types import PicoStreamingDataInfo


class BufferMaxMin(Enum):
	"""
	Represents buffer "max" (normal) or "min" type.

	:cvar MAX: A buffer to receive the maximum data values in aggregation mode,
		or the non-aggregated values otherwise.
	:cvar MIN: A buffer to receive the minimum aggregated data values. Not used
		in other downsampling modes.
	"""

	MAX = auto()
	MIN = auto()


@dataclass(frozen=True)
class BufferClass:
	# noinspection PyUnresolvedReferences
	"""
	Describes a class of buffers.

	Calls to ``get_data_buffer(s)`` will affect all existing buffers in
	the same "class", as defined by the attributes of this dataclass.

	:ivar channel: The oscilloscope channel.
	:type channel: PicoChannel
	:ivar datatype: The datatype of buffer elements.
	:type datatype: PicoDataType
	:ivar segment: The segment index.
	:type segment: int
	"""

	channel: PicoChannel
	datatype: PicoDataType
	segment: int


@dataclass(frozen=True)
class Buffer:
	# noinspection PyUnresolvedReferences
	"""
	Describes a data buffer.

	:ivar buffer: The actual buffer.
	:type buffer: Array[PicoDataType.ctype]
	:ivar channel: The associated oscilloscope channel.
	:type channel: PicoChannel
	:ivar datatype: The datatype of the buffer elements.
	:type datatype: PicoDataType
	:ivar segment: The associated segment index.
	:type segment: int
	:ivar downsampling_mode: The downsampling mode for this buffer.
	:type downsampling_mode: PicoRatioMode
	:ivar max_min: Whether buffer is "min" or "max" type. Optional, defaults to
		``BufferMaxMin.MAX`` (normal mode).
	:type max_min: BufferMaxMin
	"""

	buffer: Array = field(compare=False)
	channel: PicoChannel
	datatype: PicoDataType
	segment: int
	downsampling_mode: PicoRatioMode
	max_min: BufferMaxMin = BufferMaxMin.MAX

	@property
	def buffer_class(self) -> BufferClass:
		"""
		Get subset of contained data as ``BufferClass`` object.

		:getter: Get subset of contained data as ``BufferClass`` object.
		:setter: None, computed/read-only.
		:return: Subset of contained data as ``BufferClass`` object.
		:rtype: BufferClass
		"""
		return BufferClass(
			channel=self.channel, datatype=self.datatype, segment=self.segment
		)

	@property
	def empty_streaming_info(self) -> PicoStreamingDataInfo:
		"""
		Get subset of contained data as ``PicoStreamingDataInfo`` structure.

		The necessary fields for use with ``get_streaming_latest_values`` will
		be set. Others will be uninitialized.

		:getter: Get subset of contained data as ``PicoStreamingDataInfo``
			structure.
		:setter: None, computed/read-only.
		:return: Subset of contained data as ``PicoStreamingDataInfo``
			structure.
		:rtype: PicoStreamingDataInfo
		"""
		return PicoStreamingDataInfo(
			self.channel, self.downsampling_mode, self.datatype
		)

	@property
	def samples(self) -> int:
		"""
		Get length of the buffer, in samples.

		:getter: Get length of the buffer, in samples.
		:setter: None, computed/read-only.
		:return: Length of the buffer, in samples.
		:rtype: int
		"""
		return len(self.buffer)
