"""PicoScope API-related custom exception types."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: exceptions.py
#
# PicoScope API-related custom exception types.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210818       Created.                                       jrowley
#
###############################################################################

from typing import Optional

from ps6000a.constants import PicoStatus
from ps6000a.types import PicoHandle


class PicoError(Exception):
	"""Shared base class for this module's exceptions."""


class PicoStatusError(PicoError, RuntimeError):
	"""Exception thrown when status is not ``PicoStatus.OK``."""

	status: PicoStatus

	def __init__(self, status: PicoStatus) -> None:
		"""Create PicoStatusException instance."""
		self.status = status
		if status == PicoStatus.OK:
			raise RuntimeError("PicoStatus.OK should not cause exception.")
		message = f"PicoScope operation failed with status: {status.name}"
		super(RuntimeError, self).__init__(message)


class PicoHandleError(PicoError, RuntimeError):
	"""Exception thrown when trying to operate with invalid handle."""

	handle: Optional[PicoHandle]

	def __init__(self, handle: Optional[PicoHandle]) -> None:
		"""Create PicoHandleException instance."""
		self.handle = handle
		if handle is None:
			message = (
				"Cannot operate without acquiring handle to hardware. "
				"Call PS6000A.open_unit first."
			)
		elif handle < 0:
			message = (
				"Cannot operate without valid handle: hardware failed to "
				"to open. Call PS6000A.get_unit_info for details."
			)
		elif handle == 0:
			message = "Cannot operate without valid handle: no hardware found."
		else:
			raise RuntimeError("Valid handle should not cause exception.")
		super(RuntimeError, self).__init__(message)
