from django import forms

class YourForm(forms.Form):
    first_name = forms.CharField(label="Customer's First Name", required=True)
    last_name = forms.CharField(label="Customer's Last Name", required=True)
    email = forms.EmailField(label="Customer's Email", required=True)
    phone_number = forms.CharField(label="Customer's Phone Number", required=True, widget=forms.TextInput(attrs={'pattern': '[0-9]{3}-[0-9]{3}-[0-9]{4}'}))
    csv_file = forms.FileField(label="CSV File", required=True)

