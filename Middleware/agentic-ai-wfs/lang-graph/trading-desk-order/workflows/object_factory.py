from workflows.interfaces import DeskAgentWf


class WorkflowObjectFactory:
    _agents: dict[str, DeskAgentWf] = {}

    @classmethod
    def agent(cls, name: str) -> DeskAgentWf | None:
        if not cls._agents:
            from workflows.impl.deskagentwf import OrderAgentWf

            cls._agents = {OrderAgentWf.agent_name: OrderAgentWf()}
        return cls._agents.get(name)

    @classmethod
    def names(cls) -> list[str]:
        cls.agent("trading-desk-order")
        return sorted(cls._agents)
