from flask import Flask, request, jsonify, send_from_directory
import os
from calculator import VRAMCalculator
from data_args import DataArgs
from finetuning_args import FinetuningArgs
from model_args import ModelArgs
from optimizer_args import OptimizerArgs

app = Flask(__name__, static_folder='../../frontend/dist')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json

    model_args = ModelArgs(
        num_params=data['modelSize'] * 1000000, 
        vocab_size=data['vocabSize'],
        hidden_size=data['hiddenSize'],
        num_attention_heads=data['numAttentionHeads'],
        num_key_value_heads=data['numKeyValueHeads'],
        intermediate_size=data['intermediateSize'],
        num_layers=data['numLayers']
    )
    finetuning_args = FinetuningArgs(
        training_precision=data['trainingPrecision'],
        is_fsdp=data['isFsdp'],
        lora_alpha=data.get('loraAlpha'),
        lora_dropout=data.get('loraDropout'),
        lora_rank=data.get('loraRank'),
        lora_target=data.get('loraTarget'),
        qlora_alpha=data.get('qloraAlpha'),
        qlora_dropout=data.get('qloraDropout')
    )
    optimizer_args = OptimizerArgs(
        optimizer=data['optimizer'],
        optimizer_sgd_momentum=data.get('optimizerSgdMomentum')
    )
    data_args = DataArgs(
        batch_size=data['batchSize'],
        sequence_length=data['sequenceLength']
    )
    calculator = VRAMCalculator(
        model_args,
        finetuning_args,
        optimizer_args,
        data_args,
        num_gpus=data['numGpus'],
        unit=data['unit']
    )

    result = calculator.estimate_result()
    return jsonify(result)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)