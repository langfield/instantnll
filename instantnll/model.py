from typing import Dict

import torch
import numpy as np


# from allennlp.commands.train import train_model
from allennlp.data.vocabulary import Vocabulary
from allennlp.models import Model
from allennlp.modules.text_field_embedders import TextFieldEmbedder
from allennlp.modules.seq2seq_encoders import Seq2SeqEncoder
from allennlp.nn.util import get_text_field_mask, sequence_cross_entropy_with_logits
from allennlp.training.metrics import CategoricalAccuracy
from allennlp.training.metrics import FBetaMeasure

from encoder import CosineEncoder # pylint: disable=no-name-in-module, unused-import
torch.manual_seed(1)

#========1=========2=========3=========4=========5=========6=========7=========8=========9=========0

@Model.register('inst_entity_tagger')
class InstEntityTagger(Model):
    def __init__(self,
                 word_embeddings: TextFieldEmbedder,
                 encoder: Seq2SeqEncoder,
                 vocab: Vocabulary) -> None:

        super().__init__(vocab)
        self.word_embeddings = word_embeddings
        self.encoder = encoder
        self.vocab = vocab
        self.label_vocab = vocab.get_index_to_token_vocabulary(namespace='labels')

        inf_vec = torch.Tensor([float('-inf')] * encoder.get_input_dim())
        self.class_avgs = [inf_vec.clone() for i in range(len(self.label_vocab))]

        self.accuracy = CategoricalAccuracy()
        self.f_beta = FBetaMeasure(1.0, None, [0, 1, 2])

    #====1=========2=========3=========4=========5=========6=========7=========8=========9=========0

    # pylint: disable=arguments-differ
    def forward(self,
                sentence: Dict[str, torch.Tensor],
                labels: torch.Tensor = None) -> Dict[str, torch.Tensor]:

        mask = get_text_field_mask(sentence)
        embeddings = self.word_embeddings(sentence)

        class_avgs = self.class_avgs
        encoder_out = self.encoder(embeddings, labels, class_avgs, mask) # Modifies `class_avgs`.
        tag_logits = encoder_out
        torch.nn.functional.relu(tag_logits, inplace=True)
        output_dict = {"tag_logits": tag_logits}
        # Should we do a softmax so that we get a probability distribution?

        if labels is not None:
            self.f_beta(tag_logits, labels, mask)
            self.accuracy(tag_logits, labels, mask)

            output_dict["loss"] = sequence_cross_entropy_with_logits(tag_logits, labels, mask)

        return output_dict

    #====1=========2=========3=========4=========5=========6=========7=========8=========9=========0

    def decode(self, output_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        If there's a decode function, the predictor will try to use it.
        """
        # Shape: (batch_size, seq_len, num_classes)
        logits = output_dict['tag_logits']
        argmax_indices = np.argmax(logits, axis=-1)
        all_tags = []
        for batch_argmaxs in argmax_indices:
            label_vocab = self.vocab.get_index_to_token_vocabulary(namespace="labels")
            tags = [label_vocab[int(x)] for x in batch_argmaxs]
            all_tags.append(tags)
        output_dict['tags'] = all_tags # Shape: (batch_size, seq_len)
        return output_dict

    #====1=========2=========3=========4=========5=========6=========7=========8=========9=========0

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        f1_dict = self.f_beta.get_metric(reset)
        metrics_dict = {}
        for submetric, class_vals in f1_dict.items():
            for i, value in enumerate(class_vals):
                metrics_dict.update({submetric + " " + str(i): value})
        return {**{"accuracy": self.accuracy.get_metric(reset)}, **metrics_dict}
