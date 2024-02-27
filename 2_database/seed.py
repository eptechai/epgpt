import asyncio
import datetime
import json
import os

from gen_dist.client.client import Prisma
from gen_dist.client.enums import MessageAuthor
from gen_dist.client.models import Conversation, ConversationPermission, Message, Tag

DEBUG = os.environ.get("DEBUG", False)

firms = {
    "Technology Services": [
        "HealthStream",
        "Zillow Group",
        "Karooooo",
        "Pagaya",
    ],
    "Enterprise Software": [
        "nCino",
        "C3ai",
        "IBM",
        "SAP",
    ],
    "Data Management and Analytics": [
        "Zoominfo Technologies",
        "Fair Isaac",
    ],
}


async def seed_firms(db) -> None:
    for subsector, companies in firms.items():
        subsector_record = await db.subsector.create(
            {"name": subsector, "owner": "GLOBAL"}
        )
        for company in companies:
            await db.company.create(
                data={
                    "name": company,
                    "subSectorId": subsector_record.id,
                    "toolName": company,
                    "owner": "GLOBAL",
                }
            )


async def main() -> None:
    db = Prisma(auto_register=True)
    try:
        await db.connect()

        await seed_firms(db)

        if DEBUG:
            conversation = await Conversation.prisma().create(
                data={
                    "parameters": json.dumps(
                        {
                            "k": 5,
                            "max_new_token": 200,
                            "top_k": 5,
                            "score_threshold": 0.8,
                            "temperature": 0.25,
                            "repetition_penalty": 1.1,
                            "use_only_uploaded": False,
                        }
                    ),
                    "vectorDbPath": "dummy_vector_db_path",
                    "updatedAt": datetime.datetime.now(),
                    "status": "IDLE",
                }
            )

            conversation_owner = await ConversationPermission.prisma().create(
                data={
                    "conversationId": conversation.id,
                    "userId": "Krishna",
                    "role": "OWNER",
                }
            )

            await Message.prisma().create(
                data={
                    "author": MessageAuthor.USER,
                    "text": "dummy_text",
                    "updatedAt": datetime.datetime.now(),
                    "conversationId": conversation.id,
                }
            )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
