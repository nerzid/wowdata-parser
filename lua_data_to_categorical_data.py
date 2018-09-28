import json
import requests
from lxml import html
from pprint import pprint

wowhead_url = "https://www.wowhead.com/"
wowhead_quest_url = wowhead_url + "quest=%s"

data_path = 'C:/Users/nerzid/Documents/Untitled Folder/data/'
file_tr_lua_path = data_path + 'QuestData_tu.lua'
file_tr_json_path = data_path + 'tr_data.json'

file_tr_titles_path = data_path + 'titles.txt'
file_tr_descriptions_path = data_path + 'descriptions.txt'
file_tr_objectives_path = data_path + 'objectives.txt'

file_en_titles_path = data_path + 'en_titles.txt'
file_en_descriptions_path = data_path + 'en_descriptions.txt'
file_en_objectives_path = data_path + 'en_objectives.txt'

tr_json = None


def lua_to_json():
    file_tr_lua = open(file=file_tr_lua_path, mode='r', encoding='UTF-8')
    file_tr_data = file_tr_lua.read().splitlines()[46:]

    file_tr_data = str(file_tr_data)\
                    .replace('=', ':')\
                    .replace('[', '')\
                    .replace(']', '')\
                    .replace(',\', \'"', ',"') \
                    .replace('\\\'', ' ')\
                    .replace('\\\\', '\\')\
                    .replace('NEW_LINE', ' NEW_LINE ')

    file_tr_data = file_tr_data[24:-8]
    file_tr_data = '{' + file_tr_data + '}'
    open(file_tr_json_path, 'w+', encoding='UTF-8').write(file_tr_data)


def load_tr_json():
    global tr_json
    with open(file_tr_json_path, encoding='UTF-8') as f:
        tr_json = json.load(f)


def split_tr_data_into_categories():
    load_tr_json()

    file_tr_title = open(file_tr_titles_path, 'a', encoding='UTF-8')
    file_tr_descriptions = open(file_tr_descriptions_path, 'a', encoding='UTF-8')
    file_tr_objectives = open(file_tr_objectives_path, 'a', encoding='UTF-8')

    for quest_id, quest in tr_json.items():
        title = quest['Title'].lstrip()
        objective = quest['Objectives'].lstrip()
        description = quest['Description'].lstrip()

        file_tr_title.write(str(quest_id) + '\t' + title + '\n')
        file_tr_descriptions.write(str(quest_id) + '\t' + description + '\n')
        file_tr_objectives.write(str(quest_id) + '\t' + objective + '\n')


def get_wowhead_data():
    load_tr_json()
    quest_ids = list(tr_json.keys())[1:]
    total_quests = len(quest_ids)
    count = 0

    file_en_title = open(file_en_titles_path, 'a', encoding='UTF-8')
    file_en_descriptions = open(file_en_descriptions_path, 'a', encoding='UTF-8')
    file_en_objectives = open(file_en_objectives_path, 'a', encoding='UTF-8')

    file_en_title.write("[\n")
    file_en_descriptions.write("[\n")
    file_en_objectives.write("[\n")

    for quest_id in quest_ids:
        title, objectives, description = get_quest_data_from_wowhead(quest_id)

        title_str = preprocess_content(title, "title", quest_id)
        description_str = preprocess_content(description, "description", quest_id)
        objectives_str = preprocess_content(objectives, "objectives", quest_id)

        count += 1
        file_en_descriptions.flush()
        if count != total_quests:
            title_str += ",\n"
            objectives_str += ",\n"
            description_str += ",\n"
        file_en_title.write(title_str)
        file_en_objectives.write(objectives_str)
        file_en_descriptions.write(description_str)

        print("Status: " + str(count) + "/" + str(total_quests))
    file_en_title.write("]")
    file_en_descriptions.write("]")
    file_en_objectives.write("]")


def preprocess_content(content, label, quest_id):
    content_pre_str = "{\"id\":" + quest_id + ", \"" +label + "\":"
    content_raw_str = repr(content.strip()).replace("\\", "").replace("\"", "\\\"")[1:-2]

    if len(content_raw_str) != 0:
        if content_raw_str[0] != '"':
            content_str = content_pre_str + "\"" + content_raw_str + "\"}"
        else:
            content_str = content_pre_str + content_raw_str
            if content_str[-1] != '"':
                content_str += "\"}"
            else:
                content_str += "}"
    else:
        content_str = content_pre_str + content_raw_str + "}"
    return content_str


def get_quest_data_from_wowhead(quest_id):
    wowhead_quest_html = requests.get(url=wowhead_quest_url % quest_id).content
    page = html.fromstring(wowhead_quest_html)
    print(quest_id)
    page_content_array = page.xpath('//div[@class="text"]/text()')
    print(page_content_array)

    descriptions_count = 0
    description = ""
    is_desc_enabled = False
    for content in page_content_array:
        if is_desc_enabled:
            descriptions_count += 1
        if content == '\r\n\r\n':
            descriptions_count += 1
            is_desc_enabled = True
        if descriptions_count == 3:
            description = content

    title = page.xpath('//div[@class="text"]/h1/text()')[0]
    objectives = page.xpath('//div[@class="text"]/text()')[3]

    if description == "":
        try:
            description1 = page.xpath('//div[@class="text"]/text()')[9]
            description2 = page.xpath('//div[@class="text"]/text()')[10]

            if len(description1) > len(description2):
                description = description1
            else:
                description = description2
        except IndexError:
            description =  page.xpath('//div[@class="text"]/text()')[4]

    return title, objectives, description

if __name__ == '__main__':
    get_wowhead_data()
    # print(get_quest_data_from_wowhead(46727))
    # print(wowhead_quest_html)
    pass
