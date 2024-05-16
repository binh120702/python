from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import os

class GPT4o:
    def __init__(self, model="gpt-3.5-turbo-0125") -> None:
        
        load_dotenv()
        OPENAI_KEY=os.getenv('OPENAI_KEY')

        self.client = OpenAI(api_key=OPENAI_KEY)
        self.model = model

        self.reset_history()

    def reset_history(self):
        pass

    def ask(self, ques):
        response = self.client.chat.completions.create(
            model = self.model,
            messages=[
                {
                    "role":"user", 
                    "content":ques
                }
            ]
        )
        return response.choices[0].message.content

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = len(encoding.encode(string))
        return num_tokens


    def get_label_list(self, labels, data):
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
            print(i.split()[0], end = ' ')

            ents = None 
            tries = 0

            while ents is None:
                try:
                    tries += 1
                    ents = self.ask(schema.format(labels, data, i.split()[0]))
                except:
                    if tries >= 1:
                        ents = ""
                        print('Give up!')
                    else:
                        print('Failed', tries)
            # parse result
            print(ents)
            ents = ents.split("___")
            ents_dict[i.split()[0]] = ents
            
        return ents_dict