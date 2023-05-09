# from chatgpt
def convert_vtt_to_labels(vtt_file, labels_file):
    with open(vtt_file, 'r') as vtt:
        vtt_lines = vtt.readlines()

    labels = []
    for line in vtt_lines:
        line = line.strip()
        if line.startswith('00:'):  # Assuming timestamp format: hh:mm:ss.sss
            timestamp, text = line.split(' --> ')
            start_time = timestamp.split(':')[2].replace('.', '')  # Extract seconds without decimal
            end_time = text.split(':')[2].replace('.', '')  # Extract seconds without decimal
            label_text = vtt_lines[vtt_lines.index(line) + 1].strip()  # Get the next line as label text
            label = f'{start_time}\t{end_time}\t{label_text}'
            labels.append(label)

    with open(labels_file, 'w') as labels_out:
        labels_out.write('\n'.join(labels))

    print(f'Successfully converted {vtt_file} to Audacity labels format.')

# Example usage
vtt_file = 'example.vtt'
labels_file = 'output_labels.txt'
convert_vtt_to_labels(vtt_file, labels_file)
