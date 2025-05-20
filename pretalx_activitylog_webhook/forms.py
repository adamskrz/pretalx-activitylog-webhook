
from django import forms
from i18nfield.forms import I18nModelForm

from pretalx.common.forms.widgets import EnhancedSelectMultiple
from pretalx.common.log_display import LOG_NAMES
from pretalx.event.models import Event

from .models import ActivitylogWebhookSettings, WebhookActionType, Webhook



class WebhookForm(forms.ModelForm):
    action_types = forms.MultipleChoiceField(
        choices=LOG_NAMES.items(),
        widget=EnhancedSelectMultiple,
        required=True,
        label="Activity Types",
        help_text="Select which activity types should trigger this webhook",
    )

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
