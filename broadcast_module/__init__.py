import logging
import time
from typing import Any, Dict, Optional, Tuple, Union, Literal
from synapse.api.errors import Codes

import attr
from synapse.module_api import EventBase, ModuleApi, run_as_background_process, NOT_SPAM

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class EimisBroadcastConfig:
    url1: Optional[str] = None
    url2: Optional[str] = None

class EimisBroadcast:
    def __init__(self, config: EimisBroadcastConfig, api: ModuleApi):
        self._api = api
        self._config = config

        logger.info(
            "Accepting broadcast on this worker (here: %r)", self._api.worker_name
        )

        self._api.register_third_party_rules_callbacks(
            check_event_allowed=self.check_event_allowed
            # on_new_event=self.on_new_event,
        )

        self._api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )

    @staticmethod
    def parse_config(config: Dict[str, Any]) -> EimisBroadcastConfig:
        """Instantiates a EimisBroadcastConfig.

        Args:
            config: The raw configuration dict.

        Returns:
            A EimisBroadcastConfig generated from this configuration
        """

        return EimisBroadcastConfig(
            url1=config.get("url1", None),
            url2=config.get("url2", None)
        )

    async def check_event_allowed(
        self,
        event: "synapse.events.EventBase",
        state_events: "synapse.types.StateMap",
    ) -> Tuple[bool, Optional[dict]]:
        """Listens for invitations, invite the linked user.

        Args:
            event: The incoming event.
        """
        logger.debug(f"check_event_allowed {event} ")
        if (
            event.type == "m.room.member"
            and event.is_state()
            and event.membership == "invite"
        ):
            run_as_background_process(
                "invite_aliases",
                self._invite_aliases,
                event.sender,
                event.state_key,
                event.room_id,
                bg_start_span=False,
            )
        return True, None

    async def check_event_for_spam(self, event: "synapse.events.EventBase") -> Union[Literal["NOT_SPAM"], Codes]:
        """Listens for new events, if it's a message, mark it as read for the linked user.

        Args:
            event: The incoming event.
        """
        logger.debug(f"check_event_for_spam {event} ")
        if event.type == "m.room.encrypted" or event.type == "m.room.message":
            run_as_background_process(
                "mark_as_read",
                self._send_alias_read_receipt,
                event.event_id,
                event.room_id,
                event.sender,
                bg_start_span=False,
            )
        return NOT_SPAM

    async def _invite_aliases(
        self, sender: str, target: str, room_id: str
    ) -> None:
        """

        Args:
            sender: the user performing the membership change
            target: the for whom the membership is changing
            room_id: room id of the room to join to
        """

        logger.info(
            f"Accepting {target}, inviting {target} aliases on room {room_id}")

        logger.info(f"sender {sender} local? {self._api.is_mine(sender)}")

        other_mxid_target = self._get_user_other_mx(target)
        # todo only if not already in the room
        if other_mxid_target:
            logger.info(
                f"Inviting {other_mxid_target} sender {sender} aliases on room {room_id}...")
            try:
                await self._api.update_room_membership(
                    sender=sender,
                    target=other_mxid_target,
                    room_id=room_id,
                    new_membership="invite",
                )
            except Exception as e:
                logger.info(
                    f"invite {other_mxid_target} error: {e}"
                )

    async def _send_alias_read_receipt(self, event_id: str, room_id: str, sender: str):
        ts = int(time.time())
        await self._api.sleep(1)
        local_alias = self._get_user_other_mx(sender)
        if not local_alias:
            return
        logger.info(
            f"_send_alias_read_receipt to {local_alias} sender: {sender}")
        try:
            await self._api.create_and_send_event_into_room(
                event_dict={
                    "type": "m.receipt",
                    "content": {
                        event_id: {
                            "m.read": {
                                local_alias: {
                                    "ts": ts
                                }
                            }
                        }
                    },
                    "sender": local_alias,
                    "room_id": room_id,
                },
            )
        except Exception as e:
            logger.error(f"read receipt exception: {e}")

    async def on_new_event(self,
                           event: "synapse.events.EventBase",
                           state_events: "synapse.types.StateMap",
                           ) -> None:
        """Very good to make everything crash

        Args:
            event: The incoming event.
        """
        logger.info(f"on_new_event {event} ")
        
    def _get_user_other_mx(self, user_id: str) -> str:
        """Stubb for POC : returns the user's others MXID
        Args:
            user_id: The user's MXID
        """
        localpart = user_id.split(":")[0][1:]
        if "admin" in localpart:
            return ""
        if self._api.is_mine(user_id):
            other_domain = self._get_other_MX_domain()
            return f"@{localpart}:{other_domain}"
        else:
            domain = self._api.server_name
            return f"@{localpart}:{domain}"

    def _get_other_MX_domain(self):
        if self._api.server_name.endswith(self._config.url1):
            return self._config.url2
        return self._config.url1
