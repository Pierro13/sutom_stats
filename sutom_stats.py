input_file = "chat.txt"

# conunt the number of '#SUTOM #' and 'https://sutom.nocle.fr' in the file

with open(input_file, 'r', encoding='utf-8') as file:
    content = file.read()
sutom_count = content.count('#SUTOM #')
link_count = content.count('https://sutom.nocle.fr')
print(f"Number of '#SUTOM #': {sutom_count}")
print(f"Number of 'https://sutom.nocle.fr': {link_count}")

