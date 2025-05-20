import json
from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.urls import reverse
from pretalx.common.models.log import ActivityLog
from pretalx.orga.signals import nav_event_settings

from .models import Webhook
from .settings import get_settings
# from .tasks import fire_webhook
# from .util import cache


@receiver(nav_event_settings)
def pretalx_activitylog_webhook_settings(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        return []
    return [
        {
            "label": "ActvityLog Webhook plugin",
            "url": reverse(
                "plugins:pretalx_activitylog_webhook:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name == "plugins:pretalx_activitylog_webhook:settings",
        }
    ]


@receiver(post_save, sender=ActivityLog, weak=False, dispatch_uid="activitylog_webhook_handler")
def handle_activitylog_save(sender, instance, created=False, **kwargs):
    """
    Process ActivityLog saves and trigger webhooks for the action type.
    """
    action_type = instance.action_type
    webhook_ids = _find_webhooks(action_type)
    encoder_cls = get_settings()["PAYLOAD_ENCODER_CLASS"]
    model_label = ActivityLog._meta.label

    for id, uuid in webhook_ids:
        payload_dict = dict(
            object=model_dict(instance),
            action_type=action_type,
            object_type=model_label,
            webhook_uuid=str(uuid),
        )
        payload = json.dumps(payload_dict, cls=encoder_cls)
        # fire_webhook.delay(
        #     id,
        #     payload,
        #     action_type=action_type,
        #     object_type=model_label,
        # )


def model_dict(model):
    """
    Returns the model instance as a dict, nested values for related models.
    """
    fields = {field.name: field.value_from_object(model) for field in model._meta.fields}
    return model_to_dict(model, fields=fields)  # type: ignore


def _find_webhooks(topic: str):
    """
    In tests and for smaller setups we don't want to cache the query.
    """
    if get_settings()["USE_CACHE"]:
        return _query_webhooks_cached(topic)
    return _query_webhooks(topic)


# @cache(ttl=timedelta(minutes=1))
def _query_webhooks_cached(topic: str):
    """
    Cache the calls to the database so we're not polling the db anytime a signal is triggered.
    """
    return _query_webhooks(topic)


def _query_webhooks(topic: str):
    return Webhook.objects.filter(active=True, action_types__name=topic).values_list("id", "uuid")
