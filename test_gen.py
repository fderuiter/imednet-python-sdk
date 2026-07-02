from imednet.models.engine import ModelEngine

model = ModelEngine.get_model('Record')
for name, field in model.model_fields.items():
    print(f"{name}: {field.annotation}")
