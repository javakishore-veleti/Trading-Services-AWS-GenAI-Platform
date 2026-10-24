from workflows.interfaces import DeskAgentWf


class WorkflowObjectFactory:
    _agents: dict[str, DeskAgentWf] = {}

    @classmethod
    def agent(cls, name: str) -> DeskAgentWf | None:
        if not cls._agents:
            from workflows.impl.deskagentwf import OffersAgentWf

            cls._agents = {OffersAgentWf.agent_name: OffersAgentWf()}
        return cls._agents.get(name)

    @classmethod
    def names(cls) -> list[str]:
        cls.agent("trading-desk-offers")
        return sorted(cls._agents)
