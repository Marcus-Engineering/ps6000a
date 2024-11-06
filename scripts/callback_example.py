"""Sample program for PS6000A API external reference driver callback."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: callback_example.py
#
# Sample program for PS6000A API external reference driver callback.
#
# When connecting/disconnecting an external 10MHz clock reference to the unit,
# you should see EXTERNAL_REF/INTERNAL_REF print out to the terminal (from the
# ``ref_callback`` function).
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210901       Created.                                       jrowley
#
###############################################################################

import time

from ps6000a.callbacks import wrap_pico_external_reference_interactions
from ps6000a.constants import PicoClockReference, PicoDeviceResolution, PicoStatus
from ps6000a.exceptions import PicoStatusError
import ps6000a.functions as ll
from ps6000a.types import PicoHandle


def ref_callback(
	handle: PicoHandle, status: PicoStatus, reference: PicoClockReference
) -> None:
	"""
	Handle change of reference source.

	This implements PicoExternalReferenceInterationsCallback.

	When the driver calls this it will run in an anonymous thread via ctypes
	magic. That also means it can't be debugged by normal means.
	"""
	if status != PicoStatus.OK:
		raise PicoStatusError(status)
	print(reference.name)


# Turn callback into a Real C Function Pointer
_c_ref_callback = wrap_pico_external_reference_interactions(ref_callback)

# Open device.
status, handle = ll.open_unit(None, PicoDeviceResolution.DR_8BIT)
if status != PicoStatus.OK:
	raise PicoStatusError(status)
print("Ready...")

# Register callback.
status = ll.set_external_reference_interaction_callback(handle, _c_ref_callback)
if status != PicoStatus.OK:
	raise PicoStatusError(status)

# Wait for user to kill script.
# The driver will call ``ref_callback`` in another (anonymous) thread.
try:
	while True:
		time.sleep(1.0)
except KeyboardInterrupt:
	pass

# Close device.
status = ll.close_unit(handle)
if status != PicoStatus.OK:
	raise PicoStatusError(status)
