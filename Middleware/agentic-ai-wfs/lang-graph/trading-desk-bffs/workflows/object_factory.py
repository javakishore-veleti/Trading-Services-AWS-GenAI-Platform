from workflows.interfaces import DeskAgentWf


class WorkflowObjectFactory:
    _agents: dict[str, DeskAgentWf] = {}

    @classmethod
    def agent(cls, name: str) -> DeskAgentWf | None:
        if not cls._agents:
            from workflows.impl.deskagentwf import BffsAgentWf

            cls._agents = {BffsAgentWf.agent_name: BffsAgentWf()}
        return cls._agents.get(name)

    @classmethod
    def names(cls) -> list[str]:
        cls.agent("trading-desk-bffs")
        return sorted(cls._agents)
