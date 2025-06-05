from django import forms
from .models import Product, Expense, Recipe, ProductionBatch, Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'type', 'amount', 'description', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'ingredients', 'instructions', 'preparation_time', 'yield_quantity', 'yield_unit']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 5}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
            'preparation_time': forms.NumberInput(attrs={'min': '0'}),
            'yield_quantity': forms.NumberInput(attrs={'min': '0'}),
            'yield_unit': forms.TextInput(attrs={'placeholder': 'e.g., pieces, kg'}),
        }

class ProductionBatchForm(forms.ModelForm):
    class Meta:
        model = ProductionBatch
        fields = ['recipe', 'batch_number', 'planned_date', 'planned_start_time', 
                 'planned_end_time', 'quantity_produced', 'quality_notes', 'status']
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'planned_end_time': forms.TimeInput(attrs={'type': 'time'}),
            'quality_notes': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(choices=ProductionBatch.STATUS_CHOICES),
            'recipe': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipe'].queryset = Recipe.objects.filter(is_active=True)
        self.fields['recipe'].empty_label = "Select a recipe"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+254 XXX XXX XXX'}),
        } 