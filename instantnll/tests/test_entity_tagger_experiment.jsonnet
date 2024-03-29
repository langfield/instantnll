{
    "dataset_reader":{
        "type": "inst_dataset_reader",
    },
    "train_data_path":"../data/train_small.txt",
    "validation_data_path":"../data/validate_cities.txt",
    "model":{
        "type": "inst_entity_tagger",
        "word_embeddings": {
            // Technically you could put a "type": "basic" here,
            // but that's the default TextFieldEmbedder, so doing so
            // is optional.
            "type": "basic",
            "token_embedders": {
                "tokens": {
                    "type": "embedding",
                    "embedding_dim": 300,
                    "pretrained_file": "~/packages/data/instantnll/GoogleNews-vectors-negative300_SUBSET.txt",
                },
            }
        },
        "encoder": {
            "type": "CosineEncoder",
            "simrel": {
                "input_dim": 300,
                "num_classes": 3,
            },
        },
    },
    
    "iterator":{
        "type": "basic",
        "batch_size": 10,
    },
    "trainer":{
        "optimizer":{
            "type":"adam"
        },
        "num_epochs": 1,
    },
    "vocabulary":{
        "pretrained_files": {
            "tokens": "~/packages/data/instantnll/GoogleNews-vectors-negative300_SUBSET.txt",
        }
    },
}
