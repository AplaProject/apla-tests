import unittest
import json
import os

from libs import actions, tools, db


class TestPrototipo():
    conf = tools.read_config("nodes")
    pages = tools.read_fixtures("pages")
    url = conf[0]["url"]
    pr_key = conf[0]['private_key']
    db2 = conf[0]["db"]

    @classmethod
    def setup_class(self):
        self.maxDiff = None
        self.uni = unittest.TestCase()
        data = actions.login(self.url, self.pr_key, 0)
        self.token = data["jwtToken"]

    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url,
                                   tools.read_config("test")["wait_tx_status"],
                                   result, jwt_token)
        self.uni.assertNotIn(json.dumps(status), 'errmsg')
        self.uni.assertGreater(status['blockid'], 0)

    def create_contract(self, code):
        data = {"Wallet": "", "ApplicationId": 1,
                "Value": code,
                "Conditions": "ContractConditions(\"MainCondition\")"}
        result = actions.call_contract(self.url, self.pr_key, "NewContract",
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def call_contract(self, name, data):
        result = actions.call_contract(self.url, self.pr_key, name,
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def check_page(self, sourse):
        name = "Page_" + tools.generate_random_name()
        data = {"Name": name, "Value": sourse, "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        resp = actions.call_contract(self.url, self.pr_key, "NewPage", data, self.token)
        self.assert_tx_in_block(resp, self.token)
        cont = actions.get_content(self.url, "page", name, "", 1, self.token)
        return cont

    def find_position_element_in_tree(self, content_tree, tag_name):
        i = 0
        while i < len(content_tree):
            if content_tree[i]['tag'] == tag_name:
                return i
            i += 1

    def find_position_element_in_tree_by_attribute_name_and_value(self, content_tree, tag_name, attr_name, attr_value):
        i = 0
        while i < len(content_tree):
            if content_tree[i]['tag'] == tag_name:
                if content_tree[i]['attr'][attr_name] == attr_value:
                    return i
            i += 1

    def check_post_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_post_api(end, data, self.token)
        for key in keys:
            self.uni.assertIn(key, result)
        return result

    def check_get_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_get_api(end, data, self.token)
        for key in keys:
            self.uni.assertIn(key, result)
        return result

    def test_page_button(self):
        contract = self.pages["button"]
        content = self.check_page(contract["code"])
        self.uni.assertEqual(content["tree"][0]["tag"], "button",
                         "There is no button in content" + str(content["tree"]))

    def test_page_button_composite_contract(self):
        contract = self.pages["buttonCompositeContract"]
        content = self.check_page(contract["code"])
        part_content = content["tree"]
        contract_content = contract["content"]
        must_be = dict(tag=part_content[0]["tag"],
                      compositeName=part_content[0]["attr"]["composite"][0]["name"],
                      compositeData=part_content[0]["attr"]["composite"][0]["data"][0],
                      text=part_content[0]["children"][0]["text"])
        page = dict(tag=contract_content[0]["tag"],
                    compositeName=contract_content[0]["attr"]["composite"][0]["name"],
                    compositeData=contract_content[0]["attr"]["composite"][0]["data"][0],
                    text=contract_content[0]["children"][0]["text"])
        self.uni.assertDictEqual(must_be, page, "now has problem: " + str(content["tree"]))

    def test_page_button_popup(self):
        contract = self.pages["buttonPopup"]
        content = self.check_page(contract["code"])
        part_content = content["tree"]
        contract_content = contract["content"]
        must_be = dict(tag=part_content[0]["tag"],
                      popupHeader=part_content[0]["attr"]["popup"]["header"],
                      popupWidth=part_content[0]["attr"]["popup"]["width"],
                      text=part_content[0]["children"][0]["text"])
        page = dict(tag=contract_content[0]["tag"],
                    popupHeader=contract_content[0]["attr"]["popup"]["header"],
                    popupWidth=contract_content[0]["attr"]["popup"]["width"],
                    text=contract_content[0]["children"][0]["text"])
        self.uni.assertDictEqual(must_be, page, "now has problem: " + str(content["tree"]))

    def test_page_selectorFromDB(self):
        contract = self.pages["selectorFromDB"]
        content = self.check_page(contract["code"])
        required_tag_num = self.find_position_element_in_tree(content["tree"], "dbfind")
        must_be = dict(tag="dbfind", data=True)
        page = dict(tag=content["tree"][required_tag_num]["tag"],
                    data=len(content["tree"][required_tag_num]["attr"]["columns"]) > 2)
        self.uni.assertDictEqual(must_be, page,
                                          "DBfind has problem: " + str(content["tree"]))

    def test_page_selectorFromData(self):
        contract = self.pages["selectorFromData"]
        content = self.check_page(contract["code"])
        must_be = dict(tag="data", columns=['gender'], source="myData",
                      select="select", selectName="mySelect", selectSourse="myData")
        page = dict(tag=content["tree"][0]["tag"], columns=content["tree"][0]["attr"]["columns"],
                    source=content["tree"][0]["attr"]["source"],
                    select=content["tree"][2]["tag"], selectName=content["tree"][2]["attr"]["name"],
                    selectSourse=content["tree"][2]["attr"]["source"])
        self.uni.assertDictEqual(must_be, page,
                                          "selectorFromData has problem: " + str(content["tree"]))

    def test_page_now(self):
        contract = self.pages["now"]
        content = self.check_page(contract["code"])
        contract_content = contract["content"]
        part_content = content['tree'][0]
        must_be = dict(tagOwner=contract_content["tag"],
                      tag=contract_content["children"][0]["tag"],
                      format=contract_content["children"][0]["attr"]["format"],
                      interval=contract_content["children"][0]["attr"]["interval"])
        page = dict(tagOwner=part_content["tag"],
                    tag=part_content["children"][0]["tag"],
                    format=part_content["children"][0]["attr"]["format"],
                    interval=part_content["children"][0]["attr"]["interval"])
        self.uni.assertDictEqual(must_be, page, "now has problem: " + str(content["tree"]))

    def test_page_divs(self):
        contract = self.pages["divs"]
        content = self.check_page(contract["code"])
        # outer DIV
        part_content = content['tree'][0]
        # first level inner DIV
        required_inner_tag_num = self.find_position_element_in_tree(content['tree'][0]['children'], "div")
        part_content1 = content['tree'][0]['children'][required_inner_tag_num]
        contract_content1 = contract["content"]['children']
        # second level inner DIV
        required_inner2_tag_num = self.find_position_element_in_tree(
            content['tree'][0]['children'][required_inner_tag_num]['children'], "div")
        part_content2 = content['tree'][0]['children'][required_inner_tag_num]['children'][required_inner2_tag_num]
        contract_content2 = contract["content"]['children']['children']
        must_be = dict(firstDivTag=part_content['tag'],
                      firstDivClass=part_content['attr']['class'],
                      innerDivTag1=part_content1['tag'],
                      innerDivClass1=part_content1['attr']['class'],
                      innerDivTag2=part_content2['tag'],
                      innerDivClass2=part_content2['attr']['class'],
                      childrenText=part_content2['children'][0]['text'])
        page = dict(firstDivTag=contract["content"]['tag'],
                    firstDivClass=contract["content"]['attr']['class'],
                    innerDivTag1=contract_content1['tag'],
                    innerDivClass1=contract_content1['attr']['class'],
                    innerDivTag2=contract_content2['tag'],
                    innerDivClass2=contract_content2['attr']['class'],
                    childrenText=contract_content2['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "divs has problem: " + str(content["tree"]))

    def test_page_setVar(self):
        contract = self.pages["setVar"]
        content = self.check_page(contract["code"])
        required_tag_num = self.find_position_element_in_tree(content['tree'], "div")
        part_content = content['tree'][required_tag_num]
        contract_content = contract['content']
        must_be = dict(tag=part_content['tag'],
                      childrenText=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    childrenText=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "setVar has problem: " + str(content["tree"]))

    def test_page_input(self):
        contract = self.pages["input"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      inputClass=part_content['attr']['class'],
                      name=part_content['attr']['name'],
                      placeholder=part_content['attr']['placeholder'],
                      type=part_content['attr']['type'])
        page = dict(tag=contract_content['tag'],
                    inputClass=contract_content['attr']['class'],
                    name=contract_content['attr']['name'],
                    placeholder=contract_content['attr']['placeholder'],
                    type=contract_content['attr']['type'])
        self.uni.assertDictEqual(must_be, page,
                                          "input has problem: " + str(content["tree"]))

    def test_page_menuGroup(self):
        contract = self.pages["menuGroup"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        menu_item1 = contract_content['children'][0]
        menu_item2 = contract_content['children'][1]
        required_num_menu_item1 = self.find_position_element_in_tree_by_attribute_name_and_value(part_content['children'],
                                                                                     "menuitem", "title",
                                                                                              menu_item1['attr']['title'])
        required_num_menu_item2 = self.find_position_element_in_tree_by_attribute_name_and_value(part_content['children'],
                                                                                     "menuitem", "title",
                                                                                              menu_item2['attr']['title'])
        part_content1 = part_content['children'][required_num_menu_item1]
        part_content2 = part_content['children'][required_num_menu_item2]
        must_be = dict(menuTag=part_content['tag'],
                      name=part_content['attr']['name'],
                      title=part_content['attr']['title'],
                      menuItemTag1=part_content1['tag'],
                      menuItemPage1=part_content1['attr']['page'],
                      menuItemTitle1=part_content1['attr']['title'],
                      menuItemTag2=part_content2['tag'],
                      menuItemPage2=part_content2['attr']['page'],
                      menuItemTitle2=part_content2['attr']['title'])
        page = dict(menuTag=contract_content['tag'],
                    name=contract_content['attr']['name'],
                    title=contract_content['attr']['title'],
                    menuItemTag1=part_content1['tag'],
                    menuItemPage1=menu_item1['attr']['page'],
                    menuItemTitle1=menu_item1['attr']['title'],
                    menuItemTag2=part_content2['tag'],
                    menuItemPage2=menu_item2['attr']['page'],
                    menuItemTitle2=menu_item2['attr']['title'])
        self.uni.assertDictEqual(must_be, page,
                                          "menuGroup has problem: " + str(content["tree"]))

    def test_page_linkPage(self):
        contract = self.pages["linkPage"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      linkPageClass=part_content['attr']['class'],
                      page=part_content['attr']['page'],
                      text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    linkPageClass=contract_content['attr']['class'],
                    page=contract_content['attr']['page'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "linkPage has problem: " + str(content["tree"]))

    def test_page_ecosysParam(self):
        contract = self.pages["ecosysParam"]
        content = self.check_page(contract["code"])
        part_сontent = content['tree'][0]
        contract_сontent = contract["content"]
        must_be = dict(tag=part_сontent['tag'],
                      text=part_сontent['children'][0]['text'])
        page = dict(tag=contract_сontent['tag'],
                    text=contract_сontent['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                             "ecosysParam has problem: " + str(content["tree"]))

    def test_page_paragraph(self):
        contract = self.pages["paragraph"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "paragraph has problem: " + str(content["tree"]))

    def test_page_getVar(self):
        contract = self.pages["getVar"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "getVar has problem: " + str(content["tree"]))

    def test_page_hint(self):
        page = self.pages["hint"]
        content = self.check_page(page["code"])
        part_content = content['tree'][0]
        page_content = page["content"]
        must_be = dict(tag=part_content['tag'],
                      icon=part_content['attr']['icon'],
                      title=part_content['attr']['title'],
                      text=part_content['attr']['text'])
        page = dict(tag=page_content['tag'],
                    icon=page_content['attr']['icon'],
                    title=page_content['attr']['title'],
                    text=page_content['attr']['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "getVar has problem: " + str(content["tree"]))

    def test_page_iff(self):
        contract = self.pages["iff"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "iff has problem: " + str(content["tree"]))

    def test_page_orr(self):
        contract = self.pages["orr"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "orr has problem: " + str(content["tree"]))

    def test_page_andd(self):
        contract = self.pages["andd"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "andd has problem: " + str(content["tree"]))

    def test_page_form(self):
        contract = self.pages["form"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        part_content1 = content['tree'][0]['children'][0]['children'][0]
        contract_content = contract["content"]
        contract_content1 = contract["content"]['children'][0]['children'][0]
        must_be = dict(formTag=part_content['tag'],
                      spanTag=part_content['children'][0]['tag'],
                      spanText=part_content1['text'])
        page = dict(formTag=contract_content['tag'],
                    spanTag=contract_content['children'][0]['tag'],
                    spanText=contract_content1['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "form has problem: " + str(content["tree"]))

    def test_page_label(self):
        contract = self.pages["label"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      labelFor=part_content['attr']['for'])
        page = dict(tag=contract_content['tag'],
                    labelFor=contract_content['attr']['for'])
        self.uni.assertDictEqual(must_be, page,
                                          "label has problem: " + str(content["tree"]))

    def test_page_span(self):
        contract = self.pages["span"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "span has problem: " + str(content["tree"]))

    def test_page_langRes(self):
        lang = "lang_" + tools.generate_random_name()
        data = {"Name": lang,
                "Trans": "{\"en\": \"Lang_en\", \"ru\" : \"Язык\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = actions.call_contract(self.url, self.pr_key, "NewLang", data, self.token)
        self.assert_tx_in_block(res, self.token)
        world = "world_" + tools.generate_random_name()
        data = {"Name": world,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = actions.call_contract(self.url, self.pr_key, "NewLang", data, self.token)
        self.assert_tx_in_block(res, self.token)
        contract = self.pages["langRes"]
        content = self.check_page("LangRes(" + lang + ") LangRes(" + world + ", ru)")

    def test_page_inputErr(self):
        contract = self.pages["inputErr"]
        content = self.check_page(contract["code"])
        # iterating response elements
        required_tag_num = self.find_position_element_in_tree(content['tree'], "inputerr")
        part_content = content['tree'][required_tag_num]['tag']
        self.uni.assertEqual(part_content, contract["content"]['tag'],
                         "Error in content " + str(content['tree']))
        part_content = content['tree'][required_tag_num]['attr']
        contract_content = contract["content"]['attr']
        must_be = dict(maxlength=part_content['maxlength'],
                      name=part_content['name'],
                      minlength=part_content['minlength'])
        page = dict(maxlength=contract_content['maxlength'],
                    name=contract_content['name'],
                    minlength=contract_content['minlength'])
        self.uni.assertDictEqual(must_be, page,
                                          "inputErr has problem: " + str(content["tree"]))

    def test_page_include(self):
        name = "Block_" + tools.generate_random_name()
        data = {"Name": name, "ApplicationId": 1,
                "Value": "Hello page!", "Conditions": "true"}
        res = actions.call_contract(self.url, self.pr_key, "NewBlock", data, self.token)
        self.assert_tx_in_block(res, self.token)
        contract = self.pages["include"]
        content = self.check_page("Include(" + name + ")")
        self.uni.assertEqual(content["tree"][0]["text"], contract["content"][0]["text"],
                                      "include has problem: " + str(content["tree"]))

    def test_page_inputImage(self):
        contract = self.pages["inputImage"]
        content = self.check_page(contract["code"])
        part_content = content["tree"][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content["tag"],
                      name=part_content["attr"]["name"],
                      ratio=part_content["attr"]["ratio"],
                      width=part_content["attr"]["width"])
        page = dict(tag=contract_content["tag"],
                    name=contract_content["attr"]["name"],
                    ratio=contract_content["attr"]["ratio"],
                    width=contract_content["attr"]["width"])
        self.uni.assertDictEqual(must_be, page,
                                          "inputErr has problem: " + str(content["tree"]))

    def test_page_alert(self):
        contract = self.pages["alert"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        part_content1 = content['tree'][0]['attr']['alert']
        contract_content1 = contract["content"]['attr']['alert']
        must_be = dict(tag=part_content["tag"],
                      cancelbutton=part_content1['cancelbutton'],
                      confirmbutton=part_content1['confirmbutton'],
                      icon=part_content1['icon'],
                      text=part_content1['text'])
        page = dict(tag=contract_content["tag"],
                    cancelbutton=contract_content1['cancelbutton'],
                    confirmbutton=contract_content1['confirmbutton'],
                    icon=contract_content1['icon'],
                    text=contract_content1['text'])
        self.uni.assertDictEqual(must_be, page,
                                          "alert has problem: " + str(content["tree"]))

    def test_page_table(self):
        contract = self.pages["table"]
        content = self.check_page(contract["code"])
        must_be = dict(tag="dbfind", source="mysrc",
                      tag2="table", columns=[{'Name': 'name', 'Title': 'Name'}, {'Name': 'value', 'Title': 'Value'},
                                             {'Name': 'conditions', 'Title': 'Conditions'}])
        page = dict(tag=content["tree"][0]["tag"], source=content["tree"][1]["attr"]["source"],
                    tag2=content["tree"][1]["tag"],
                    columns=content["tree"][1]["attr"]["columns"])
        self.uni.assertDictEqual(must_be, page,
                                          "selectorFromData has problem: " + str(content["tree"]))

    def test_page_kurs(self):
        contract = self.pages["kurs"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]["text"])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "kurs has problem: " + str(content["tree"]))

    def test_page_strong(self):
        contract = self.pages["strong"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]["text"])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "strong has problem: " + str(content["tree"]))

    def test_page_getColumnType(self):
        contract = self.pages["getColumnType"]
        content = self.check_page(contract["code"])
        self.uni.assertEqual(str(content["tree"][0]["text"]), contract["content"]["text"],
                                      "getColumnType has problem: " + str(content["tree"]))

    def test_page_sys_var_isMobile(self):
        contract = self.pages["sys_var_isMobile"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]["text"])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "isMobile has problem: " + str(content["tree"]))

    def test_page_sys_var_roleID(self):
        contract = self.pages["sys_var_roleID"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]["text"])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "roleID has problem: " + str(content["tree"]))

    def test_page_sys_var_ecosystemID(self):
        contract = self.pages["sys_var_ecosystemID"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"][0]
        must_be = dict(tag=part_content['tag'],
                      text=part_content['children'][0]["text"])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "ecosystemID has problem: " + str(content["tree"]))

    def test_page_sys_var_ecosystem_name(self):
        # get ecosystem name from api
        asserts = ["list"]
        res = self.check_get_api("/list/ecosystems", "", asserts)
        id = 1
        i = 0
        required_ecosys_name = ""
        while i < int(res['count']):
            if int(res['list'][i]['id']) == id:
                required_ecosys_name = res['list'][i]['name']
            i += 1
        # test
        contract = self.pages["sys_var_ecosystem_name"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        must_be = dict(tag="em",
                      text=required_ecosys_name)
        page = dict(tag=part_content['tag'],
                    text=part_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "ecosystem_name has problem: " + str(content["tree"]))

    def test_page_sys_var_key_id(self):
        content = self.check_page("Em(EcosysParam(founder_account))")
        founder_acc = content["tree"][0]["children"][0]["text"]
        contract = self.pages["sys_var_keyID"]
        content = self.check_page(contract["code"])
        key_id = content["tree"][0]["children"][0]["text"]
        self.uni.assertEqual(key_id, founder_acc,
                                      "key_id has problem: " + contract["content"] + ". Content = " + str(
                                          content["tree"]))


    def test_db_find_where_count(self):
        contract = self.pages["dbfindWhereCount"]
        content = self.check_page(contract["code"])
        required_num = self.find_position_element_in_tree(content["tree"], "em")
        page = content['tree'][required_num]["children"][0]["text"]
        self.uni.assertEqual(contract["content"], page,
                                      "dbfind_where_count has problem: " + contract["content"] + ". Content = " + str(
                                          content["tree"]))

    def test_db_find_where_id_count(self):
        contract = self.pages["dbfindWhereIdCount"]
        content = self.check_page(contract["code"])
        required_num = self.find_position_element_in_tree(content["tree"], "em")
        page = content['tree'][required_num]["children"][0]["text"]
        self.uni.assertEqual(contract["content"], page,
                                      "dbfind_whereId_count has problem: " + contract["content"] + ". Content = " + str(
                                          content["tree"]))

    def test_binary(self):
        # this test has not fixture
        name = "image_" + tools.generate_random_name()
        app_id = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {"Name": name, "ApplicationId": app_id, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        member_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        last_rec = actions.get_count(self.url, "binaries", self.token)
        content = self.check_page("Binary(Name: " + name + ", AppID: " + app_id +\
                                  ", MemberID: " + member_id + ")")
        msg = "test_binary has problem. Content = " + str(content["tree"])
        file_hash = "122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05"
        self.uni.assertEqual("/data/1_binaries/"+last_rec+"/data/" + file_hash,
                             content["tree"][0]["text"])

    def test_binary_by_id(self):
        # this test has not fixture
        name = "image_" + tools.generate_random_name()
        app_id = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": app_id, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        # test
        last_rec = actions.get_count(self.url, "binaries", self.token)
        content = self.check_page("Binary().ById(" + last_rec + ")")
        msg = "test_binary has problem. Content = " + str(content["tree"])
        file_hash = "122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05"
        self.uni.assertEqual("/data/1_binaries/" + last_rec + "/data/" + file_hash,
                         content["tree"][0]["text"])

    def test_image_binary(self):
        # this test has not fixture
        name = "image_" + tools.generate_random_name()
        app_id = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {"Name": name, "ApplicationId": app_id, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        member_id = actions.get_parameter_value(self.url, 'founder_account', self.token)
        last_rec = actions.get_count(self.url, "binaries", self.token)
        content = self.check_page("Image(Binary(Name: " + name + ", AppID: " + app_id +\
                                  ", MemberID: " + member_id + "))")
        part_content = content["tree"][0]
        file_hash = "122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05"
        must_be = dict(tag=part_content['tag'],
                      src=part_content['attr']["src"])
        page = dict(tag="image",
                    src="/data/1_binaries/" + last_rec + "/data/" + file_hash)
        self.uni.assertDictEqual(must_be, page,
                             "test_image_binary has problem: " + str(content["tree"]))
        
    def test_image_binary_by_id(self):
        # this test has not fixture
        name = "image_" + tools.generate_random_name()
        app_id = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        data = {"Name": name, "ApplicationId": app_id, 'Data': file}
        resp = actions.call_contract(self.url, self.pr_key, "UploadBinary", data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        last_rec = actions.get_count(self.url, "binaries", self.token)
        content = self.check_page("Image(Binary().ById(" + last_rec + "))")
        part_сontent = content["tree"][0]
        file_hash = "122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05"
        must_be = dict(tag = part_сontent['tag'],
                      src = part_сontent['attr']["src"])
        page = dict(tag = "image",
                    src = "/data/1_binaries/" + last_rec + "/data/" + file_hash)
        self.uni.assertDictEqual(must_be, page,
                             "test_image_binary_by_id has problem: " + str(content["tree"]))
    def test_address(self):
        contract = self.pages["address"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tagOwner = contract_content['tag'],
                      tag = contract_content['children'][0]["tag"],
                      text = contract_content['children'][0]["text"])
        page = dict(tagOwner = part_content['tag'],
                    tag = part_content['children'][0]["tag"],
                    text = part_content['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "address has problem: " + str(content["tree"]))

    def test_money(self):
        contract = self.pages["money"]
        content1 = self.check_page(contract["code1"])
        content2 = self.check_page(contract["code2"])
        part_content1 = content1['tree'][0]
        part_content2 = content2['tree'][0]
        contract_content1 = contract["content1"]
        contract_content2 = contract["content2"]
        must_be = dict(tagOwner1 = contract_content1['tag'],
                      tag1 = contract_content1['children'][0]["tag"],
                      text1 = contract_content1['children'][0]["text"],
                      tagOwner2 = contract_content2['tag'],
                      tag2 = contract_content2['children'][0]["tag"],
                      text2 = contract_content2['children'][0]["text"])
        page = dict(tagOwner1 = part_content1['tag'],
                    tag1 = part_content1['children'][0]["tag"],
                    text1 = part_content1['children'][0]["text"],
                    tagOwner2 = part_content2['tag'],
                    tag2 = part_content2['children'][0]["tag"],
                    text2=part_content2['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page,
                                          "money has problem: " + "\n" + str(content1["tree"]) + "\n" + str(
                                              content2["tree"]))

    def test_calculate(self):
        contract = self.pages["calculate"]
        # Set for type of money
        money_content1 = self.check_page(contract["moneyCode1"])
        part_money_content1 = money_content1['tree'][0]
        contract_money_content1 = contract["moneyContent1"]
        money_content2 = self.check_page(contract["moneyCode2"])
        part_money_content2 = money_content2['tree'][0]
        contract_money_content2 = contract["moneyContent2"]
        money_content3 = self.check_page(contract["moneyCode3"])
        part_money_content3 = money_content3['tree'][0]
        contract_money_content3 = contract["moneyContent3"]
        money_content4 = self.check_page(contract["moneyCode4"])
        part_money_content4 = money_content4['tree'][0]
        contract_money_content4 = contract["moneyContent4"]
        money_content5 = self.check_page(contract["moneyCode5"])
        part_money_content5 = money_content5['tree'][0]
        contract_money_content5 = contract["moneyContent5"]
        money_content6 = self.check_page(contract["moneyCode6"])
        part_money_content6 = money_content6['tree'][0]
        contract_money_content6 = contract["moneyContent6"]
        moneyContent7 = self.check_page(contract["moneyCode7"])
        partMoneyContent7 = moneyContent7['tree'][0]
        contractMoneyContent7 = contract["moneyContent7"]
        moneyContent8 = self.check_page(contract["moneyCode8"])
        partMoneyContent8 = moneyContent8['tree'][0]
        contractMoneyContent8 = contract["moneyContent8"]
        moneyContent9 = self.check_page(contract["moneyCode9"])
        partMoneyContent9 = moneyContent9['tree'][0]
        contractMoneyContent9 = contract["moneyContent9"]
        moneyContent10 = self.check_page(contract["moneyCode10"])
        partMoneyContent10 = moneyContent10['tree'][0]
        contractMoneyContent10 = contract["moneyContent10"]
        moneyContent11 = self.check_page(contract["moneyCode11"])
        partMoneyContent11 = moneyContent11['tree'][0]
        contractMoneyContent11 = contract["moneyContent11"]
        moneyContent12 = self.check_page(contract["moneyCode12"])
        partMoneyContent12 = moneyContent12['tree'][0]
        contractMoneyContent12 = contract["moneyContent12"]
        moneyContent13 = self.check_page(contract["moneyCode13"])
        partMoneyContent13 = moneyContent13['tree'][0]
        contractMoneyContent13 = contract["moneyContent13"]
        moneyContent14 = self.check_page(contract["moneyCode14"])
        partMoneyContent14 = moneyContent14['tree'][0]
        contractMoneyContent14 = contract["moneyContent14"]
        moneyContent15 = self.check_page(contract["moneyCode15"])
        partMoneyContent15 = moneyContent15['tree'][0]
        contractMoneyContent15 = contract["moneyContent15"]
        # Set for type of money
        floatContent1 = self.check_page(contract["floatCode1"])
        partFloatContent1 = floatContent1['tree'][0]
        contractFloatContent1 = contract["floatContent1"]
        floatContent2 = self.check_page(contract["floatCode2"])
        partFloatContent2 = floatContent2['tree'][0]
        contractFloatContent2 = contract["floatContent2"]
        floatContent3 = self.check_page(contract["floatCode3"])
        partFloatContent3 = floatContent3['tree'][0]
        contractFloatContent3 = contract["floatContent3"]
        floatContent4 = self.check_page(contract["floatCode4"])
        partFloatContent4 = floatContent4['tree'][0]
        contractFloatContent4 = contract["floatContent4"]
        floatContent5 = self.check_page(contract["floatCode5"])
        partFloatContent5 = floatContent5['tree'][0]
        contractFloatContent5 = contract["floatContent5"]
        floatContent6 = self.check_page(contract["floatCode6"])
        partFloatContent6 = floatContent6['tree'][0]
        contractFloatContent6 = contract["floatContent6"]
        floatContent7 = self.check_page(contract["floatCode7"])
        partFloatContent7 = floatContent7['tree'][0]
        contractFloatContent7 = contract["floatContent7"]
        floatContent8 = self.check_page(contract["floatCode8"])
        partFloatContent8 = floatContent8['tree'][0]
        contractFloatContent8 = contract["floatContent8"]
        floatContent9 = self.check_page(contract["floatCode9"])
        partFloatContent9 = floatContent9['tree'][0]
        contractFloatContent9 = contract["floatContent9"]
        floatContent10 = self.check_page(contract["floatCode10"])
        partFloatContent10 = floatContent10['tree'][0]
        contractFloatContent10 = contract["floatContent10"]
        floatContent11 = self.check_page(contract["floatCode11"])
        partFloatContent11 = floatContent11['tree'][0]
        contractFloatContent11 = contract["floatContent11"]
        floatContent12 = self.check_page(contract["floatCode12"])
        partFloatContent12 = floatContent12['tree'][0]
        contractFloatContent12 = contract["floatContent12"]
        floatContent13 = self.check_page(contract["floatCode13"])
        partFloatContent13 = floatContent13['tree'][0]
        contractFloatContent13 = contract["floatContent13"]
        floatContent14 = self.check_page(contract["floatCode14"])
        partFloatContent14 = floatContent14['tree'][0]
        contractFloatContent14 = contract["floatContent14"]
        floatContent15 = self.check_page(contract["floatCode15"])
        partFloatContent15 = floatContent15['tree'][0]
        contractFloatContent15 = contract["floatContent15"]
        # Set for type of int
        intContent1 = self.check_page(contract["intCode1"])
        partIntContent1 = intContent1['tree'][0]
        contractIntContent1 = contract["intContent1"]
        intContent2 = self.check_page(contract["intCode2"])
        partIntContent2 = intContent2['tree'][0]
        contractIntContent2 = contract["intContent2"]
        intContent3 = self.check_page(contract["intCode3"])
        partIntContent3 = intContent3['tree'][0]
        contractIntContent3 = contract["intContent3"]
        intContent4 = self.check_page(contract["intCode4"])
        partIntContent4 = intContent4['tree'][0]
        contractIntContent4 = contract["intContent4"]
        intContent5 = self.check_page(contract["intCode5"])
        partIntContent5 = intContent5['tree'][0]
        contractIntContent5 = contract["intContent5"]
        intContent6 = self.check_page(contract["intCode6"])
        partIntContent6 = intContent6['tree'][0]
        contractIntContent6 = contract["intContent6"]
        # Set wrong type
        wrongContent1 = self.check_page(contract["wrongCode1"])
        partWrongContent1 = wrongContent1['tree'][0]
        contractWrongContent1 = contract["wrongContent1"]
        must_be = dict(money1 = contract_money_content1['children'][0]["text"],
                      money2 = contract_money_content2['children'][0]["text"],
                      money3 = contract_money_content3['children'][0]["text"],
                      money4 = contract_money_content4['children'][0]["text"],
                      money5 = contract_money_content5['children'][0]["text"],
                      money6 = contract_money_content6['children'][0]["text"],
                      money7 = contractMoneyContent7['children'][0]["text"],
                      money8 = contractMoneyContent8['children'][0]["text"],
                      money9 = contractMoneyContent9['children'][0]["text"],
                      money10 = contractMoneyContent10['children'][0]["text"],
                      money11 = contractMoneyContent11['children'][0]["text"],
                      money12 = contractMoneyContent12['children'][0]["text"],
                      money13 = contractMoneyContent13['children'][0]["text"],
                      money14 = contractMoneyContent14['children'][0]["text"],
                      money15 = contractMoneyContent15['children'][0]["text"],
                      float1 = contractFloatContent1['children'][0]["text"],
                      float2 = contractFloatContent2['children'][0]["text"],
                      float3 = contractFloatContent3['children'][0]["text"],
                      float4 = contractFloatContent4['children'][0]["text"],
                      float5 = contractFloatContent5['children'][0]["text"],
                      float6 = contractFloatContent6['children'][0]["text"],
                      float7 = contractFloatContent7['children'][0]["text"],
                      float8 = contractFloatContent8['children'][0]["text"],
                      float9 = contractFloatContent9['children'][0]["text"],
                      float10 = contractFloatContent10['children'][0]["text"],
                      float11 = contractFloatContent11['children'][0]["text"],
                      float12 = contractFloatContent12['children'][0]["text"],
                      float13 = contractFloatContent13['children'][0]["text"],
                      float14 = contractFloatContent14['children'][0]["text"],
                      float15 = contractFloatContent15['children'][0]["text"],
                      int1 = contractIntContent1['children'][0]["text"],
                      int2 = contractIntContent2['children'][0]["text"],
                      int3 = contractIntContent3['children'][0]["text"],
                      int4 = contractIntContent4['children'][0]["text"],
                      int5 = contractIntContent5['children'][0]["text"],
                      int6 = contractIntContent6['children'][0]["text"],
                      wrong1 = contractWrongContent1['children'][0]["text"])
        page = dict(money1 = part_money_content1['children'][0]["text"],
                    money2 = part_money_content2['children'][0]["text"],
                    money3 = part_money_content3['children'][0]["text"],
                    money4 = part_money_content4['children'][0]["text"],
                    money5 = part_money_content5['children'][0]["text"],
                    money6 = part_money_content6['children'][0]["text"],
                    money7 = partMoneyContent7['children'][0]["text"],
                    money8 = partMoneyContent8['children'][0]["text"],
                    money9 = partMoneyContent9['children'][0]["text"],
                    money10 = partMoneyContent10['children'][0]["text"],
                    money11 = partMoneyContent11['children'][0]["text"],
                    money12 = partMoneyContent12['children'][0]["text"],
                    money13 = partMoneyContent13['children'][0]["text"],
                    money14 = partMoneyContent14['children'][0]["text"],
                    money15 = partMoneyContent15['children'][0]["text"],
                    float1 = partFloatContent1['children'][0]["text"],
                    float2 = partFloatContent2['children'][0]["text"],
                    float3 = partFloatContent3['children'][0]["text"],
                    float4 = partFloatContent4['children'][0]["text"],
                    float5 = partFloatContent5['children'][0]["text"],
                    float6 = partFloatContent6['children'][0]["text"],
                    float7 = partFloatContent7['children'][0]["text"],
                    float8 = partFloatContent8['children'][0]["text"],
                    float9 = partFloatContent9['children'][0]["text"],
                    float10 = partFloatContent10['children'][0]["text"],
                    float11 = partFloatContent11['children'][0]["text"],
                    float12 = partFloatContent12['children'][0]["text"],
                    float13 = partFloatContent13['children'][0]["text"],
                    float14 = partFloatContent14['children'][0]["text"],
                    float15 = partFloatContent15['children'][0]["text"],
                    int1 = partIntContent1['children'][0]["text"],
                    int2 = partIntContent2['children'][0]["text"],
                    int3 = partIntContent3['children'][0]["text"],
                    int4 = partIntContent4['children'][0]["text"],
                    int5 = partIntContent5['children'][0]["text"],
                    int6 = partIntContent6['children'][0]["text"],
                    wrong1 = partWrongContent1['children'][0]["text"])
        self.uni.assertDictEqual(must_be, page, "calculate has problem!")

    def test_arrayToSource(self):
        contract = self.pages["arrayToSource"]
        content = self.check_page(contract["code"])
        part_content = content['tree'][0]
        contract_content = contract["content"]
        must_be = dict(tag = part_content["tag"],
                      data1 = part_content["attr"]["data"][0],
                      data2 = part_content["attr"]["data"][1],
                      data3 = part_content["attr"]["data"][2],
                      source = part_content["attr"]["source"])
        page = dict(tag = contract_content["tag"],
                    data1 = contract_content["attr"]["data"][0],
                    data2 = contract_content["attr"]["data"][1],
                    data3 = contract_content["attr"]["data"][2],
                    source = contract_content["attr"]["source"])
        self.uni.assertDictEqual(must_be, page,
                                          "arrayToSource has problem: " + "\n" + str(content["tree"]))

    def test_getHistoryContract(self):
        # it test has not fixture
        # create contract
        replaced_string = "variable_for_replace"
        code = """
                { 
                    data{}
                    conditions{}
                    action{ var %s int }
                }
                """ % replaced_string
        code, name = tools.generate_name_and_code(code)
        self.create_contract(code)
        # change contract
        id = actions.get_object_id(self.url, name, "contracts", self.token)
        new_code = code.replace(replaced_string, "new_var")
        data = {"Id": id, "Value": new_code}
        self.call_contract("EditContract", data)
        # test
        content = self.check_page("GetHistory(src, contracts, " + str(id) + ")")
        part_content = content['tree'][0]["attr"]["data"][0]
        self.uni.assertIn(replaced_string, str(part_content),
                          "getHistoryContract has problem: " + str(content["tree"]))