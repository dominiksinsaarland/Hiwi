import ast
from sklearn.model_selection import train_test_split
from parameters18 import *
import h5py


def read_record(file):
    with open(file) as f:
        return [ast.literal_eval(line) for line in f]


def read_shape_file(file, unkwn):
    shps = {}
    with open(file) as f:
        for i, line in enumerate(f):
            shps[ast.literal_eval(line)] = i
    shps[unkwn] = len(shps)
    return shps


def read_feat_file(file, unkwn):
    feats = {}
    with open(file) as f:
        for i, item in enumerate(f):
            feats[item.strip()] = i
    feats[unkwn] = len(feats)
    return feats


def read_embeddings(file):
    embs = {}
    with open(file) as f:
        for line in f:
            split = line.strip().split()
            if len(split) == 2:
                continue
            else:
                word, vec = split[0], [float(val) for val in split[1:]]
                embs[word] = vec
    return embs


def pad_middle(sent, max_len):
    for i in range(max_len-len(sent)):
        if before_e2:
            sent.insert(-1, None)
        else:
            sent.insert(1, None)
    return sent


if __name__ == '__main__':
    record_file = 'features/record.txt'
    vocab_file = 'features/vocab.txt'
    shapes_file = 'features/shapes.txt'
    relation_file = 'features/relations.txt'
    word_embds_file = '/home/tyler/PycharmProjects/Hiwi/NemexRelator2010/features/numberbatch-en.txt'\
    # word_embds_file = 'features/mini.h5'
    libLinearInput = 'models/libLinearInput.txt'
    unknown = 'UNK'
    records = read_record(record_file)
    max_rel_length = max([len(rec[1]) for rec in records])
    # record_train, record_test = train_test_split(records, test_size=0.1)
    num_words = 0
    num_shapes = 0
    num_embeddings = 0
    if fire_words:
        words = read_feat_file(vocab_file, unknown)
        num_words = len(words)
    if fire_shapes:
        shapes = read_shape_file(shapes_file, unknown)
        num_shapes = len(shapes)
    if fire_embeddings:
        embeddings = read_embeddings(word_embds_file)
        num_embeddings = len(embeddings['0'])

    relations = read_feat_file(relation_file, unknown)
    len_token_vec = num_words + num_shapes + num_embeddings
    feat_val = ':1.0'

    with open(libLinearInput, 'w+') as lib_out:
        for rec in records:
            sentence_feats = []
            current_relation = rec[4]
            norm_sentence = pad_middle(rec[1], max_rel_length)
            for i, token in enumerate(norm_sentence):
                offset = i * len_token_vec
                token_feats = []
                if token:
                    if fire_words:
                        if token in words:
                            feat_pos = offset + words[token] + 1
                        else:
                            feat_pos = offset + words[unknown] + 1
                        token_feat = str(feat_pos) + feat_val
                        token_feats.append(token_feat)
                    if fire_shapes:
                        shape_vec = [0, 0, 0, 0, 0, 0, 0]
                        if any(char.isupper() for char in token):
                            shape_vec[0] = 1
                        if '-' in token:
                            shape_vec[1] = 1
                        if any(char.isdigit() for char in token):
                            shape_vec[2] = 1
                        if i == 0 and token[0].isupper():
                            shape_vec[3] = 1
                        if token[0].islower():
                            shape_vec[4] = 1
                        if '_' in token:
                            shape_vec[5] = 1
                        if '"' in token:
                            shape_vec[6] = 1
                        tup_vec = tuple(shape_vec)
                        feat_pos = offset + shapes[tup_vec] + num_words + 1
                        token_feat = str(feat_pos) + feat_val
                        token_feats.append(token_feat)
                    if fire_embeddings:
                        temp_token = ''.join('#' if char.isdigit() else char for char in token)
                        temp_token = ''.join('_' if char == '-' else char for char in temp_token)
                        lowered = temp_token.lower()
                        if lowered in embeddings:
                            vec = embeddings[lowered]
                            token_feats += [str(offset + n + num_shapes + num_words + 1) + ':' + str(vec[n])
                                            for n in range(num_embeddings)]
                else:
                    unknown_word = None
                    unknown_shape = None
                    # not handling unknown embeddings because they don't have indices
                    if fire_words:
                        feat_pos = offset + words[unknown] + 1
                        unknown_word = str(feat_pos) + feat_val
                    if fire_shapes:
                        feat_pos = offset + shapes[unknown] + num_words + 1
                        unknown_shape = str(feat_pos) + feat_val
                    token_feats = [unknown_word, unknown_shape]

                sentence_feats += token_feats
            print(sentence_feats[-1], offset)
            lib_out.write(str(relations[current_relation]) + ' ')
            lib_out.write(' '.join(i for i in sentence_feats if i) + '\n')