import os
import re
import pandas as pd

def generate_excel_from_spectrograms(folder, output_file="clasified_spectrograms.xlsx"):
    
    pattern = re.compile(r'spectrogram_(\d+)\.png')
    
    data = []
    
    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))  
            data.append([number])
    
    
    data.sort(key=lambda x: x[0])
    
    df = pd.DataFrame(data, columns=["Spectrogram Number"])

    df.to_excel(output_file, index=False)
    print(f"Excel file generated: {output_file}")


folder_path = "./data/raw/preprocessed_spectograms/"
generate_excel_from_spectrograms(folder_path)
