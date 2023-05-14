#import torch
from collections import deque


def rotate(l, n):
    d = deque(l)
    d.rotate(n)
    return list(d)


# def check_for_cuda():
#     if torch.cuda.is_available():
#         print("CUDA is available! PyTorch can use your GPU.")
#         device = torch.device("cuda")
#     else:
#         print("CUDA is not available. PyTorch will use the CPU instead.")
#         device = torch.device("cpu")
#
#     print("PyTorch will use the following device for computation:", device)
#     return device

