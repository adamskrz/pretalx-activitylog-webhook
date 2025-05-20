import uuid

from celery import states
from django.core import validators
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields import DateTimeField


class ActivitylogWebhookSettings(models.Model):
    event = models.OneToOneField(
        to="event.Event",
        on_delete=models.CASCADE,
        related_name="pretalx_activitylog_webhook_settings",
    )
    some_setting = models.CharField(max_length=10, default="A")


# Webhook models from django-webhook Copyright (c) 2023 Dani Hodovic
class Webhook(models.Model):
    url = models.URLField()
    pretalx_event = models.ForeignKey(
        to="event.Event",
        on_delete=models.CASCADE,
        related_name="pretalx_activitylog_webhooks",
    )
    active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)

    @property
    def action_types(self):
        # returns a simple list of strings
        return list(self._action_types.values_list("action_type", flat=True))

    def set_action_types(self, new_list):
        self._action_types.all().delete()
        objs = [WebhookActionType(webhook=self, action_type=at) for at in new_list]
        WebhookActionType.objects.bulk_create(objs)

    def __str__(self):
        return f"id={self.id} active={self.active}"


class WebhookActionType(models.Model):  # type: ignore
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name="_action_types",
    )
    action_type = models.CharField(
        max_length=200,
        # choices=LOG_NAMES,
    )

    class Meta:
        unique_together = ("webhook", "action_type")

    def __str__(self):
        return f"{self.webhook} - {self.action_type}"


class WebhookSecret(models.Model):
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name="secrets",
        related_query_name="secret",
        editable=False,
    )
    token = models.CharField(
        max_length=100,
        validators=[validators.MinLengthValidator(12)],
    )
    created = DateTimeField(auto_now_add=True)


class WebhookEvent(models.Model):
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name="events",
        related_query_name="event",
    )
    object = models.JSONField(
        max_length=1000,
        encoder=DjangoJSONEncoder,
        editable=False,
    )
    STATES = [
        (states.PENDING, states.PENDING),
        (states.FAILURE, states.FAILURE),
        (states.SUCCESS, states.SUCCESS),
    ]
    status = models.CharField(
        max_length=40,
        default=states.PENDING,
        choices=STATES,
        editable=False,
    )
    created = DateTimeField(auto_now_add=True)
    url = models.URLField(editable=False)
    topic = models.CharField(max_length=250, null=True, editable=False)
