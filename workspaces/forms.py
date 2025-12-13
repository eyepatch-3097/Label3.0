from django import forms
from .models import WorkspaceField, LabelTemplate, GlobalTemplate


class WorkspaceCreateStep1Form(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Workspace Name",
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Description",
    )
    template_file = forms.FileField(
        required=False,
        label="Upload label template file (CSV)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )


FIELD_TYPE_CHOICES = WorkspaceField.FIELD_TYPE_CHOICES


class ManualFieldsForm(forms.Form):
    """
    Very simple: allow up to N manual fields at once.
    Users can leave blank ones empty.
    """
    def __init__(self, *args, **kwargs):
        num_rows = kwargs.pop('num_rows', 5)
        super().__init__(*args, **kwargs)

        for i in range(num_rows):
            self.fields[f'field_name_{i}'] = forms.CharField(
                max_length=255,
                required=False,
                widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
                label=f"Field name #{i+1}",
            )
            self.fields[f'field_type_{i}'] = forms.ChoiceField(
                required=False,
                choices=[('', '--- Select type ---')] + list(FIELD_TYPE_CHOICES),
                widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
                label=f"Field type #{i+1}",
            )

class LabelTemplateForm(forms.ModelForm):
    class Meta:
        model = LabelTemplate
        fields = [
            "name",
            "description",
            "width_cm",
            "height_cm",
            "dpi",
            "category",
            "custom_category",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        custom_category = (cleaned.get("custom_category") or "").strip()

        if category == LabelTemplate.CATEGORY_OTHERS and not custom_category:
            self.add_error(
                "custom_category",
                "Please specify a category when selecting 'Others'.",
            )
        return cleaned

class TemplateDuplicateForm(forms.Form):
    name = forms.CharField(
        label="Template Name",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )

class GlobalTemplateForm(forms.ModelForm):
    class Meta:
        model = GlobalTemplate
        fields = [
            "name",
            "description",
            "width_cm",
            "height_cm",
            "dpi",
            "category",
            "custom_category",
        ]