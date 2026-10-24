from workflows.interfaces import DeskAgentWf


class WorkflowObjectFactory:
    _agents: dict[str, DeskAgentWf] = {}

    @classmethod
    def agent(cls, name: str) -> DeskAgentWf | None:
        if not cls._agents:
            from workflows.impl.deskagentwf import PlatformsAgentWf

            cls._agents = {PlatformsAgentWf.agent_name: PlatformsAgentWf()}
        return cls._agents.get(name)

    @classmethod
    def names(cls) -> list[str]:
        cls.agent("trading-desk-platforms")
        return sorted(cls._agents)
