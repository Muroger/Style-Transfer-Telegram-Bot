from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
import copy


class ContentLoss(nn.Module):

    def __init__(self, target, ):
        super(ContentLoss, self).__init__()
        # we 'detach' the target content from the tree used
        # to dynamically compute the gradient: this is a stated value,
        # not a variable. Otherwise the forward method of the criterion
        # will throw an error.
        self.target = target.detach()  # это константа. Убираем ее из дерева вычеслений
        self.loss = F.mse_loss(self.target, self.target)  # to initialize with something

    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input