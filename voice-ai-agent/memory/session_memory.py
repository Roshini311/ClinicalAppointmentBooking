import json

# Swapped Redis to a standard python dictionary so it runs out-of-the-box without Docker!
_mock_redis_db = {}

class SessionMemory:
    @staticmethod
    async def get_session(session_id: str) -> dict:
        data = _mock_redis_db.get(f"session:{session_id}")
        if data:
            return json.loads(data)
        return {"history": [], "language": "English"}

    @staticmethod
    async def update_session(session_id: str, data: dict):
        # Store in dict
        _mock_redis_db[f"session:{session_id}"] = json.dumps(data)

    @staticmethod
    async def add_message(session_id: str, role: str, content: str):
        session = await SessionMemory.get_session(session_id)
        session["history"].append({"role": role, "content": content})
        # Keep last 10 messages to avoid huge context
        session["history"] = session["history"][-10:]
        await SessionMemory.update_session(session_id, session)

    @staticmethod
    async def set_language(session_id: str, language: str):
        session = await SessionMemory.get_session(session_id)
        session["language"] = language
        await SessionMemory.update_session(session_id, session)
