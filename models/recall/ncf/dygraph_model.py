# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import paddle
import paddle.nn as nn
import paddle.nn.functional as F
import math
import net


class DygraphModel():
    # define model
    def create_model(self, config):
        num_users = config.get("hyper_parameters.num_users")
        num_items = config.get("hyper_parameters.num_items")
        latent_dim = config.get("hyper_parameters.latent_dim")
        layers = config.get("hyper_parameters.fc_layers")
        ncf_model = net.NCFLayer(num_users, num_items, latent_dim, layers)
        return ncf_model

    # define feeds which convert numpy of batch data to paddle.tensor 
    def create_feeds(self, batch_data, is_infer=False):
        user_input = paddle.to_tensor(batch_data[0].numpy().astype('int64')
                                      .reshape(-1, 1))
        item_input = paddle.to_tensor(batch_data[1].numpy().astype('int64')
                                      .reshape(-1, 1))
        if is_infer:
            return [user_input, item_input]

        label = paddle.to_tensor(batch_data[2].numpy().astype('int64')
                                 .reshape(-1, 1))
        return [user_input, item_input, label]

    # define loss function by predicts and label
    def create_loss(self, prediction, label):
        cost = F.log_loss(
            input=prediction, label=paddle.cast(
                x=label, dtype='float32'))
        avg_cost = paddle.mean(cost)
        return avg_cost

    # define optimizer 
    def create_optimizer(self, dy_model, config):
        lr = config.get("hyper_parameters.optimizer.learning_rate", 0.001)
        optimizer = paddle.optimizer.Adam(
            learning_rate=lr, parameters=dy_model.parameters())
        return optimizer

    # define metrics such as auc/acc
    # multi-task need to define multi metric

    def create_metrics(self):
        metrics_list_name = []
        metrics_list = []
        return metrics_list, metrics_list_name

    # construct train forward phase  
    def train_forward(self, dy_model, metrics_list, batch_data, config):
        inputs = self.create_feeds(batch_data, False)

        prediction = dy_model.forward(inputs, False)
        loss = self.create_loss(prediction, inputs[2])
        # update metrics
        print_dict = {"loss": loss, "prediction": prediction}
        return loss, metrics_list, print_dict

    def infer_forward(self, dy_model, metrics_list, batch_data, config):
        inputs = self.create_feeds(batch_data, True)

        prediction = dy_model.forward(inputs, True)
        # update metrics
        print_dict = {"prediction": prediction}
        return metrics_list, print_dict
