from hanziconv import HanziConv
import pinyin_jyutping_sentence
sen = "世界上的教育都讓我失望。"

out = open("cmn_sen_db.tsv", "w", encoding="utf-8")

with open("cmn_sentences.tsv", encoding="utf-8") as fh:
    lines = fh.readlines()
    i=0
    for line in lines:
        i += 1
        sen_data = line.split("\t")
        sen_id = i
        sen_sen = sen_data[2]
        sen_tran = sen_data[3]

        sen_sim = HanziConv.toSimplified(sen_sen)
        sen_trad = HanziConv.toTraditional(sen_sen)
        sen_pin = pinyin_jyutping_sentence.pinyin(sen_sen)

        sen_db = str(sen_id) + "\t" + sen_sim + "\t" + sen_trad + "\t" + sen_pin + "\t" + sen_tran
        print(sen_db)
        out.write(sen_db)
out.close()




