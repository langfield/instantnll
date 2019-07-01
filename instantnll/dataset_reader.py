from typing import Iterator, List, Dict

import os
import torch
import torch.optim as optim
import numpy as np

import shutil
import tempfile

from allennlp.commands.train import train_model
from allennlp.common.params import Params
from allennlp.data import Instance
from allennlp.data.fields import TextField, SequenceLabelField
from allennlp.data.dataset_readers import DatasetReader
from allennlp.common.file_utils import cached_path
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.tokenizers import Token
from allennlp.data.vocabulary import Vocabulary
from allennlp.models import Model
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder, TextFieldEmbedder
from allennlp.modules.token_embedders import Embedding
from allennlp.modules.seq2seq_encoders import Seq2SeqEncoder, PytorchSeq2SeqWrapper
from allennlp.nn.util import get_text_field_mask, sequence_cross_entropy_with_logits

from allennlp.training.metrics import CategoricalAccuracy
from allennlp.data.iterators import BucketIterator
from allennlp.training.trainer import Trainer
from allennlp.predictors import SentenceTaggerPredictor
torch.manual_seed(1)

@DatasetReader.register('instantnll')
class InstDatasetReader(DatasetReader):
    """
    DatasetReader for NER tagging data, one sentence per line, like
        The###DET dog###NN ate###V the###DET apple###NN
    """
    def __init__(self, token_indexers: Dict[str, TokenIndexer] = None) -> None:
        super().__init__(lazy=False)
        self.token_indexers = token_indexers or {"tokens": SingleIdTokenIndexer()}

    def text_to_instance(self, tokens: List[Token], ent_types: List[str] = None) -> Instance:
        sentence_field = TextField(tokens, self.token_indexers)
        fields = {"sentence": sentence_field}
        if ent_types:
            label_field = SequenceLabelField(labels=ent_types, sequence_field=sentence_field)
            fields["labels"] = label_field
        return Instance(fields)

    def _read(self, file_path: str) -> Iterator[Instance]:
        with open(file_path) as f:
            for line in f:
                # Strips leading and trailing whitespace, splits into tokens. 
                tokens = line.strip().split()
                sentence = []
                ent_types = []
                for token in tokens:
                    ent_type = token[0]
                    if ent_type not in ['!','*']:
                        ent_type = '#'   # Indicates irrelevant non-tagged tokens.
                    else: 
                        token = token[1:] 
                    sentence.append(token)
                    ent_types.append(ent_type)
                yield self.text_to_instance([Token(word) for word in sentence], ent_types)
