from uetools.unreal.unreal_config import EngineLocation, UnrealConfiguration

class UEToolsState:

    def __init__(self):

        # Instantiate and store the singleton
        self.config: UnrealConfiguration = UnrealConfiguration()