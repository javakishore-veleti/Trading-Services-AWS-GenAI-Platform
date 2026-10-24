from business.interfaces import DeskAgentBiz


class BusinessObjectFactory:
    _agents: dict[str, DeskAgentBiz] = {}

    @classmethod
    def agent_biz(cls, agent: str) -> DeskAgentBiz | None:
        if agent not in cls._agents:
            from business.impl.agentbiz import OrderAgentBiz

            if agent != OrderAgentBiz.agent_name:
                return None
            cls._agents[agent] = OrderAgentBiz()
        return cls._agents.get(agent)
