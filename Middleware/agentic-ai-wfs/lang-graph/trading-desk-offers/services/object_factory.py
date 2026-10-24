from services.interfaces import AgentSvc


class ServiceObjectFactory:
    _agent_svc: AgentSvc | None = None

    @classmethod
    def agent_svc(cls) -> AgentSvc:
        if cls._agent_svc is None:
            from services.impl.agentsvc import AgentSvcImpl

            cls._agent_svc = AgentSvcImpl()
        return cls._agent_svc
