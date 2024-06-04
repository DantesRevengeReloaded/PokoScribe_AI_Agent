import transformers
import torch

model_dir = "/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/Meta-Llama"

pipeline = transformers.pipeline(
  "text-generation",
  model=model_dir,
  model_kwargs={"torch_dtype": torch.bfloat16},
  device="cuda",
)