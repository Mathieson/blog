+++
title = "Tensorflow to PyTorch"
date = 2021-10-10T00:00:00Z
tags = ["deep-learning", "pytorch"]
+++


My journey into machine learning is still in its relatively early stages. I began by familiarizing myself with Tensorflow. It was an excellent introduction, whetting my appetite for AI, but I am now ready to make the switch to PyTorch.

There are two key drivers behind my decision to make this change.

1. Debugging
2. Process transparency

## Debugging

Debugging in Tensorflow has been problematic, to say the least, being most painful when writing custom loss functions. I'd feed dummy data to the loss function while writing it, pre-vetting what I was creating. However, when something didn't work as expected during training, troubleshooting was near impossible. Tensors at training time are opaque, acting in some "virtual" fashion if my memory serves (this was a while ago now).

While I could throw down a breakpoint and inspect the values or print them out when I was "pre-vetting," this "virtual" tensor removed any ability to do so. Perhaps this is possible to do, and I just hadn't dug deep enough to discover how. I did dig mighty deep, though - so much so that it isn't worth the effort even if it is possible.

On the other hand, PyTorch maintains a reputation of operating much closer to native Python, interfacing more cleanly with NumPy, and being a friendlier experience when debugging.

## Process transparency

Deep learning and neural nets have a steep learning curve, with many moving pieces and new concepts to understand (which can be intimidating). Tensorflow, and more specifically Keras, help reduce the barrier to entry by being a high-level wrapper, simplifying and removing the need for understanding some of the details of the underlying process. The structure for assembling a graph is apparent and feels guided, giving a clear template to follow to get results quickly.

After much reading and researching, I feel I am now over the initial hump of bewilderment and have a decent grasp of _most_ of the inner workings of the training process. It feels like a good time to expose myself to a new library in hopes of validating and cementing my understandings. PyTorch feels, so far, like it shares more of what Keras is hiding and is slightly less structured. Seeing and working with more of the moving pieces is an exciting next step.

For anyone out there also looking to break into PyTorch as a learning framework, I've found the following article to give a nicely pared-down view of the PyTorch life-cycle: [PyTorch Tutorial: How to Develop Deep Learning Models with Python](https://machinelearningmastery.com/pytorch-tutorial-develop-deep-learning-models/). Instead of walking you through a completed example, introducing too much additional information too soon and making things cloudy, It strips away everything non-essential. It gives you a look at the core process, leaving you with an easily digestible overview of the abstracted process.

## In closing

I've immensely enjoyed working with Tensorflow and Keras and may find myself returning to it someday. For now, I am excited to continue my journey with PyTorch and see how different the experience is.
