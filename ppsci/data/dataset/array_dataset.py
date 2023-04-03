"""Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import paddle
from paddle import io


class NamedArrayDataset(io.Dataset):
    """Class for Named Array Dataset.

    Args:
        input (Dict[str, np.ndarray]): Input dict.
        label (Dict[str, np.ndarray]): Label dict.
        weight (Dict[str, np.ndarray], optional): Weight dict.
        transforms (vision.Compose, optional): Compose object contains sample wise transform(s).
    """

    def __init__(self, input, label, weight, transforms=None):
        super().__init__()
        self.input = input
        self.label = label
        self.weight = weight
        self.transforms = transforms
        self._len = len(next(iter(input.values())))

    def __getitem__(self, idx):

        input_item = {key: value[idx] for key, value in self.input.items()}
        label_item = {key: value[idx] for key, value in self.label.items()}
        weight_item = {key: value[idx] for key, value in self.weight.items()}

        # TODO(sensen): Transforms may be applied on label and weight.
        if self.transforms is not None:
            input_item = self.transforms(input_item)

        return (input_item, label_item, weight_item)

    def __len__(self):
        return self._len


class IterableNamedArrayDataset(io.IterableDataset):
    """IterableNamedArrayDataset for full-data training, i.e.batch_size=len(data).
    
    Args:
        input (Dict[str, np.ndarray]): Input dict.
        label (Dict[str, np.ndarray]): Label dict.
        weight (Dict[str, np.ndarray]): Weight dict.
        batch_size (int): Batch size. Defaults to None.
        transforms (vision.Compose, optional): Compose object contains sample wise transform(s). Defaults to None.
    """

    def __init__(self, input, label, weight, transforms=None):
        self.input = {k: paddle.to_tensor(v) for k, v in input.items()}
        self.label = {k: paddle.to_tensor(v) for k, v in label.items()}
        self.weight = {k: paddle.to_tensor(v) for k, v in weight.items()}
        self._len = len(next(iter(self.input.values())))

    @property
    def num_samples(self):
        """Number of samples within current dataset."""
        return self._len

    def __iter__(self):
        yield self.input, self.label, self.weight

    def __len__(self):
        return 1
