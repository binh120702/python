import google.generativeai as genai
from dotenv import load_dotenv
import os

class Gemini:
    def __init__(self) -> None:
        
        load_dotenv()
        GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

        self.model = genai.GenerativeModel('gemini-pro')
        self.reset_history()

    def reset_history(self):
        self.chat = self.model.start_chat(history=[])

    def ask(self, ques):
        tmp = self.model.generate_content(ques)
        return tmp.text


    def get_label_list(self, labels, datax):
        schema = """
                Cho tập nhãn sau: {}
                
                Dựa trên tập nhãn đã cho, hãy nhận diện các thực thể có tên(có thể lồng nhau) trong đoạn sau:

                {}
               
                Câu hỏi: Những thực thể nào thuộc lớp {} trong đoạn trên?
                Trả lời dưới dạng 1 dòng duy nhất chỉ gồm các thực thể phân chia bằng dấu "___"
                """
               
        ents_dict = {}
        # iterate through all entity types:
        for i in labels.split('\n'):
            self.reset_history()
            print(i.split()[0], end = ' ')

            data = datax.split(' ')
            maxn = len(data)
            m = 0
            n = min(8000, maxn)
            # naive approach: split by X k words _ each to fit prompt
            all_ents = []
            while m <= maxn:
                #print('round:', m, n)
                ents = None 
                tries = 0
                while ents is None:
                    try:
                        tries += 1
                        ents = self.ask(schema.format(labels, ' '.join(data[m:n]), i.split()[0]))
                    except:
                        if tries >= 1:
                            ents = ""
                            print('Give up!')
                        else:
                            print('Failed', tries)
                # parse result
                ents = ents.split("___")
                all_ents.extend(ents)

                m = n+1
                n = min(n+8000, maxn)
            ents_dict[i.split()[0]] = all_ents
            #print(all_ents)
        return ents_dict