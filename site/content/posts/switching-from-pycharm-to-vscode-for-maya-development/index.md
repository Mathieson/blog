+++
title = "Switching from PyCharm to VS Code for Maya Development"
date = 2026-04-02
draft = false
tags = ["maya", "python", "vscode", "tooling", "tech-art"]
+++

If you've been around here before, you might have seen my post on [setting up PyCharm for Maya Python development](/posts/the-best-pycharm-mayapy-interpreter-setup/). It's been one of my more practical posts, and for a long time it reflected how I actually worked. PyCharm was my IDE of choice for Maya scripting, and I didn't have much reason to look elsewhere.

I'd tried VS Code over the years and never really landed on it. Getting it properly configured for Maya — pointing it at the right interpreter, getting reasonable autocomplete — always felt like more friction than it was worth. PyCharm just worked, and once you had a good setup going, it was hard to argue with.

Recently I went back to VS Code and gave it another proper shot. This time, it clicked. And in revisiting everything, I also realized my old workflow had a limitation I hadn't fully reckoned with — something I'll get into below. Workflows evolve. It is what it is. Here's where I've landed.

## Two things that made the difference

### uv

The first is [`uv`](https://docs.astral.sh/uv/), the Python package and project manager from Astral. If you haven't run into it yet, it's worth a look — it's fast, opinionated in the right ways, and has become my go-to for managing Python environments.

For Maya development specifically, the challenge has always been the same: getting a Python environment set up that gives you both good autocomplete in the editor and the ability to actually execute code against Maya in headless mode.

In my PyCharm post, the approach was to point PyCharm directly at mayapy as the system interpreter — no virtual environment involved. That works, and it unlocks a lot, but it means you're working in Maya's Python environment directly. Any packages you install go in there with everything else, and you lose the isolation and reproducibility that a virtual environment gives you.

With uv, the goal was to get to a venv-based workflow. The problem is that when you create a virtual environment and try to run code with mayapy in headless mode, Maya's own site-packages folder isn't on the Python path inside your venv — so anything that depends on Maya's modules can't be found.

In my old PyCharm setup, the fix was a manual step in the interpreter settings — you had to go in and explicitly add Maya's site-packages directory to the path. It worked, but it was easy to forget, and it was something you had to redo whenever you set up a new project.

With uv, we solved this more cleanly. As part of the thin wrapper script that creates the virtual environment, we now automatically drop a `.pth` file into the venv's own site-packages directory. That file contains a single line: the path to Maya's site-packages. Python picks up `.pth` files automatically at startup, so the moment the venv is activated, Maya's packages are on the path — no manual config step, nothing to forget, nothing to redo.

The wrapper script lets you define which Maya version to work with, which then gets passed to uv. For example:

```bash
uv sync --python maya2025
```

Behind the scenes, this becomes:

```bash
uv sync --python "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe"
```

You could pass the full interpreter path like this every time and use vanilla uv if you wanted — it works. But it's a bit tedious, and you'd also miss out on the automatic `.pth` setup and the auto-sync of maya-stubs that the wrapper handles for you. The script just takes care of all of that in one step.

The script handles setting up the venv and dropping in that `.pth` file automatically.

On Windows, that `.pth` file line looks something like this (adjust for your Maya version):

```
C:\Program Files\Autodesk\Maya2025\Python\Lib\site-packages
```

Worth noting: this isn't a VS Code-specific trick. If you're still on PyCharm, the same approach should work for you too — it operates at the Python environment level, not the IDE level. But it did solve the friction I was hitting in VS Code, and it's cleaner than the manual path configuration I'd been doing before.

### AI-assisted autocomplete

The other thing is that Copilot — and AI-assisted autocomplete in general — has really closed the gap that used to make PyCharm feel superior on the completions side. VS Code's native autocomplete for Maya was always a weak point. That's less of a concern now when you've got something like Copilot doing a lot of the heavy lifting on suggestions.

## A couple of areas where VS Code is notably better

Once I was set up, a couple of things stood out as better in VS Code than I was used to in PyCharm.

The GitLab Workflow extension is the main one. MR reviews, pipeline status, CI feedback — it all surfaces cleanly inside the editor. The PyCharm experience always felt like it was playing catch-up by comparison.

Copilot integration is the second. I'll caveat that it's been a while since I've been in PyCharm, so it may have improved — but I'd find it hard to imagine it hitting the same level of integration that VS Code has, given that both Copilot and VS Code come from Microsoft. It shows. Commit message generation is built right in. Copilot can look at what's happening in the terminal and help you work through errors there. It's woven into the editor throughout rather than feeling like something bolted on.

To be fair, I haven't explored the newer AI-centric IDEs that have been popping up recently. I've stayed between these two main players, so it's entirely possible there's something out there with even better AI integration. I'm happy with where I've landed though — there's only so much you can realistically go and evaluate.

## What I do miss about PyCharm

PyCharm is a more polished experience. It's a commercial product built specifically for Python development, and that focus shows. Everything is there out of the box. You don't have to go hunting for extensions, experiment with settings, or put in the upfront investment to get things feeling right.

VS Code is the opposite. It's general purpose, and making it your own takes real time and exploration. Finding the extensions that fit your workflow, getting them configured the way you want — none of that is handed to you. It's a more DIY experience, and if you're not in the mood for that, PyCharm's polish is hard to argue with.

Once I'd put in the time though, I found I prefer where I landed. The trade-off of upfront investment for a better-integrated toolchain — especially around GitLab and Copilot — is one I'd make again.

## So should you switch?

If you're on PyCharm for Maya development and things are working for you, there's no urgent reason to change. The [old PyCharm setup post](/posts/the-best-pycharm-mayapy-interpreter-setup/) still holds up for what it is.

But if GitLab and Copilot are a meaningful part of your workflow, VS Code has better answers for both now. And the setup story — which used to be the main argument against it — isn't really an argument anymore.
