import os
from WordNet import WordNet
import string


# S015674 Mustafa Alper Sayan


def main():
    turkish = WordNet.WordNet('TurkishWordNet-Py-master/turkish_wordnet.xml')
    loader(my_annotations=True)
    sentences, semantics = prepare_corpus_and_semantics(my_annotations=True)

    calculated_senses = simple_lesk_algorithm(sentences, turkish)

    accuracy_include_none = calculate_accuracy(semantics, calculated_senses, include_none_senses=True)
    accuracy_exclude_none = calculate_accuracy(semantics, calculated_senses, include_none_senses=False)


    print('accuracy of the simple lesk algorithm on my annotations including nones = %' + str(accuracy_include_none))
    print('accuracy of the simple lesk algorithm on my annotations excluding nones = %' + str(accuracy_exclude_none))


    loader(my_annotations=False)
    sentences, semantics = prepare_corpus_and_semantics(my_annotations=False)

    calculated_senses = simple_lesk_algorithm(sentences, turkish)

    accuracy_include_none = calculate_accuracy(semantics, calculated_senses, include_none_senses=True)
    accuracy_exclude_none = calculate_accuracy(semantics, calculated_senses, include_none_senses=False)


    print('accuracy of the simple lesk algorithm on all annotations including nones = %' + str(accuracy_include_none))
    print('accuracy of the simple lesk algorithm on all annotations excluding nones = %' + str(accuracy_exclude_none))



def calculate_accuracy(semantics, calculated_senses, include_none_senses):

    if include_none_senses:
        number_of_correct_senses = 0
        number_of_senses = 0
        for i in range(len(semantics)):
            for j in range(len(semantics[i])):
                calculated_sense = calculated_senses[i][j]
                actual_sense = semantics[i][j]
                if actual_sense == calculated_sense or (actual_sense and calculated_sense is None):
                    number_of_correct_senses += 1

                number_of_senses += 1

    else:

        number_of_correct_senses = 0
        number_of_senses = 0
        for i in range(len(semantics)):
            for j in range(len(semantics[i])):
                calculated_sense = calculated_senses[i][j]
                actual_sense = semantics[i][j]
                if actual_sense is None or calculated_sense is None:
                    continue
                else:
                    if actual_sense == calculated_sense:
                        number_of_correct_senses += 1

                    number_of_senses += 1


    return (number_of_correct_senses / number_of_senses) * 100


def simple_lesk_algorithm(sentences, turkish):

    calculated_senses = []
    for sentence in sentences:

        context = sentence
        senses_of_the_sentence = []
        for word in sentence:
            word_senses = turkish.getSynSetsWithLiteral(str(word))
            best_sense = get_most_frequent_sense(word_senses)
            max_overlap = 0
            for sense in word_senses:

                signature = sense.getExample()
                overlap = compute_overlap(signature, context)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_sense = sense

            if best_sense is not None:
                senses_of_the_sentence.append(best_sense.getId())
            else:
                senses_of_the_sentence.append(best_sense)

        calculated_senses.append(senses_of_the_sentence)

    return calculated_senses


def compute_overlap(signature, context):

    length_of_common_occurences = 0

    if signature is not None:
        signature = signature.translate(str.maketrans({key: " {0} ".format(key) for key in string.punctuation}))
        signature = signature.split()

        common_occurences = list(set(signature).intersection(context))
        length_of_common_occurences = len(common_occurences)

        return length_of_common_occurences

    else:
        return length_of_common_occurences


def get_most_frequent_sense(senses):
    max_frequency = 0
    most_freq_sense = None
    for sense in senses:
        frequency = sense.relationSize()

        if frequency > max_frequency:
            most_freq_sense = sense
            max_frequency = frequency

    return most_freq_sense


def prepare_corpus_and_semantics(my_annotations):

    sentence = []
    semantics_of_the_sentence = []
    sentences = []
    semantics = []

    word = None
    semantic = None

    if my_annotations:
        f = open("semantics_dataset.txt", "r", encoding='utf-8')
    else:
        f = open("semantics_dataset_all_annotations.txt", "r",encoding='utf-8')

    lines = f.readlines()

    for line in lines:

        split_0 = line.split()

        if split_0[0] == '<S>':
            pass

        elif 'DOC' in split_0[0]:
            pass

        elif split_0[0] == '</S>':
            sentences.append(sentence)
            semantics.append(semantics_of_the_sentence)
            sentence = []
            semantics_of_the_sentence = []

        else: # means this is a word or a punc

            if len(split_0) == 2:
                word = split_0[0]
                semantic = split_0[1]

                sentence.append(word)
                semantics_of_the_sentence.append(semantic)

            else:
                word = split_0[0]
                sentence.append(word)
                semantics_of_the_sentence.append(semantic)

    return sentences, semantics


# method to write Turkish-phrase as text file
def loader(my_annotations):

    if my_annotations:
        folderpath = r"Turkish-Phrase"

    else:
        folderpath = r"Turkish-Phrase-all-annotations"

    filepaths = [os.path.join(folderpath, name) for name in os.listdir(folderpath)]

    str_ = '<DOC>\t<DOC>+BDTAG\n'

    for path in filepaths:

        with open(path, 'r', encoding='utf-8') as f:

            file = f.readlines()

            if 'semantics' not in file[0]:
                pass

            else:

                str_ += '<S>\t<S>+BSTAG\n'
                line = file[0]
                line_split = line.split()
                for split in line_split:
                    split_2 = split[1:-1].split("}{")
                    for split_3 in split_2:
                        split_4 = split_3.split('=')
                        semantics = None

                        if split_4[0] == 'turkish':
                            full_word = str(split_4[1])
                        elif split_4[0] == 'semantics':
                            semantics = str(split_4[1])
                        else:
                            pass

                        if semantics is not None:
                            str_ += full_word + '\t' + semantics + '\n'
                        else:
                            pass


                str_ += '</S>\t</S>+ESTAG\n'

    str_ += '</DOC>\t</DOC>+EDTAG\n'

    if my_annotations:
        with open("semantics_dataset.txt", "w", encoding='utf8') as text_file:
            text_file.write(str_)

    else:

        with open("semantics_dataset_all_annotations.txt", "w", encoding='utf8') as text_file:
            text_file.write(str_)

if __name__ == '__main__':
    main()