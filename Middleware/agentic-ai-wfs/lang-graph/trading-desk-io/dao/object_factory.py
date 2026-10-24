from dao.interfaces import ContextDao, McpToolDao, SkillDao


class DaoObjectFactory:
    _mcp: McpToolDao | None = None
    _context: ContextDao | None = None
    _skills: SkillDao | None = None

    @classmethod
    def mcp_dao(cls) -> McpToolDao:
        if cls._mcp is None:
            from dao.impl.mcpdao import McpToolDaoImpl

            cls._mcp = McpToolDaoImpl()
        return cls._mcp

    @classmethod
    def context_dao(cls) -> ContextDao:
        if cls._context is None:
            from dao.impl.contextdao import RedisContextDao

            cls._context = RedisContextDao()
        return cls._context

    @classmethod
    def skill_dao(cls) -> SkillDao:
        if cls._skills is None:
            from dao.impl.skilldao import FileSkillDao

            cls._skills = FileSkillDao()
        return cls._skills
