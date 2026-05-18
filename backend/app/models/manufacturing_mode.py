"""Manufacturing mode profile constants.

The pilot runtime is discrete-first, but the product must not become
discrete-only. These constants record the supported profile values without
introducing batch/process execution behavior.
"""

MANUFACTURING_MODE_PROFILE_DISCRETE = "DISCRETE"
MANUFACTURING_MODE_PROFILE_BATCH_PROCESS = "BATCH_PROCESS"

SUPPORTED_MANUFACTURING_MODE_PROFILES = (
    MANUFACTURING_MODE_PROFILE_DISCRETE,
    MANUFACTURING_MODE_PROFILE_BATCH_PROCESS,
)

