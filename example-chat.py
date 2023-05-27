# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the GNU General Public License version 3.

from typing import Tuple
import os
import sys
import torch
import fire
import time
import json
import pyarrow as pa

from pathlib import Path

from llama import ModelArgs, Transformer, Tokenizer, LLaMA

torch.cuda.empty_cache()
def load(
        ckpt_dir: str,
        tokenizer_path: str,
        max_seq_len: int,
        max_batch_size: int,
) -> LLaMA:
    start_time = time.time()
    arrow_dir = Path(ckpt_dir).expanduser() / 'arrow'

    if not arrow_dir.exists():
        print('Converting checkpoints to arrow format')
        checkpoints = sorted(Path(ckpt_dir).expanduser().glob("*.pth"))
        for ckpt_file in checkpoints:
            print(ckpt_file)
            index = ckpt_file.parts[-1].split('.')[-2]

            ckpt = torch.load(ckpt_file, map_location='cpu')
            (arrow_dir / index).mkdir(parents=True, exist_ok=True)
            for k, v in ckpt.items():
                tens = pa.Tensor.from_numpy(v.numpy())
                with pa.output_stream(arrow_dir / index / k) as f:
                    pa.ipc.write_tensor(tens, f)
            ckpt = None

    with open(Path(ckpt_dir) / "params.json", "r") as f:
        params = json.loads(f.read())

    print("Loading checkpoint")
    segments = sorted((arrow_dir / '00').glob("*"))

    checkpoint = {}
    files = []
    for seg in segments:
        f = pa.memory_map(str(seg))
        files.append(f)
        t = pa.ipc.read_tensor(f).to_numpy()
        t = torch.from_numpy(t)
        checkpoint[seg.parts[-1]] = t
    # torch.set_default_tensor_type(torch.cuda.HalfTensor)
    torch.set_default_tensor_type(torch.BFloat16Tensor)
    # torch.set_default_tensor_type(torch.FloatTensor)

    model_args: ModelArgs = ModelArgs(
        max_seq_len=max_seq_len, max_batch_size=max_batch_size, **params  
    )
    print("Loading tokenizer")
    tokenizer = Tokenizer(model_path=tokenizer_path)
    model_args.vocab_size = tokenizer.n_words
    print("Loading model")
    model = Transformer(model_args)

    checkpoints = sorted(Path(ckpt_dir).glob("*.pth"))
    
    try:
        model.load_state_dict(torch.load(checkpoints[-1]), strict=False)
    except RuntimeError as e:
        print('Ignoring "' + str(e) + '"')
    

    for f in files:
        f.close()
    files = None

    generator = LLaMA(model, tokenizer)
    print(f"Loaded in {time.time() - start_time:.2f} seconds")
    return generator


def main(
        ckpt_dir: str,
        tokenizer_path: str,
        temperature: float = 0.0,
        top_p: float = 0.95,  # use 0.95 or so for top_p sampler, and 0.0 for top_k sampler
        top_k: int = 40,
        repetition_penalty: float = 1.0,  # 1.0 to disable repetition_penalty
        sampler: str = 'top_p',  # top_p or top_k
        max_seq_len: int = 2048,
        max_batch_size: int = 1,
):
    generator = load(ckpt_dir, tokenizer_path, max_seq_len, max_batch_size)

    ctx = """A dialog, where User interacts with AI. AI is helpful, kind, obedient, honest, and knows its own limits.
User: Hello, AI.
AI: Hello! How can I assist you today?
"""

    while True:
        prompt = input(f'User: ')
        if ctx != "":
            ctx = ctx + "User: " + prompt + "\n"
        else:
            ctx = prompt + "\n"

        ctx = (ctx[-1920:]) if len(ctx) >= 2048 else ctx

        if len(ctx.strip()) > 0:
            prompts = [ctx]
            results = generator.generate(
                prompts, max_gen_len=max_seq_len, temperature=temperature, top_p=top_p, top_k=top_k, repetition_penalty=repetition_penalty, sampler=sampler
            )
            ctx = results[0]


if __name__ == "__main__":
    fire.Fire(main)
