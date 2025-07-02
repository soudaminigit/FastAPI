import torch
import torchvision.models as models

# Load pretrained ResNet50
resnet = models.resnet50(pretrained=True)
resnet.eval()

# Create dummy input for scripting
example_input = torch.rand(1, 3, 224, 224)

# Convert to TorchScript
scripted_model = torch.jit.trace(resnet, example_input)
torch.jit.save(scripted_model, "resnet_scripted.pt")

print("✅ Model saved as 'resnet_scripted.pt'")
