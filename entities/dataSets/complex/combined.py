from census import Census
import enum

class UnitOfAnalysis(enum.Enum):
    TRACT = Enum.auto()
    FACILITY = Enum.auto()

class Combined():
    def __init__(self, census, facility, unitOfAnalysis):
        pass