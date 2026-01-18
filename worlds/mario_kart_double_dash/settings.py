import settings

class MkddSettings(settings.Group):
    class DolphinProcessName(str):
        """The name of the Dolphin process to connect to. Leave blank for system default."""

    dolphin_process_name: DolphinProcessName = ""
