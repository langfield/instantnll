{
    "dataset_reader":{
        "type": "instantnll",
    },
    "train_data_path":"../data/train.txt",
    "validation_data_path":"../data/validate.txt",
    "model":{
        "type": "instantnll",
        "word_embeddings": {
            // Technically you could put a "type": "basic" here,
            // but that's the default TextFieldEmbedder, so doing so
            // is optional.
            "type": "debug",
            "token_embedders": {
                "tokens": {
                    "type": "embedding",
                    "embedding_dim": 100,
                    "pretrained_file": "~/packages/data/instantnll/top_10000_emb.txt",
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
        }
    }
}
