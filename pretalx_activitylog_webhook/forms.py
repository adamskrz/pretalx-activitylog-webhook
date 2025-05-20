from django import forms
from i18nfield.forms import I18nModelForm

from pretalx.common.forms.widgets import EnhancedSelectMultiple
from pretalx.common.log_display import LOG_NAMES
from pretalx.event.models import Event

from .models import Webhook, ActivitylogWebhookSettings

class WebhookForm(I18nModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['action_types'].initial = self.instance.action_types


    action_types = forms.MultipleChoiceField(
        choices=LOG_NAMES.items(),
        widget=EnhancedSelectMultiple,
        required=True,
        label="Activity Types",
        help_text="Select which activity types should trigger this webhook",
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save instance first if not yet saved (so it has a PK)
        if commit:
            instance.save()
        # Update action_types M2M
        action_types = self.cleaned_data.get('action_types', [])
        instance.set_action_types(action_types)
        return instance

    class Meta:
        model = Webhook
        fields = ['url', 'active', 'action_types']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com/webhook'}),
        }


# Create a formset for handling multiple webhooks
WebhookFormSet = forms.inlineformset_factory(
    Event,
    Webhook,
    form=WebhookForm,
    extra=1,
    can_delete=True,
)


class ActivitylogWebhookSettingsForm(I18nModelForm):
    action_types = forms.MultipleChoiceField(
        choices=LOG_NAMES,
        widget=EnhancedSelectMultiple,
        required=True,
        label="Activity Types",
        help_text="Select which activity types should trigger this webhook",
    )

    def __init__(self, *args, event=None, **kwargs):
        self.instance, _ = ActivitylogWebhookSettings.objects.get_or_create(event=event)
        super().__init__(*args, **kwargs, instance=self.instance, locales=event.locales)

        # formset = WebhookFormSet(instance=event)


    class Meta:
        model = ActivitylogWebhookSettings
        fields = ("some_setting",)
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'https://example.com/webhook'}),
        }
