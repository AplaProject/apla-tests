import unittest
import utils
import config
import requests
import json
import time
import funcs
import datetime


class PrototipoTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.readMainConfig()
        global url, prKey,token
        self.pages = config.readFixtures("pages")
        url = self.config["url"]
        prKey = self.config['private_key']
        self.data = utils.login(url,prKey)
        token = self.data["jwtToken"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(url,
                                self.config["time_wait_tx_in_block"],
                                result['hash'], jwtToken)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def check_page(self, sourse):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": sourse,
                "Conditions": "true", "Menu": "default_menu"}
        resp = utils.call_contract(url, prKey, "NewPage", data, token)
        self.assertTxInBlock(resp, token)
        cont = funcs.get_content(url, "page", name, "", token)
        return cont

    def findPositionElementInTree(self, contentTree, tagName):
        i = 0
        while i < len(contentTree):
            if contentTree[i]['tag'] == tagName:
                return i
            i += 1
        
    def test_page_button(self):
        contract = self.pages["button"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][0]["tag"], "button",
                         "There is no button in content" + str(content["tree"]))
        
    def test_page_selectorFromDB(self):
        contract = self.pages["selectorFromDB"]
        content = self.check_page(contract["code"])
        requiredTagNum = self.findPositionElementInTree(content["tree"],"dbfind")
        mustBe = dict(tag = "dbfind", data = True)
        page = dict(tag = content["tree"][requiredTagNum]["tag"], data = len(content["tree"][requiredTagNum]["attr"]["columns"]) > 2)
        self.assertDictEqual(mustBe, page,
                         "DBfind has problem: " + str(content["tree"]))
        
    def test_page_selectorFromData(self):
        contract = self.pages["selectorFromData"]
        content = self.check_page(contract["code"])
        mustBe = dict(tag = "data", columns = ['gender'], source = "myData",
                      select = "select", selectName = "mySelect", selectSourse = "myData")
        page = dict(tag = content["tree"][0]["tag"], columns = content["tree"][0]["attr"]["columns"],
                    source = content["tree"][0]["attr"]["source"],
                    select = content["tree"][2]["tag"], selectName = content["tree"][2]["attr"]["name"],
                    selectSourse = content["tree"][2]["attr"]["source"])
        self.assertDictEqual(mustBe, page,
                         "selectorFromData has problem: " + str(content["tree"]))
        
    def test_page_now(self):
        contract = self.pages["now"]
        content = self.check_page(contract["code"])
        today = "Today is " + str(datetime.date.today().strftime("%d.%m.%Y"))
        now = "Now: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        mustBe = dict(text1 = today, text2 = now)
        page = dict(text1 = content["tree"][0]["children"][0]["text"],
                    text2 = content["tree"][2]["children"][0]["text"])
        self.assertDictEqual(mustBe, page, "now has problem: " + str(content["tree"]))
        
    def test_page_divs(self):
        contract = self.pages["divs"]
        content = self.check_page(contract["code"])
        # outer DIV
        partContent = content['tree'][0]
        # first level inner DIV
        requiredInnerTagNum = self.findPositionElementInTree(content['tree'][0]['children'], "div")
        partContent1 = content['tree'][0]['children'][requiredInnerTagNum]
        contractContent1 = contract["content"]['children']
        # second level inner DIV
        requiredInner2TagNum = self.findPositionElementInTree(
            content['tree'][0]['children'][requiredInnerTagNum]['children'], "div")
        partContent2 = content['tree'][0]['children'][requiredInnerTagNum]['children'][requiredInner2TagNum]
        contractContent2 = contract["content"]['children']['children']
        mustBe = dict(firstDivTag=partContent['tag'],
                      firstDivClass=partContent['attr']['class'],
                      innerDivTag1=partContent1['tag'],
                      innerDivClass1=partContent1['attr']['class'],
                      innerDivTag2=partContent2['tag'],
                      innerDivClass2=partContent2['attr']['class'],
                      childrenText=partContent2['children'][0]['text'])
        page = dict(firstDivTag=contract["content"]['tag'],
                    firstDivClass=contract["content"]['attr']['class'],
                    innerDivTag1=contractContent1['tag'],
                    innerDivClass1=contractContent1['attr']['class'],
                    innerDivTag2=contractContent2['tag'],
                    innerDivClass2=contractContent2['attr']['class'],
                    childrenText=contractContent2['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "divs has problem: " + str(content["tree"]))

    def test_page_setVar(self):
        contract = self.pages["setVar"]
        content = self.check_page(contract["code"])
        requiredTagNum = self.findPositionElementInTree(content['tree'], "div")
        partContent = content['tree'][requiredTagNum]
        contractContent = contract['content']
        mustBe = dict(tag=partContent['tag'],
                    childrenText=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                    childrenText=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "setVar has problem: " + str(content["tree"]))

    def test_page_input(self):
        contract = self.pages["input"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      inputClass=partContent['attr']['class'],
                      name=partContent['attr']['name'],
                      placeholder=partContent['attr']['placeholder'],
                      type=partContent['attr']['type'])
        page = dict(tag=contractContent['tag'],
                    inputClass=contractContent['attr']['class'],
                    name=contractContent['attr']['name'],
                    placeholder=contractContent['attr']['placeholder'],
                    type=contractContent['attr']['type'])
        self.assertDictEqual(mustBe, page,
                             "input has problem: " + str(content["tree"]))
        
    def test_page_menuGroup(self):
        contract = self.pages["menuGroup"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_linkPage(self):
        contract = self.pages["linkPage"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_ecosysParam(self):
        contract = self.pages["ecosysParam"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_paragraf(self):
        contract = self.pages["paragraf"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
    
    def test_page_getVar(self):
        contract = self.pages["getVar"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_iff(self):
        contract = self.pages["iff"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_orr(self):
        contract = self.pages["orr"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_andd(self):
        contract = self.pages["andd"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_form(self):
        contract = self.pages["form"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_label(self):
        contract = self.pages["label"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_span(self):
        contract = self.pages["span"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_langRes(self):
        lang = "lang_"+utils.generate_random_name()
        data = {"Name": lang,
                "Trans": "{\"en\": \"Lang_en\", \"ru\" : \"Язык\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = utils.call_contract(url, prKey, "NewLang", data, token)
        self.assertTxInBlock(res, token)
        word = "word_" + utils.generate_random_name()
        data = {"Name": word,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = utils.call_contract(url, prKey, "NewLang", data, token)
        self.assertTxInBlock(res, token)
        contract = self.pages["langRes"]
        content = self.check_page("LangRes("+lang+") LangRes("+word+", ru)")
        
    def test_page_inputErr(self):
        contract = self.pages["inputErr"]
        content = self.check_page(contract["code"])
        # iterating response elements
        requiredTagNum = self.findPositionElementInTree(content['tree'],"inputerr")
        partContent = content['tree'][requiredTagNum]['tag']
        self.assertEqual(partContent, contract["content"]['tag'],
                         "Error in content " + str(content['tree']))
        partContent = content['tree'][requiredTagNum]['attr']
        contractContent = contract["content"]['attr']
        mustBe = dict(maxlength=partContent['maxlength'],
                      name=partContent['name'],
                      minlength=partContent['minlength'])
        page = dict(maxlength=contractContent['maxlength'],
                      name=contractContent['name'],
                      minlength=contractContent['minlength'])
        self.assertDictEqual(mustBe, page,
                             "inputErr has problem: " + str(content["tree"]))

    def test_page_include(self):
        name = "Block_"+utils.generate_random_name()
        data = {"Name": name,
                "Value": "Hello page!", "Conditions": "true"}
        res = utils.call_contract(url, prKey, "NewBlock", data, token)
        self.assertTxInBlock(res, token)
        contract = self.pages["include"]
        content = self.check_page("Include("+name+")")
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_inputImage(self):
        contract = self.pages["inputImage"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_alert(self):
        contract = self.pages["alert"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]['tag']
        self.assertEqual(partContent, contract["content"]['tag'],
                         "Error in content " + str(content['tree']))
        partContent = content['tree'][0]['attr']['alert']
        contractContent = contract["content"]['attr']['alert']
        mustBe = dict(cancelbutton = partContent['cancelbutton'],
                      confirmbutton = partContent['confirmbutton'],
                      icon = partContent['icon'],
                      text = partContent['text'])
        page = dict(cancelbutton=contractContent['cancelbutton'],
                      confirmbutton=contractContent['confirmbutton'],
                      icon=contractContent['icon'],
                      text=contractContent['text'])
        self.assertDictEqual(mustBe, page,
                             "alert has problem: " + str(content["tree"]))
        
    def test_page_table(self):
        contract = self.pages["table"]
        content = self.check_page(contract["code"])
        mustBe = dict(tag = "dbfind", source = "mysrc",
                      tag2 = "table", columns = [{'Name': 'name', 'Title': 'Name'}, {'Name': 'value', 'Title': 'Value'}, {'Name': 'conditions', 'Title': 'Conditions'}])
        page = dict(tag = content["tree"][0]["tag"], source = content["tree"][1]["attr"]["source"],
                    tag2 = content["tree"][1]["tag"],
                    columns = content["tree"][1]["attr"]["columns"])
        self.assertDictEqual(mustBe, page,
                         "selectorFromData has problem: " + str(content["tree"]))
        
    def test_page_kurs(self):
        contract = self.pages["kurs"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_strong(self):
        contract = self.pages["strong"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))

    def test_page_getColumnType(self):
        contract = self.pages["getColumnType"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"]), contract["content"],
                         "Error in content" + str(content["tree"]))
        
    def test_page_sys_var_isMobile(self):
        contract = self.pages["sys_var_isMobile"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][1]["children"][0]["text"], contract["content"],
                         "isMobile is not equal " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_page_sys_var_roleID(self):
        contract = self.pages["sys_var_roleID"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][1]["children"][0]["text"], contract["content"],
                         "role_id is not equal " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_page_sys_var_ecosystemID(self):
        contract = self.pages["sys_var_ecosystemID"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][1]["children"][0]["text"], contract["content"],
                         "ecosystem_id is not equal " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_page_sys_var_ecosystem_name(self):
        contract = self.pages["sys_var_ecosystem_name"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][1]["children"][0]["text"], contract["content"],
                         "ecosystem_name is not equal " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_page_sys_var_key_id(self):
        content = self.check_page("Span(EcosysParam(founder_account))")
        founderAcc = content["tree"][0]["children"][0]["text"]
        contract = self.pages["sys_var_keyID"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][1]["children"][0]["text"], founderAcc,
                        "key_id is not equal " + contract["content"] + ". Content = " + str(content["tree"]))
        
if __name__ == '__main__':
    unittest.main()
