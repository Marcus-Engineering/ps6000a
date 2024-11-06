"""Utility functions for picosave."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: util.py
#
# Utility functions for picosave.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210823       Created                                        jrowley
#
###############################################################################

from enum import IntEnum, IntFlag
from typing import Any


class FlexIntEnum(IntEnum):
	"""
	IntEnum with more flexible constructor.

	For an Enum ``Foo`` with a member ``BAR = 0``, the valid patterns would be:

	- ``Foo(0) is Foo.BAR``
	- ``Foo(Foo.BAR) is Foo.BAR``

	FlexIntEnum adds an additional pattern:

	- ``Foo("BAR") is Foo.BAR``

	Additionally, when constructed from a value that is neither the name or
	value of a member, a new "fake" member is created at runtime to enumerate
	that value. Further instantiation with the same value will return that same
	fake member.
	"""

	@classmethod
	def _missing_(cls, value: Any) -> "FlexIntEnum":
		"""
		Get a member of FlexIntEnum by name, as fallback to by value.

		Alternatively, create a new "fake" member to accomodate an unknown
		name/value.

		:param value: FlexIntEnum member name.
		:type value: Any
		"""
		try:
			return cls[value]
		except KeyError:
			fake = int.__new__(cls, value)
			fake._name_ = str(value)
			fake._value_ = value
			return cls._value2member_map_.setdefault(value, fake)  # type: ignore


class FlexIntFlag(IntFlag):
	"""
	IntFlag with more flexible constructor.

	For a Flag ``Foo`` with a member ``BAR = 1``, the valid patterns would be:

	- ``Foo(1) is Foo.BAR``
	- ``Foo(Foo.BAR) is Foo.BAR``

	FlexIntFlag adds an additional pattern:

	- ``Foo("BAR") is Foo.BAR``

	Loading of a compound flag (e.g. ``Foo.BAR | Foo.BAZ``) from string name is
	not currently supported.
	"""

	@classmethod
	def _missing_(cls, value: Any) -> "FlexIntFlag":
		"""
		Get a member of FlexIntFlag by name, as fallback to by value.

		Loading of a compound flag (e.g. ``Foo.BAR | Foo.BAZ``) from string
		name is not currently supported.

		:param value: FlexIntFlag member name.
		:type value: Any
		"""
		try:
			return super()._missing_(value)  # type: ignore
		except ValueError:
			return cls[value]
