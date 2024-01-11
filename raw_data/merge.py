import os

ocr_path = os.path.join(os.getcwd(), 'raw_data', 'ocr')
output_path = os.path.join(os.getcwd(), 'raw_data', 'kokuyaku.txt')

with open(output_path, 'a', encoding='utf-8') as output:
    for batch in os.listdir(ocr_path):
        text_dir = os.path.join(ocr_path, batch, 'shared', 'txt')
        for pagefile in os.listdir(text_dir):
            if 'main' in pagefile:
                page_dir = os.path.join(text_dir, pagefile)
                with open(page_dir, 'r', encoding='utf-8') as data:
                    output.write(data.read())