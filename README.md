# Chat with Meta's LLaMA models at home made easy

This repository is a chat example with [LLaMA](https://ai.facebook.com/blog/large-language-model-llama-meta-ai/) ([arXiv](https://arxiv.org/abs/2302.13971v1)) models running on a typical home PC. You will just need a NVIDIA videocard and some RAM to chat with model.

By using HF version you may fine-tune the model to any desired task.

## Copyright

This repo is heavily based on Meta's original repo: https://github.com/facebookresearch/llama

And on Steve Manuatu's repo: https://github.com/venuatu/llama

And on Shawn Presser's repo: https://github.com/shawwn/llama

[HF 🤗 version](https://github.com/randaller/llama-chat#hugging-face--version-inference--training) by Yam Peleg and Jason Phang: https://github.com/ypeleg/llama & https://github.com/zphang

## Examples of chats here

https://github.com/facebookresearch/llama/issues/162

Share your best prompts, chats or generations here in this issue: https://github.com/randaller/llama-chat/issues/7

## System requirements
- Modern enough CPU
- NVIDIA graphics card (2 Gb of VRAM is ok); HF version is able to run on CPU, or mixed CPU/GPU, or pure GPU
- 64 or better 128 Gb of RAM (192 would be perfect for 65B model)

One may run with 32 Gb of RAM, but inference will be slow (with the speed of your swap file reading)

I am running PyArrow version on a [12700k/128 Gb RAM/NVIDIA 3070ti 8Gb/fast huge nvme with 256 Gb swap for 65B model] and getting one token from 30B model in a few seconds.

For example, **PyArrow 30B model uses around 70 Gb of RAM**. 7B model fits into 18 Gb. 13B model uses 48 Gb.

If you do not have nvidia videocard, you may use another repo for cpu-only inference: https://github.com/randaller/llama-cpu or [HF 🤗 version](https://github.com/randaller/llama-chat#hugging-face--version-inference--training).

## Installation

### Download the repo

```
git clone https://github.com/randaller/llama-chat.git
cd llama-chat
```

### Conda Environment Setup Example for Windows 10+
Download and install Anaconda Python https://www.anaconda.com and run Anaconda Prompt
```
conda create -n llama python=3.10
conda activate llama
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
```

### Install requirements
In a conda env with pytorch / cuda available, run
```
pip install -r requirements.txt
```
Then in this repository
```
pip install -e .
```

## PyArrow version (inference only)

### Download tokenizer and models
magnet:?xt=urn:btih:ZXXDAUWYLRUXXBHUYEMS6Q5CE5WA3LVA&dn=LLaMA

or

magnet:?xt=urn:btih:b8287ebfa04f879b048d4d4404108cf3e8014352&dn=LLaMA&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce

### Prepare model

First, you need to unshard model checkpoints to a single file. Let's do this for 30B model.

```
python merge-weights.py --input_dir D:\Downloads\LLaMA --model_size 30B
```

In this example, D:\Downloads\LLaMA is a root folder of downloaded torrent with weights.

This will create merged.pth file in the root folder of this repo.

Place this file and corresponding (torrentroot)/30B/params.json of model into [/model] folder.

So you should end up with two files in [/model] folder: merged.pth and params.json.

Place (torrentroot)/tokenizer.model file to the [/tokenizer] folder of this repo. Now you are ready to go.

### Run the chat

```
python example-chat.py ./model ./tokenizer/tokenizer.model
```

### Generation parameters

![image](https://user-images.githubusercontent.com/22396871/224481306-0079dc71-a659-46f2-96a3-38d8a0b8bafc.png)

**Temperature** is one of the key parameters of generation. You may wish to play with temperature. The more temperature is, the model will use more "creativity", and the less temperature instruct model to be "less creative", but following your prompt stronger.

**Repetition penalty** is a feature implemented by Shawn Presser. With this, the model will be fined, when it would like to enter to repetion loop state. Set this parameter to 1.0, if you wish to disable this feature.

**Samplers**

By default, Meta provided us with top_p sampler only. Again, Shawn added an alternate top_k sampler, which (in my tests) performs pretty well. If you wish to switch to top_k sampler, use the following parameters:

```
temperature: float = 0.7,
top_p: float = 0.0,
top_k: int = 40,
sampler: str = 'top_k',
```

For sure, you may play with all the values to get different outputs.

**Launch examples**

One may modify these hyperparameters straight in the code. But it is better to leave the defaults in code and set the parameters of experiments in the launch line.

```
# Run with top_p sampler, with temperature 0.75, with top_p value 0.95, repetition penalty disabled
python example-chat.py ./model ./tokenizer/tokenizer.model 0.75 0.95 0 1.0 top_p

# Run with top_k sampler, with temperature 0.7, with top_k value 40, default repetition penalty value
python example-chat.py ./model ./tokenizer/tokenizer.model 0.7 0.0 40 1.17 top_k
```

Of course, this is also applicable to a [python example.py] as well (see below).


### Enable multi-line answers

If you wish to stop generation not by "\n" sign, but by another signature, like "User:" (which is also good idea), or any other, make the following modification in the llama/generation.py:

![image](https://user-images.githubusercontent.com/22396871/224122767-227deda4-a718-4774-a7f9-786c07d379cf.png)

-5 means to remove last 5 chars from resulting context, which is length of your stop signature, "User:" in this example.

### Share the best with community

Share your best prompts and generations with others here: https://github.com/randaller/llama-chat/issues/7

### Typical generation with prompt (not a chat)

Simply comment three lines in llama/generation.py to turn it to a generator back.

![image](https://user-images.githubusercontent.com/22396871/224283389-e29de04e-28d1-4ccd-bf6b-81b29828d3eb.png)

```
python example.py ./model ./tokenizer/tokenizer.model
```

Confirming that 30B model is able to generate code and fix errors in code: https://github.com/randaller/llama-chat/issues/7

Confirming that 30B model is able to generate prompts for Stable Diffusion: https://github.com/randaller/llama-chat/issues/7#issuecomment-1463691554

Confirming that 7B and 30B model support Arduino IDE: https://github.com/randaller/llama-chat/issues/7#issuecomment-1464179944

Confirming that 30B model is able to generate SQL code: https://github.com/randaller/llama-chat/issues/7#issuecomment-1467861922

## Hugging Face 🤗 version (inference & training)

### Inference

Thanks to Yam Peleg, we now have *"No overengineering bullshit"* version.

You do not need to download torrent or merge weights, as model shards and tokenizer will be downloaded from HF automatically at the first run. They will be cached in [C:\Users\USERNAME\\.cache\huggingface\hub] folder under Windows, so do not forget to clean up to 250 Gb after experiments.

```
python hf-inference-example.py
```

### Chatting

```
python hf-chat-example.py
```

### Training

Prepare your dataset, edit the training example to define your dataset file and launch training. Dataset file with strings should be in UTF-8 encoding.

![image](https://user-images.githubusercontent.com/22396871/226167997-475b806a-e257-4628-979c-d15df4b3bc5c.png)
```
python hf-training-example.py
```
Trained model will be saved into [./trained] folder. Now launch chat or inference example with freshly trained model:

```
python hf-chat-example.py
```
```
python hf-inference-example.py
```

### Bfloat16 training and inference optimization

To save CPU RAM or GPU VRAM memory, one may wish to enable Bfloat16 processing.

```
# to save memory use bfloat16
import torch
torch.set_default_dtype(torch.bfloat16)
```

### Offload to GPU with accelerate

```
device_map = infer_auto_device_map(model, max_memory={0: "6GiB", "cpu": "128GiB"})
```

One with A100 might try to set 38Gb to a GPU0 and try to inference the model completely in the GPU VRAM.

One with 4*A100 might wish to use: {0: "38GiB", 1: "38GiB", 2: "38GiB", 3: "38GiB", "cpu":"128GiB"}.

For me, with 7Gb for 3070ti, for 7B model, this works at the same speed as pure CPU inference.

```
python hf-inference-cuda-example.py
```

### How to fine-tune LLaMA for Stable Diffusion prompting

Modify hf-training-example.py, also feel free to use more or less lines of SD prompts examples in csv file:

```
MODEL = 'decapoda-research/llama-7b-hf'
DATA_FILE_PATH = 'datasets/stable_diffusion_prompts.csv'
OUTPUT_DIR = './trained'
```

*Note: You may also prepare your own dataset, for example, with Prompt: and Negative prompt: and even Steps Sampler etc lines interleaving or single-lined in csv. Max length of each data string should not exceed LLaMA's 2048 tokens.*

Then run the training, then after a long-long time, use something like this as a prompt for LLaMA to generate SD prompts:

```
batch = tokenizer("A portrait of a beautiful girl, ", return_tensors="pt")
```

*Note: If you have prepared and used own dataset with Prompt: Negative prompt: lines, the initial LLaMA prompt may look like:*

```
batch = tokenizer("Prompt: A warship flying thru the Wormhole, ", return_tensors="pt")
```

Run inference, this should return continued prompt for SD.

## Reference

LLaMA: Open and Efficient Foundation Language Models -- https://arxiv.org/abs/2302.13971

```
@article{touvron2023llama,
  title={LLaMA: Open and Efficient Foundation Language Models},
  author={Touvron, Hugo and Lavril, Thibaut and Izacard, Gautier and Martinet, Xavier and Lachaux, Marie-Anne and Lacroix, Timoth{\'e}e and Rozi{\`e}re, Baptiste and Goyal, Naman and Hambro, Eric and Azhar, Faisal and Rodriguez, Aurelien and Joulin, Armand and Grave, Edouard and Lample, Guillaume},
  journal={arXiv preprint arXiv:2302.13971},
  year={2023}
}
```
