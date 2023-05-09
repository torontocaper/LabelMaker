# from chatgpt
def convert_vtt_to_labels(vtt_file, labels_file):
    with open(vtt_file, 'r') as vtt:
        vtt_lines = vtt.readlines()

    labels = []
    for line in vtt_lines:
        line_index = vtt_lines.index(line)
        line = line.strip()
        if line.startswith('00:'):  # Assuming timestamp format: hh:mm:ss.sss
            start_time, end_time = line.split(' --> ')
            # start_time = timestamp.split(':')[2].replace('.', '')  # Extract seconds without decimal
            # end_time = text.split(':')[2].replace('.', '')  # Extract seconds without decimal
            start_time_hours, start_time_minutes, start_time_seconds = start_time.split(":")
            start_time_audacity = float(start_time_hours)*3600 + float(start_time_minutes)*60 + float(start_time_seconds)
            end_time_hours, end_time_minutes, end_time_seconds = end_time.split(":")
            end_time_audacity = float(end_time_hours)*3600 + float(end_time_minutes)*60 + float(end_time_seconds)
            label_text = vtt_lines[line_index + 1].strip("- ")  # Get the next line as label text
            label = f'{start_time_audacity}\t{end_time_audacity}\t{label_text}'
            labels.append(label)

    with open(labels_file, 'w') as labels_out:
        labels_out.write(''.join(labels))

    print(f'Successfully converted {vtt_file} to Audacity labels format.')

# Example usage
vtt_file = 'file_test.vtt'
labels_file = 'file_test_converted.txt'
convert_vtt_to_labels(vtt_file, labels_file)
