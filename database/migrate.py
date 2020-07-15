import json
import pathlib
from datetime import datetime

from .database import session
from .models import (Category, Channel, ChannelEmoji, Guild, Melon, Message,
                     ReactionRole, Tag)

path = pathlib.Path(__file__).parent.absolute()


def main():
    with open(f"{path}/database-old/channels.json") as f:
        channels = json.loads(f.read())
        for c in channels:
            channel = session.query(Channel).filter(Channel.channel_id == c["id"]).first()
            if not channel:
                channel = Channel(channel_id=c["id"],
                                  poll_channel=c["poll"] if "poll" in c else False)
                session.add(channel)
            if "defaultemojis" in c:
                for emoji in c["defaultemojis"]:
                    emoji = ChannelEmoji(channel_id=c["id"],
                                         emoji=emoji,
                                         default_emoji=True)
                    session.add(emoji)
            if "emojis" in c:
                for emoji in c["emojis"]:
                    emoji = ChannelEmoji(channel_id=c["id"],
                                         emoji=emoji)
                    session.add(emoji)

    with open(f"{path}/database-old/melons.json") as f:
        melon_categories = json.loads(f.read())
        for mc in melon_categories:
            category = session.query(Category).filter(Category.name == mc).first()
            if not category:
                category = Category(name=mc)
                session.add(category)
            for m in melon_categories[mc]:
                melon = session.query(Melon).filter(Melon.key == m["key"]).first()
                if not melon:
                    melon = Melon(
                        key=m["key"],
                        value=m["value"],
                        uses=m["uses"],
                        created_by=m["creator"] if "creator" in m else None,
                        created_at=datetime.utcfromtimestamp(m["created"]) if "created" in m else None,
                        category=category)
                    session.add(melon)
                if "tags" in m:
                    for t in m["tags"]:
                        tag = session.query(Tag).filter(Tag.value == t).first()
                        if not tag:
                            tag = Tag(value=t)
                            session.add(tag)
                        melon.tags.append(tag)

    with open(f"{path}/database-old/guilds.json") as f:
        guilds = json.loads(f.read())
        for g in guilds:
            guild = session.query(Guild).filter(Guild.guild_id == g["id"]).first()
            if not guild:
                guild = Guild(guild_id=g["id"],
                              melon_role=g["tagrole"] if "tagrole" in g else None)
                session.add(guild)
            if "melons" in g:
                for mc in g["melons"]:
                    category = session.query(Category).filter(Category.name == mc).first()
                    if category:
                        guild.categories.append(category)
            if "tags" in g:
                for m in g["tags"]:
                    melon = session.query(Melon).filter(Melon.key == m["key"]).first()
                    if not melon:
                        melon = Melon(
                            key=m["key"],
                            value=m["value"],
                            uses=m["uses"],
                            created_by=m["creator"] if "creator" in m else None,
                            created_at=datetime.utcfromtimestamp(m["created"]) if "created" in m else None,
                            guild=guild)
                        session.add(melon)
                    if "tags" in m:
                        for t in m["tags"]:
                            tag = session.query(Tag).filter(Tag.value == t).first()
                            if not tag:
                                tag = Tag(value=t)
                                session.add(tag)
                            melon.tags.append(tag)

    with open(f"{path}/database-old/reactroles.json") as f:
        messages = json.loads(f.read())
        for m in messages:
            message = session.query(Message).filter(Message.message_id == m["msg"]).first()
            if not message:
                message = Message(message_id=m["msg"])
                session.add(message)
            for rr in m["reactroles"]:
                emoji = rr["emoji"] if len(
                    rr["emoji"].split(":")) != 3 else f"<:{rr['emoji'].split(':')[1]}:{rr['emoji'].split(':')[2]}>"
                reaction_role = ReactionRole(message=message,
                                             role=rr["role"],
                                             emoji=emoji)
                session.add(reaction_role)

    session.commit()


if __name__ == "__main__":
    main()
